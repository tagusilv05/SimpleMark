# schemas/consulta_paciente.py
"""Saídas das consultas do paciente logado (/consultas/minhas)."""

from datetime import date, time
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel


class ProfissionalResumo(BaseModel):
    """Profissional e especialidade da consulta."""

    id_profissional: int
    nome: str
    path_imagem: Optional[str] = None
    especialidade: str


class AvaliacaoResumo(BaseModel):
    """Avaliação que o paciente deu à consulta."""

    avaliacao: int
    feedback: Optional[str] = None


class ConsultaPacienteResponse(BaseModel):
    """Consulta do paciente, em GET /consultas/minhas/{id_consulta} e na lista.

    pode_avaliar só é verdadeiro em consulta realizada ainda sem avaliação.
    """

    id_consulta: int
    data: date
    hora: time
    tipo: str
    status: str
    valor: Decimal
    profissional: ProfissionalResumo
    pagamento_status: Optional[str] = None
    avaliacao: Optional[AvaliacaoResumo] = None
    pode_avaliar: bool
    # Videochamada (Jitsi Meet): link nulo enquanto não gerado ou se a consulta foi cancelada.
    meet_link: Optional[str] = None


class AgendarConsultaInput(BaseModel):
    """Corpo de POST /consultas/agendar: o horário livre escolhido na busca."""

    id_horario: int


class ListaConsultasResponse(BaseModel):
    """Resposta de GET /consultas/minhas."""

    total: int
    itens: List[ConsultaPacienteResponse]