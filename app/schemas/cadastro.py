# Arquivo criado por Victor
from datetime import date

from pydantic import Field, field_validator

# Importação dos validadores comuns.
from app.core.validators import (
    normalizar_cep,
    normalizar_cpf,
    normalizar_email,
    normalizar_nome,
    normalizar_telefone,
    texto_obrigatorio,
    validar_data_nascimento,
    validar_senha,
)
# Importação do esquema comum.
from app.schemas.comum import Esquema

# Classe para representar os dados comuns do cadastro de paciente e de administrador (RF1).
class CadastroUsuarioEntrada(Esquema):
    """Dados comuns do cadastro de paciente e de administrador (RF1)."""

    nome: str = Field(description="Nome completo.", examples=["Maria da Silva"])
    cpf: str = Field(description="CPF do usuário.", examples=["529.982.247-25"])
    orgao_emissor: str = Field(description="Órgão emissor do documento.", examples=["SSP/PI"])
    data_nascimento: date = Field(description="Data de nascimento.", examples=["1998-05-20"])
    genero: str = Field(description="Gênero, como no modelo de dados.", examples=["feminino"])
    telefone: str = Field(description="Telefone com DDD.", examples=["86988887777"])
    email: str = Field(description="E-mail único na plataforma.", examples=["maria@example.com"])
    senha: str = Field(description="Senha com no mínimo 8 caracteres.", examples=["Senha123"])
    consentimento_lgpd: bool = Field(
        description="Autorização para guardar os dados pessoais. Precisa ser verdadeiro.",
    )
    cep: str = Field(description="CEP com 8 dígitos. Pode ser enviado com ou sem hífen.", examples=["64000-000"])
    endereco: str = Field(
        description="Endereço completo.",
        examples=["Rua das Laranjeiras, 100, Teresina"],
    )

    # Validador para o nome.
    @field_validator("nome")
    # Método para validar o nome.
    @classmethod
    def validar_nome(cls, valor: str) -> str:
        """Roda antes de aceitar o JSON. Delega a limpeza e a regra do nome completo."""
        return normalizar_nome(valor)

    # Validador para o CPF.
    @field_validator("cpf")
    # Método para validar o CPF.
    @classmethod
    def validar_cpf(cls, valor: str) -> str:
        """Confere o CPF e troca a máscara pelos 11 dígitos que serão gravados."""
        return normalizar_cpf(valor)


    # Validador para o órgão emissor.
    @field_validator("orgao_emissor")
    # Método para validar o órgão emissor.
    @classmethod
    def validar_orgao(cls, valor: str) -> str:
        """Exige o órgão emissor e limita a 40 caracteres, tamanho da coluna."""
        return texto_obrigatorio(valor, "órgão emissor", 40)


    # Validador para a data de nascimento.
    @field_validator("data_nascimento")
    # Método para validar a data de nascimento.
    @classmethod
    def validar_nascimento(cls, valor: date) -> date:
        """Recusa nascimento futuro. O formato AAAA-MM-DD já foi lido pelo Pydantic."""
        return validar_data_nascimento(valor)


    # Validador para o gênero.
    @field_validator("genero")
    # Método para validar o gênero.
    @classmethod
    def validar_genero(cls, valor: str) -> str:
        """Exige o gênero. O relatório não lista valores fechados, então o texto é livre até 30 caracteres."""
        return texto_obrigatorio(valor, "gênero", 30)


    # Validador para o telefone.
    @field_validator("telefone")
    # Método para validar o telefone.
    @classmethod
    def validar_telefone(cls, valor: str) -> str:
        """Confere DDD + número e guarda só os dígitos."""
        return normalizar_telefone(valor)


    # Validador para o e-mail.
    @field_validator("email")
    # Método para validar o e-mail.
    @classmethod
    def validar_email(cls, valor: str) -> str:
        """Confere o formato e guarda o e-mail em minúsculas."""
        return normalizar_email(valor)


    # Validador para a senha.
    @field_validator("senha")
    # Método para validar a senha.
    @classmethod
    def validar_senha_cadastro(cls, valor: str) -> str:
        """Exige o tamanho mínimo. O hash Argon2 é calculado depois, no service."""
        return validar_senha(valor)

    # Validador para o consentimento LGPD.
    @field_validator("consentimento_lgpd")
    # Método para validar o consentimento LGPD.
    @classmethod
    def validar_consentimento(cls, valor: bool) -> bool:
        """Exige consentimento verdadeiro antes de gravar dados pessoais (RNF25).

        Passo a passo:
        1. Se o JSON vier com false, interrompe o cadastro.
        2. Se vier true, segue. O service grava consentimento_lgpd como verdadeiro.
        """
        if valor is not True:
            raise ValueError(
                "É necessário autorizar o tratamento dos dados pessoais para concluir o cadastro. "
                "Confirme o consentimento e tente novamente."
            )
        return valor

    # Validador para o CEP.
    @field_validator("cep")
    # Método para validar o CEP.
    @classmethod
    def validar_cep(cls, valor: str) -> str:
        """Confere o CEP e guarda os 8 dígitos."""
        return normalizar_cep(valor)

    # Validador para o endereço.
    @field_validator("endereco")
    # Método para validar o endereço.
    @classmethod
    def validar_endereco(cls, valor: str) -> str:
        """Exige o endereço em um único texto, com no máximo 200 caracteres."""
        return texto_obrigatorio(valor, "endereço", 200)


