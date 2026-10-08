from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from sqlalchemy.orm import Session

from dependencies.autenticacao import UsuarioAtual
from dependencies.database import get_db
from services.avaliacao import avaliar_consulta, obter_media_profissional
from schemas.avaliacao import (
    AvaliacaoCreate,
    AvaliacaoResponse,
    MediaProfissionalResponse,
)

from typing import Annotated

from dependencies.autenticacao import PacienteAtual, ServicoAvaliacaoDep
from schemas.avaliacao import (
    AvaliacaoEntrada,
    AvaliacaoResposta,
    ProfissionalMelhorAvaliadoResposta,
    ResumoAvaliacoesResposta,
)
from schemas.comum import MensagemResposta


router = APIRouter(prefix="/avaliacoes", tags=["Avaliações"])


@router.post("", response_model=AvaliacaoResponse, status_code=status.HTTP_201_CREATED)
def avaliar_profissional(
    dados: AvaliacaoCreate,
    paciente: UsuarioAtual,
    db: Session = Depends(get_db),
):
    if paciente.paciente is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Somente pacientes podem avaliar consultas.",
        )
    return avaliar_consulta(db, dados, paciente.paciente.id_paciente)


@router.get("/profissionais/{id_profissional}/media", response_model=MediaProfissionalResponse)
def media_profissional(
    id_profissional: int,
    db: Session = Depends(get_db),
):
    return obter_media_profissional(db, id_profissional)


@router.post(
    "/consultas/{id_consulta}/avaliacao",
    response_model=AvaliacaoResposta,
    status_code=201,
    summary="Avaliar a consulta",
    responses={
        401: {"model": MensagemResposta},
        403: {"model": MensagemResposta},
        404: {"model": MensagemResposta},
        409: {"model": MensagemResposta},
        422: {"model": MensagemResposta},
    },
)
def avaliar_consulta(
    id_consulta: int,
    dados: Annotated[
        AvaliacaoEntrada,
        Body(
            openapi_examples={
                "com_estrelas": {
                    "summary": "Estrelas e comentário",
                    "value": {"nota": 5, "feedback": "Atendimento excelente."},
                },
                "sem_estrelas": {
                    "summary": "Somente comentário",
                    "value": {"feedback": "Consulta tranquila."},
                },
            }
        ),
    ],
    servico: ServicoAvaliacaoDep,
    paciente: PacienteAtual,
) -> AvaliacaoResposta:
    avaliacao = servico.avaliar(paciente, id_consulta, dados)
    return AvaliacaoResposta.model_validate(avaliacao, from_attributes=True)


@router.get(
    "/consultas/{id_consulta}/avaliacao",
    response_model=AvaliacaoResposta,
    summary="Ver a minha avaliação da consulta",
    responses={
        401: {"model": MensagemResposta},
        403: {"model": MensagemResposta},
        404: {"model": MensagemResposta},
    },
)
def minha_avaliacao(
    id_consulta: int,
    servico: ServicoAvaliacaoDep,
    paciente: PacienteAtual,
) -> AvaliacaoResposta:
    avaliacao = servico.minha_avaliacao(paciente, id_consulta)
    return AvaliacaoResposta.model_validate(avaliacao, from_attributes=True)


@router.get(
    "/profissionais/{id_profissional}/avaliacoes",
    response_model=ResumoAvaliacoesResposta,
    summary="Média e distribuição das estrelas do profissional",
    responses={404: {"model": MensagemResposta}},
)
def resumo_avaliacoes(
    id_profissional: int,
    servico: ServicoAvaliacaoDep,
) -> ResumoAvaliacoesResposta:
    return servico.resumo_do_profissional(id_profissional)


@router.get(
    "/profissionais/melhor-avaliados",
    response_model=list[ProfissionalMelhorAvaliadoResposta],
    summary="Profissionais mais bem avaliados",
    responses={422: {"model": MensagemResposta}},
)
def melhor_avaliados(
    servico: ServicoAvaliacaoDep,
    id_especialidade: int | None = Query(default=None, description="Filtra por especialidade"),
    limite: int = Query(default=10, ge=1, le=50, description="Quantidade máxima de profissionais"),
) -> list[ProfissionalMelhorAvaliadoResposta]:
    return servico.ranking(id_especialidade, limite)
