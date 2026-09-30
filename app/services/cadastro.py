# Arquivo criado por Victor
"""Regras de criação das contas de paciente e de profissional de saúde."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ErroNegocio
from app.core.security import gerar_hash_senha
from app.models.endereco import Endereco
from app.models.info_conselho import InfoConselho
from app.models.paciente import Paciente
from app.models.profissional import Profissional
from app.models.profissional_especialidade import ProfissionalEspecialidade
from app.models.usuario import Usuario
from app.repositories.conselho import RepositorioConselho
from app.repositories.especialidade import RepositorioEspecialidade
from app.repositories.usuario import RepositorioUsuario
from app.schemas.cadastro import CadastroProfissionalEntrada, CadastroUsuarioEntrada


class ServicoCadastro:
    """Cria paciente e profissional de saúde a partir de dados que o schema já validou.

    As contas de paciente nascem ativas. O profissional de saúde fica inativo
    até o administrador validar o cadastro. Administrador não é criado aqui:
    essa conta é inserida direto no banco.
    """

    # Construindo o serviço de cadastro - Criando uma instância do serviço de cadastro e passando a sessão do banco de dados.
    def __init__(self, db: Session) -> None:
        """Guarda a sessão do banco e os repositórios que usam essa mesma sessão.

        Passo a passo:
        1. Recebe a sessão aberta pela dependência get_db da requisição.
        2. Cria os repositórios de usuário, especialidade e conselho com ela.
        3. Assim, tudo que este serviço gravar entra na mesma transação.
        """
        # self é o próprio objeto que está sendo criado.
        self.db = db

        # Criando os repositórios de usuário, especialidade e conselho com a sessão do banco de dados.
        self.usuarios = RepositorioUsuario(db)
        self.especialidades = RepositorioEspecialidade(db)
        self.conselhos = RepositorioConselho(db)

    # Cria uma conta de paciente a partir de dados válidos.
    def cadastrar_paciente(self, dados: CadastroUsuarioEntrada) -> Usuario:
        """Cria um paciente com conta ativa (RF1).

        Passo a passo:
        1. Monta o usuário e o endereço com status verdadeiro.
        2. Liga uma linha da tabela paciente a esse usuário.
        3. Grava tudo e devolve o usuário já com o id gerado.
        """
        # Chama outra função da própria classe para criar o usuário.
        usuario = self._criar_usuario(dados, status=True)
        # Cria uma linha na tabela paciente e liga ao usuário.
        usuario.paciente = Paciente()
        # Salva tudo no banco (commit) e devolve o usuário já com o id gerado
        return self._concluir(usuario)

    def cadastrar_profissional(self, dados: CadastroProfissionalEntrada) -> Usuario:
        """Cria um profissional de saúde inativo, até o administrador validar.

        Passo a passo:
        1. Recusa se o par número + órgão do conselho já existir.
        2. Monta o usuário com status falso. O login só passa depois da validação.
        3. Grava o conselho e o perfil profissional.
        4. Para cada especialidade, reaproveita a que já existe ou cria outra.
        5. Liga profissional, especialidade e conselho na tabela de vínculo.
        6. Confirma a transação.
        """
        # Verifica se o número e o órgão do conselho já existem.
        if self.conselhos.buscar(dados.numero_conselho, dados.orgao_conselho) is not None:
            raise ErroNegocio(
                "Já existe um profissional com este número de conselho. Verifique os dados ou faça login.",
                409,
            )
        # Chama outra função da própria classe para criar o usuário.
        usuario = self._criar_usuario(dados, status=False)
        # Cria uma linha na tabela info_conselho e liga ao usuário.
        conselho = InfoConselho(
            numero_conselho=dados.numero_conselho,
            orgao_conselho=dados.orgao_conselho,
        )
        # Cria um Profissional (a linha que faz esse usuário "ser" um profissional) com as infos profissionais.
        profissional = Profissional(info_profissional=dados.info_profissional)
        # Liga o profissional ao usuário.
        usuario.profissional = profissional

        # Salva o conselho no banco de dados.
        self.db.add(conselho) # coloca o conselho na fila pra ser salvo
        self.db.flush() # manda pro banco , mas sem confirmar a transação. Não posso commitar ainda, porque o profissional ainda não foi criado.

        # Loop para ligar cada especialidade ao profissional.
        for nome in dados.especialidades:
            especialidade = self.especialidades.obter_ou_criar(nome)
            profissional.vinculos.append(
                ProfissionalEspecialidade(
                    id_especialidade=especialidade.id_especialidade,
                    id_conselho=conselho.id_conselho,
                )
            )
        # Salva tudo no banco (commit) e devolve o usuário já com o id gerado
        return self._concluir(usuario)


    # Cria um usuário a partir de dados válidos.
    def _criar_usuario(self, dados: CadastroUsuarioEntrada, status: bool) -> Usuario:
        """Monta usuário e endereço ainda sem confirmar a transação.

        Passo a passo:
        1. Garante que CPF e e-mail ainda não existem (RN1).
        2. Cria o usuário com a senha já transformada em hash Argon2.
        3. Anexa o endereço na relação 1 para 1.
        4. Coloca o usuário na sessão e devolve, sem dar commit.
        O commit fica em _concluir, depois que o perfil paciente ou
        profissional também estiver ligado.
        """

        # Utiliza uma função da própria classe para garantir que o CPF e o e-mail ainda não existem
        self._garantir_unicidade(dados.cpf, dados.email)

        # Cria o usuário com a senha já transformada em hash Argon2.
        usuario = Usuario(
            nome=dados.nome,
            cpf=dados.cpf,
            orgao_emissor=dados.orgao_emissor,
            data_nascimento=dados.data_nascimento,
            genero=dados.genero,
            telefone=dados.telefone,
            email=dados.email,
            senha_hash=gerar_hash_senha(dados.senha),
            status=status,
            consentimento_lgpd=True,
        )
        # Cria o endereço e liga ao usuário.
        usuario.endereco = Endereco(
            cep=dados.cep,
            endereco=dados.endereco,
        )
        # Coloca o usuário na fila pra ser salvo.
        self.usuarios.adicionar(usuario)
        # Devolve o usuário já com o id gerado
        return usuario


    # Garante que o CPF e o e-mail ainda não existem.
    def _garantir_unicidade(self, cpf: str, email: str) -> None:
        """Impede dois cadastros com o mesmo CPF ou o mesmo e-mail (RN1).

        Passo a passo:
        1. Busca o CPF. Se achar, interrompe com 409 e pede para fazer login.
        2. Busca o e-mail. Se achar, interrompe do mesmo jeito.
        3. Se nenhum existir, a função termina e o cadastro continua.
        A mensagem cita qual campo repetiu para a pessoa corrigir o formulário (RNF3).
        """
        # Usa o repositório de usuários para buscar o CPF e o e-mail.
        if self.usuarios.buscar_por_cpf(cpf) is not None:
            raise ErroNegocio(
                "Já existe um cadastro com este CPF. Faça login ou utilize outro CPF.",
                409,
            )
        # Usa o repositório de usuários para buscar o e-mail.
        if self.usuarios.buscar_por_email(email) is not None:
            raise ErroNegocio(
                "Já existe um cadastro com este e-mail. Faça login ou utilize outro e-mail.",
                409,
            )

    # Finaliza o cadastro.
    def _concluir(self, usuario: Usuario) -> Usuario:
        """Confirma no banco o usuário, o endereço e o perfil.

        Passo a passo:
        1. Pede commit da sessão.
        2. Se o banco recusar por chave única (duas requisições ao mesmo tempo),
           desfaz a transação e devolve 409.
        3. Se o commit passar, devolve o usuário com os ids preenchidos.
        """
        
        # Tenta confirmar a transação.
        try:
            self.db.commit()
        except IntegrityError:
            # Se a transação falhar, desfaz a transação e devolve 409.
            self.db.rollback()
            raise ErroNegocio(
                "Já existe um cadastro com estes dados. Verifique CPF, e-mail ou conselho e tente novamente.", # Mensagem de erro
                409, # Código de erro
            ) from None # from None é para evitar que o erro seja propagado para o usuário.

        # Se a transação for confirmada, devolve o usuário com os ids preenchidos.
        return usuario