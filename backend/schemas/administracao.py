import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from models.models import Paciente, Profissional
from models.administracao import LogAcaoAdministrador


class BanirEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    motivo: str | None = Field(default=None, max_length=500)


class ProfissionalIdResposta(BaseModel):
    id_profissional: int
    id_usuario: uuid.UUID
    nome: str
    email: str

    @classmethod
    def de_profissional(cls, profissional: Profissional) -> "ProfissionalIdResposta":
        return cls(
            id_profissional=profissional.id_profissional,
            id_usuario=profissional.id_usuario,
            nome=profissional.usuario.nome,
            email=profissional.usuario.email,
        )


class PacienteIdResposta(BaseModel):
    id_paciente: int
    id_usuario: uuid.UUID
    nome: str
    email: str

    @classmethod
    def de_paciente(cls, paciente: Paciente) -> "PacienteIdResposta":
        return cls(
            id_paciente=paciente.id_paciente,
            id_usuario=paciente.id_usuario,
            nome=paciente.usuario.nome,
            email=paciente.usuario.email,
        )


class IdsUsuariosResposta(BaseModel):
    profissionais: list[ProfissionalIdResposta]
    pacientes: list[PacienteIdResposta]


class LogAcaoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_log: int
    id_administrador: int
    acao: str
    alvo_tipo: str
    alvo_id: int
    id_usuario_alvo: uuid.UUID | None
    detalhe: str | None
    realizada_em: datetime

    @classmethod
    def de_log(cls, log: LogAcaoAdministrador) -> "LogAcaoResposta":
        return cls.model_validate(log)