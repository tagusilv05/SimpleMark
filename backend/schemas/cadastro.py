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
        return normalizar_cpf(valor)

    @field_validator("email")
    @classmethod
    def email_valido(cls, valor: str) -> str:
        return normalizar_email(valor)

    @field_validator("cep")
    @classmethod
    def cep_valido(cls, valor: str) -> str:
        return normalizar_cep(valor)

    @field_validator("telefone")
    @classmethod
    def telefone_valido(cls, valor: str) -> str:
        return normalizar_telefone(valor)

    @field_validator("senha")
    @classmethod
    def senha_minima(cls, valor: str) -> str:
        if len(valor) < 8:
            raise ValueError("A senha deve ter no mínimo 8 caracteres.")
        return valor

    @field_validator("consentimento_lgpd")
    @classmethod
    def consentimento_obrigatorio(cls, valor: bool) -> bool:
        if valor is not True:
            raise ValueError(
                "É preciso autorizar o consentimento para o tratamento dos dados pessoais."
            )
        return valor

    @field_validator("data_nascimento")
    @classmethod
    def nascimento_no_passado(cls, valor: date) -> date:
        if valor >= date.today():
            raise ValueError("A data de nascimento precisa ser anterior a hoje. Use o formato AAAA-MM-DD.")
        return valor

    @field_validator("complemento")
    @classmethod
    def complemento_opcional(cls, valor: str | None) -> str | None:
        if valor is None:
            return None
        texto = valor.strip()
        return texto or None


class CadastroProfissionalEntrada(CadastroUsuarioEntrada):
    numero_conselho: str = Field(min_length=1, max_length=30)
    orgao_conselho: str = Field(min_length=2, max_length=30)
    info_profissional: str = Field(min_length=3)
    especialidades: list[str] = Field(min_length=1)

    @field_validator("especialidades")
    @classmethod
    def especialidades_validas(cls, valor: list[str]) -> list[str]:
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
    id_profissional: int
    nome: str
    email: str
    cpf: str
    numero_conselho: str | None = None
    orgao_conselho: str | None = None
    especialidades: list[str]

    @classmethod
    def de_profissional(cls, profissional: Profissional) -> "ProfissionalPendenteResposta":
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
