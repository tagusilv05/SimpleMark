# routers/consulta_paciente_router.py
"""Rotas do paciente logado para agendar, listar e detalhar as próprias consultas."""

from datetime import date
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
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
from services.videochamada import enviar_email_confirmacao, gerar_link_nova_consulta

router = APIRouter(prefix="/consultas", tags=["Consultas do paciente"])


def get_paciente_logado(usuario: UsuarioAtual) -> Paciente:
    """Devolve o paciente da conta logada; outros perfis recebem 403."""
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
    tarefas: BackgroundTasks,
    paciente: Paciente = Depends(get_paciente_logado),
    db: Session = Depends(get_db),
):
    """Agenda uma consulta do paciente logado num horário livre.

    Somente pacientes. Responde 404 se o horário não existir e 409 se ele não
    estiver mais livre. Gera o link da videochamada e envia o e-mail de
    confirmação em segundo plano.
    """
    consulta = agendar_consulta(db, dados.id_horario, paciente.id_paciente)
    gerar_link_nova_consulta(db, consulta.id_consulta)
    tarefas.add_task(enviar_email_confirmacao, consulta.id_consulta)
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
    """
    return detalhar_consulta(db, id_consulta, paciente.id_paciente)