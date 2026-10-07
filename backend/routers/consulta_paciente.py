# routers/consulta_paciente_router.py
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from dependencies.autenticacao import UsuarioAtual
from dependencies.database import get_db
from models.models import Paciente
from schemas.consulta_paciente import ConsultaPacienteResponse, ListaConsultasResponse
from services.consulta_paciente import detalhar_consulta, listar_consultas

router = APIRouter(prefix="/consultas", tags=["Consultas do paciente"])


def get_paciente_logado(usuario: UsuarioAtual) -> Paciente:
    paciente = usuario.paciente
    if paciente is None:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Apenas pacientes podem acessar suas consultas.",
        )
    return paciente


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
    return detalhar_consulta(db, id_consulta, paciente.id_paciente)