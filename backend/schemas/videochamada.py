"""Entradas e saídas das rotas da videochamada (Jitsi Meet) da consulta."""

from datetime import date, datetime, time
from pydantic import BaseModel, ConfigDict, Field

from core.tempo import agora_local
from models.models import Consulta

_STATUS_SEM_LINK = {"cancelada", "cancelado"}


def link_visivel(consulta: Consulta) -> str | None:
    """Link da videochamada para exibir: some quando a consulta é cancelada."""
    return None if consulta.status in _STATUS_SEM_LINK else consulta.meet_link


def _idade(nascimento: date | None) -> int | None:
    """Idade em anos completos na data de hoje (horário de Brasília)."""
    if nascimento is None:
        return None
    hoje = agora_local().date()
    return hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))


def _cpf_mascarado(cpf: str | None) -> str | None:
    """CPF só com os 3 primeiros e os 2 últimos dígitos: 123.***.***-01."""
    digitos = "".join(c for c in (cpf or "") if c.isdigit())
    if len(digitos) != 11:
        return None
    return f"{digitos[:3]}.***.***-{digitos[-2:]}"


class PacienteVideochamadaOutput(BaseModel):
    """Paciente da consulta, como aparece na tela de atendimento."""

    nome: str
    idade: int | None = None
    cpf: str | None = Field(default=None, description="CPF mascarado (123.***.***-01).")

class VideochamadaOutput(BaseModel):
    """Dados da videochamada de uma consulta."""

    id_consulta: int
    data: date = Field(description="Data da consulta (horário de Brasília).")
    hora: time = Field(description="Hora de início da consulta (horário de Brasília).")
    status_consulta: str
    meet_link: str | None = Field(
        default=None,
        description="Link da sala no Jitsi Meet. Nulo se a consulta foi cancelada ou já foi realizada sem link.",
    )
    data_geracao_link: datetime | None = Field(default=None, description="Quando o link foi gerado (UTC).")
    paciente: PacienteVideochamadaOutput | None = None

    @classmethod
    def da_consulta(cls, consulta: Consulta) -> "VideochamadaOutput":
        """Monta a saída a partir do modelo, escondendo o link de consulta cancelada."""
        usuario = consulta.paciente.usuario if consulta.paciente else None
        paciente = (
            PacienteVideochamadaOutput(
                nome=usuario.nome,
                idade=_idade(usuario.data_nascimento),
                cpf=_cpf_mascarado(usuario.cpf),
            )
            if usuario
            else None
        )
        return cls(
            paciente=paciente,
            id_consulta=consulta.id_consulta,
            data=consulta.data,
            hora=consulta.hora,
            status_consulta=consulta.status,
            meet_link=link_visivel(consulta),
            data_geracao_link=consulta.data_geracao_link,
        )


class OperacaoVideochamadaOutput(BaseModel):
    """Resposta de reagendamento, cancelamento e reprocessamento."""

    mensagem: str
    consulta: VideochamadaOutput


class ReagendarConsultaInput(BaseModel):
    """Nova data e hora; precisam existir livres na agenda do profissional."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"examples": [{"data": "2026-11-05", "hora": "14:30:00"}]},
    )

    data: date
    hora: time