# Classe para representar os dados comuns do cadastro de profissional de saúde (RF20 e RN15).
class CadastroProfissionalEntrada(CadastroUsuarioEntrada):
    """Cadastro do profissional de saúde (RF20 e RN15)."""

    numero_conselho: str = Field(description="Número de registro no conselho de classe.", examples=["123456"])
    orgao_conselho: str = Field(description="Sigla do conselho. Exemplo: CRM.", examples=["CRM"])
    info_profissional: str = Field(
        description="Informações profissionais exibidas ao paciente.",
        examples=["Clínico geral com atuação em telemedicina."],
    )
    especialidades: list[str] = Field(
        description="Ao menos uma especialidade (RN15).",
        min_length=1,
        examples=[["Clínica médica"]],
    )

    @field_validator("numero_conselho")
    @classmethod
    def validar_numero_conselho(cls, valor: str) -> str:
        return texto_obrigatorio(valor, "número do conselho", 30)

    @field_validator("orgao_conselho")
    @classmethod
    def validar_orgao_conselho(cls, valor: str) -> str:
        return texto_obrigatorio(valor, "órgão do conselho", 30).upper()

    @field_validator("info_profissional")
    @classmethod
    def validar_info(cls, valor: str) -> str:
        return texto_obrigatorio(valor, "informações profissionais", 2000)

    @field_validator("especialidades")
    @classmethod
    def validar_especialidades(cls, valor: list[str]) -> list[str]:
        """Garante ao menos uma especialidade e remove repetidas (RN15).

        Passo a passo:
        1. Percorre a lista enviada.
        2. Limpa espaços e recusa item em branco ou maior que 80 caracteres.
        3. Ignora repetição sem diferenciar maiúsculas, como "Cardiologia" e "cardiologia".
        4. Se sobrar alguma, devolve a lista limpa. Lista vazia interrompe o cadastro.
        """
        # Inicializa as listas e conjuntos para armazenar os nomes das especialidades.
        nomes: list[str] = []
        vistos: set[str] = set()
        # Percorre a lista de especialidades.
        for item in valor:
            # Limpa espaços e recusa item em branco ou maior que 80 caracteres.
            nome = " ".join(item.split())
            if not nome:
                raise ValueError(
                    "A especialidade não pode ficar em branco. Informe ao menos uma especialidade."
                )
            # Recusa item maior que 80 caracteres.
            if len(nome) > 80:
                raise ValueError("Cada especialidade deve ter no máximo 80 caracteres.")
            chave = nome.casefold()
            # Ignora repetição sem diferenciar maiúsculas, como "Cardiologia" e "cardiologia".
            if chave in vistos:
                continue
            vistos.add(chave)
            nomes.append(nome)
        # Se não houver nenhuma especialidade, interrompe o cadastro.
        if not nomes:
            raise ValueError(
                "Informe ao menos uma especialidade para o profissional atuar na plataforma."
            )
        # Devolve a lista de especialidades limpa.
        return nomes


# Classe para representar o profissional de saúde que ainda aguarda a validação do administrador.
class ProfissionalPendenteResposta(Esquema):
    """Profissional de saúde que ainda aguarda a validação do administrador."""

    id_profissional: int
    nome: str
    email: str
    cpf: str
    numero_conselho: str
    orgao_conselho: str

    # Método para montar a resposta do profissional de saúde que ainda aguarda a validação do administrador.
    @classmethod
    def de_profissional(cls, profissional) -> "ProfissionalPendenteResposta":
        """Monta a linha da lista a partir do profissional e do primeiro conselho.

        Passo a passo:
        1. Copia o id do profissional e os dados da conta.
        2. Lê o conselho do primeiro vínculo gravado no cadastro.
        3. Devolve o objeto que a rota transforma em JSON.
        """
        vinculo = profissional.vinculos[0]
        return cls(
            id_profissional=profissional.id_profissional,
            nome=profissional.usuario.nome,
            email=profissional.usuario.email,
            cpf=profissional.usuario.cpf,
            numero_conselho=vinculo.conselho.numero_conselho,
            orgao_conselho=vinculo.conselho.orgao_conselho,
        )
