"""Regras de criação das contas de paciente e de profissional de saúde."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.excecoes import ErroNegocio
from core.seguranca import gerar_hash_senha
from models.acesso import Credencial
from models.models import (
    Endereco,
    InfoConselho,
    Paciente,
    Profissional,
    ProfissionalEspecialidade,
    Usuario,
)
from repositories.conselho import RepositorioConselho
from repositories.credencial import RepositorioCredencial
from repositories.especialidade import RepositorioEspecialidade
from repositories.usuario import RepositorioUsuario
from schemas.cadastro import CadastroProfissionalEntrada, CadastroUsuarioEntrada


class ServicoCadastro:
    """Cria paciente e profissional usando as tabelas que o grupo já definiu.

    A senha não entra em usuario: ela vai para a tabela credencial.
    O paciente nasce ativo. O profissional fica inativo até o administrador validar.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.usuarios = RepositorioUsuario(db)
        self.credenciais = RepositorioCredencial(db)
        self.especialidades = RepositorioEspecialidade(db)
        self.conselhos = RepositorioConselho(db)

    def cadastrar_paciente(self, dados: CadastroUsuarioEntrada) -> Usuario:
        usuario = self._criar_usuario(dados, status=True)
        usuario.paciente = Paciente()
        return self._concluir(usuario)

    def cadastrar_profissional(self, dados: CadastroProfissionalEntrada) -> Usuario:
        if self.conselhos.buscar(dados.numero_conselho, dados.orgao_conselho) is not None:
            raise ErroNegocio(
                "Já existe um profissional com este número de conselho. Verifique os dados ou faça login.",
                409,
            )
        usuario = self._criar_usuario(dados, status=False)
        conselho = InfoConselho(
            numero_conselho=dados.numero_conselho,
            orgao_conselho=dados.orgao_conselho,
        )
        profissional = Profissional(info_profissional=dados.info_profissional)
        usuario.profissional = profissional
        self.db.add(conselho)
        self.db.flush()
        for nome in dados.especialidades:
            especialidade = self.especialidades.obter_ou_criar(nome)
            profissional.especialidades.append(
                ProfissionalEspecialidade(
                    id_especialidade=especialidade.id_especialidade,
                    id_conselho=conselho.id_conselho,
                    valor_consulta=0.0,
                )
            )
        return self._concluir(usuario)

    def _criar_usuario(self, dados: CadastroUsuarioEntrada, status: bool) -> Usuario:
        self._garantir_unicidade(dados.cpf, dados.email)
        usuario = Usuario(
            nome=dados.nome,
            cpf=dados.cpf,
            orgao_emissor=dados.orgao_emissor,
            data_nascimento=dados.data_nascimento,
            genero=dados.genero,
            telefone=dados.telefone,
            email=dados.email,
            status=status,
        )
        usuario.endereco = Endereco(
            cep=dados.cep,
            cidade=dados.cidade,
            logradouro=dados.logradouro,
            numero=dados.numero,
            bairro=dados.bairro,
            complemento=dados.complemento,
        )
        self.usuarios.adicionar(usuario)
        self.db.flush()
        self.credenciais.adicionar(
            Credencial(
                id_usuario=usuario.id,
                senha_hash=gerar_hash_senha(dados.senha),
                consentimento_lgpd=True,
                tentativas_login_falhas=0,
            )
        )
        return usuario

    def _garantir_unicidade(self, cpf: str, email: str) -> None:
        if self.usuarios.buscar_por_cpf(cpf) is not None:
            raise ErroNegocio(
                "Já existe um cadastro com este CPF. Faça login ou utilize outro CPF.",
                409,
            )
        if self.usuarios.buscar_por_email(email) is not None:
            raise ErroNegocio(
                "Já existe um cadastro com este e-mail. Faça login ou utilize outro e-mail.",
                409,
            )

    def _concluir(self, usuario: Usuario) -> Usuario:
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ErroNegocio(
                "Já existe um cadastro com estes dados. Verifique CPF, e-mail ou conselho e tente novamente.",
                409,
            ) from None
        return usuario
