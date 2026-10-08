# routers/busca_profissional.py
from datetime import date, time

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from dependencies.database import get_db
from schemas.busca_profissional import (
    FiltroBuscaProfissional,
    OrdenacaoBusca,
    ProfissionalBuscaOutput,
)
from services.busca_profissional import buscar_profissionais

router = APIRouter(prefix="/profissionais", tags=["Busca de Profissionais"])


# Endpoint público da busca de profissionais. O paciente combina especialidade,
# período, faixa de horário e faixa de preço; a resposta traz, de cada
# profissional encontrado, os horários ainda livres para o agendamento.
@router.get("/busca", response_model=list[ProfissionalBuscaOutput])
def buscar(
    id_especialidade: int | None = Query(
        default=None, ge=1, description="Especialidade exata, pelo id do catálogo."
    ),
    especialidade: str | None = Query(
        default=None,
        min_length=2,
        max_length=100,
        description="Parte do nome da especialidade, sem diferenciar maiúsculas.",
    ),
    data_inicio: date | None = Query(
        default=None, description="Primeiro dia do período (AAAA-MM-DD). Padrão: hoje."
    ),
    data_fim: date | None = Query(
        default=None, description="Último dia do período (AAAA-MM-DD)."
    ),
    hora_inicio: time | None = Query(
        default=None, description="Não devolve horário que comece antes disso (HH:MM)."
    ),
    hora_fim: time | None = Query(
        default=None, description="Não devolve horário que termine depois disso (HH:MM)."
    ),
    valor_min: float | None = Query(
        default=None, ge=0, description="Valor mínimo da consulta."
    ),
    valor_max: float | None = Query(
        default=None, ge=0, description="Valor máximo da consulta."
    ),
    ordenar_por: OrdenacaoBusca = Query(
        default=OrdenacaoBusca.NOME,
        description="nome (A-Z), valor (do mais barato) ou avaliacao (da maior nota).",
    ),
    db: Session = Depends(get_db),
):
    filtro = FiltroBuscaProfissional(
        id_especialidade=id_especialidade,
        especialidade=especialidade,
        data_inicio=data_inicio,
        data_fim=data_fim,
        hora_inicio=hora_inicio,
        hora_fim=hora_fim,
        valor_min=valor_min,
        valor_max=valor_max,
        ordenar_por=ordenar_por,
    )
    return buscar_profissionais(db=db, filtro=filtro)
