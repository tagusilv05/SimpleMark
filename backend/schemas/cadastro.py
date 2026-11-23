"""Entradas do cadastro de pacientes e profissionais e a lista de pendentes."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.validadores import normalizar_cep, normalizar_cpf, normalizar_email, normalizar_telefone
from models.models import Profissional


class CadastroUsuarioEntrada(BaseModel):
    """Dados do paciente, já no formato das colunas de usuario e endereco."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    nome: str = Field(min_length=3, max_length=150)
    cpf: str
    orgao_emissor: str = Field(min_length=2, max_length=50)
    data_nascimento: date
    genero: str = Field(min_length=1, max_length=30)
    telefone: str
    email: str
    senha: str
    consentimento_lgpd: bool
    cep: str
    cidade: str = Field(min_length=2, max_length=100)
    logradouro: str = Field(min_length=2, max_length=150)
    numero: str = Field(min_length=1, max_length=20)
    bairro: str = Field(min_length=2, max_length=100)
    complemento: str | None = Field(default=None, max_length=150)

    @field_validator("cpf")
    @classmethod
    def cpf_valido(cls, valor: str) -> str:
        """Normaliza e valida o CPF.

        Args:
            valor (str): CPF informado.

        Returns:
            str: CPF no formato ``000.000.000-00``.
        """
        return normalizar_cpf(valor)

    @field_validator("email")
    @classmethod
    def email_valido(cls, valor: str) -> str:
        """Normaliza e valida o e-mail.

        Args:
            valor (str): E-mail informado.

        Returns:
            str: E-mail normalizado.
        """
        return normalizar_email(valor)

    @field_validator("cep")
    @classmethod
    def cep_valido(cls, valor: str) -> str:
        """Normaliza e valida o CEP.

        Args:
            valor (str): CEP informado.

        Returns:
            str: CEP no formato ``00000-000``.
        """
        return normalizar_cep(valor)

    @field_validator("telefone")
    @classmethod
    def telefone_valido(cls, valor: str) -> str:
        """Normaliza e valida o telefone.

        Args:
            valor (str): Telefone informado.

        Returns:
            str: Somente os dígitos do telefone.
        """
        return normalizar_telefone(valor)

    @field_validator("senha")
    @classmethod
    def senha_minima(cls, valor: str) -> str:
        """Recusa senha com menos de 8 caracteres.

        Args:
            valor (str): Senha informada.

        Returns:
            str: A senha, sem alteração.

        Raises:
            ValueError: Quando a senha tem menos de 8 caracteres.
        """
        if len(valor) < 8:
            raise ValueError("A senha deve ter no mínimo 8 caracteres.")
        return valor

    @field_validator("consentimento_lgpd")
    @classmethod
    def consentimento_obrigatorio(cls, valor: bool) -> bool:
        """Exige o consentimento LGPD marcado.

        Args:
            valor (bool): Consentimento informado.

        Returns:
            bool: O consentimento, sem alteração.

        Raises:
            ValueError: Quando o consentimento não é ``True``.
        """
        if valor is not True:
            raise ValueError(
                "É preciso autorizar o consentimento para o tratamento dos dados pessoais."
            )
        return valor

    @field_validator("data_nascimento")
    @classmethod
    def nascimento_no_passado(cls, valor: date) -> date:
        """Exige data de nascimento anterior a hoje.

        Args:
            valor (date): Data de nascimento informada.

        Returns:
            date: A data, sem alteração.

        Raises:
            ValueError: Quando a data é hoje ou futura.
        """
        if valor >= date.today():
            raise ValueError("A data de nascimento precisa ser anterior a hoje. Use o formato AAAA-MM-DD.")
        return valor

    @field_validator("complemento")
    @classmethod
    def complemento_opcional(cls, valor: str | None) -> str | None:
        """Trata complemento em branco como ausente.

        Args:
            valor (str | None): Complemento informado, ou ``None``.

        Returns:
            str | None: Complemento sem espaços nas pontas, ou ``None`` se em branco.
        """
        if valor is None:
            return None
        texto = valor.strip()
        return texto or None


class CadastroProfissionalEntrada(CadastroUsuarioEntrada):
    """Corpo de POST /cadastro/profissional: dados do paciente mais conselho,
    apresentação e especialidades.
    """

    numero_conselho: str = Field(min_length=1, max_length=30)
    orgao_conselho: str = Field(min_length=2, max_length=30)
    info_profissional: str = Field(min_length=3)
    especialidades: list[str] = Field(min_length=1)

    @field_validator("especialidades")
    @classmethod
    def especialidades_validas(cls, valor: list[str]) -> list[str]:
        """Limpa a lista: tira itens vazios e repetidos (sem diferenciar
        maiúsculas) e exige ao menos uma especialidade de até 100 caracteres.

        Args:
            valor (list[str]): Especialidades informadas.

        Returns:
            list[str]: Especialidades limpas, sem vazias nem repetidas.

        Raises:
            ValueError: Quando alguma especialidade passa de 100 caracteres ou não sobra
                nenhuma especialidade válida.
        """
        limpas: list[str] = []
        for item in valor:
            nome = item.strip()
            if not nome:
                continue
            if len(nome) > 100:
                raise ValueError("Cada especialidade deve ter no máximo 100 caracteres.")
            if nome.casefold() not in {existente.casefold() for existente in limpas}:
                limpas.append(nome)
        if not limpas:
            raise ValueError("Informe ao menos uma especialidade para o profissional atuar na plataforma.")
        return limpas


class ProfissionalPendenteResposta(BaseModel):
    """Profissional aguardando validação, em GET
    /administracao/profissionais/pendentes.
    """

    id_profissional: int
    nome: str
    email: str
    cpf: str
    numero_conselho: str | None = None
    orgao_conselho: str | None = None
    especialidades: list[str]

    @classmethod
    def de_profissional(cls, profissional: Profissional) -> "ProfissionalPendenteResposta":
        """Monta a resposta com as especialidades e o primeiro conselho achado.

        Args:
            profissional (Profissional): Profissional com usuário e especialidades carregados.

        Returns:
            ProfissionalPendenteResposta: Resposta montada a partir do profissional.
        """
        numero = None
        orgao = None
        nomes: list[str] = []
        for vinculo in profissional.especialidades:
            if vinculo.especialidade is not None:
                nomes.append(vinculo.especialidade.especialidade)
            if numero is None and vinculo.conselho is not None:
                numero = vinculo.conselho.numero_conselho
                orgao = vinculo.conselho.orgao_conselho
        return cls(
            id_profissional=profissional.id_profissional,
            nome=profissional.usuario.nome,
            email=profissional.usuario.email,
            cpf=profissional.usuario.cpf,
            numero_conselho=numero,
            orgao_conselho=orgao,
            especialidades=nomes,
        )
