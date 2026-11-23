# routers/profissional.py
"""Rota que lista as consultas de um profissional."""

from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dependencies.database import get_db
from schemas.consulta_profissional import ConsultaProfissionalOut
from services.consulta_profissional import listar_consultas_do_profissional

router = APIRouter(prefix="/consultas_profissionais", tags=["Consultas Profissionais"])

@router.get("/{id_profissional}/consultas", response_model=list[ConsultaProfissionalOut])
def consultas_do_profissional(
    id_profissional: int,
    status: str | None = Query("agendada"),
    data_inicio: date | None = None,
    data_fim: date | None = None,
    db: Session = Depends(get_db),
):
    """Lista as consultas do profissional, com os dados do paciente.

    Rota sem autenticação. Por padrão traz só as agendadas e aceita filtro por
    período. Responde 404 se o profissional não existir.

    Args:
        id_profissional (int): Id do profissional.
        status (str | None): Filtro por status; padrão ``agendada``.
        data_inicio (date | None): Início do período.
        data_fim (date | None): Fim do período.
        db (Session): Sessão do banco de dados, injetada pelo FastAPI.

    Returns:
        list[ConsultaProfissionalOut]: Consultas do profissional com os dados do paciente.

    Raises:
        HTTPException: Quando o profissional não existe (404).
    """
    consultas = listar_consultas_do_profissional(
        db, id_profissional, status, data_inicio, data_fim
    )
    if consultas is None:
        raise HTTPException(status_code=404, detail="Profissional não encontrado.")
    return consultas