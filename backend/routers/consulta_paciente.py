# routers/consulta_paciente_router.py
"""Rotas do paciente logado para agendar, listar e detalhar as próprias consultas."""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from dependencies.autenticacao import UsuarioAtual
from dependencies.database import get_db
from models.models import Paciente
from schemas.consulta_paciente import (
    AgendarConsultaInput,
    ConsultaPacienteResponse,
    ListaConsultasResponse,
)
from services.consulta_paciente import agendar_consulta, detalhar_consulta, listar_consultas
from services.videochamada import gerar_link_nova_consulta

router = APIRouter(prefix="/consultas", tags=["Consultas do paciente"])


def get_paciente_logado(usuario: UsuarioAtual) -> Paciente:
    """Devolve o paciente da conta logada; outros perfis recebem 403.

    Args:
        usuario (Usuario): Usuário logado, injetado pelo FastAPI.

    Returns:
        Paciente: Paciente vinculado à conta logada.

    Raises:
        HTTPException: Quando a conta logada não é de paciente (403).
    """
    paciente = usuario.paciente
    if paciente is None:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Apenas pacientes podem acessar suas consultas.",
        )
    return paciente


@router.post(
    "/agendar",
    response_model=ConsultaPacienteResponse,
    status_code=status.HTTP_201_CREATED,
)
def agendar(
    dados: AgendarConsultaInput,
    paciente: Paciente = Depends(get_paciente_logado),
    db: Session = Depends(get_db),
):
    """Agenda uma consulta do paciente logado num horário livre.

    Somente pacientes. Responde 404 se o horário não existir e 409 se ele não
    estiver mais livre. Gera o link da videochamada; o e-mail de confirmação
    só é enviado depois que o pagamento for aprovado (PagamentoService).

    Args:
        dados (AgendarConsultaInput): Id do horário escolhido.
        paciente (Paciente): Paciente logado, injetado pelo FastAPI.
        db (Session): Sessão do banco de dados, injetada pelo FastAPI.

    Returns:
        ConsultaPacienteResponse: Detalhes da consulta agendada.
    """
    consulta = agendar_consulta(db, dados.id_horario, paciente.id_paciente)
    gerar_link_nova_consulta(db, consulta.id_consulta)
    return detalhar_consulta(db, consulta.id_consulta, paciente.id_paciente)


@router.get("/minhas", response_model=ListaConsultasResponse)
def minhas_consultas(
    status_consulta: Optional[str] = Query(None, alias="status"),
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    paciente: Paciente = Depends(get_paciente_logado),
    db: Session = Depends(get_db),
):
    """Lista as consultas do paciente logado, com filtros e paginação.

    Somente pacientes (401 sem token, 403 para outros perfis). Filtra por status e
    período; responde 400 se data_inicio for maior que data_fim.

    Args:
        status_consulta (str | None): Filtro por status (parâmetro ``status``).
        data_inicio (date | None): Início do período.
        data_fim (date | None): Fim do período.
        skip (int): Quantidade de registros a pular (paginação).
        limit (int): Quantidade máxima de registros (1 a 100).
        paciente (Paciente): Paciente logado, injetado pelo FastAPI.
        db (Session): Sessão do banco de dados, injetada pelo FastAPI.

    Returns:
        ListaConsultasResponse: Consultas encontradas, paginadas.
    """
    return listar_consultas(
        db,
        paciente.id_paciente,
        status_consulta,
        data_inicio,
        data_fim,
        skip,
        limit,
    )


@router.get("/minhas/{id_consulta}", response_model=ConsultaPacienteResponse)
def detalhar_minha_consulta(
    id_consulta: int,
    paciente: Paciente = Depends(get_paciente_logado),
    db: Session = Depends(get_db),
):
    """Detalha uma consulta do paciente logado.

    Somente pacientes. Responde 404 se a consulta não existir ou for de outro
    paciente.

    Args:
        id_consulta (int): Id da consulta.
        paciente (Paciente): Paciente logado, injetado pelo FastAPI.
        db (Session): Sessão do banco de dados, injetada pelo FastAPI.

    Returns:
        ConsultaPacienteResponse: Detalhes da consulta.
    """
    return detalhar_consulta(db, id_consulta, paciente.id_paciente)