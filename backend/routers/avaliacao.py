from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies.autenticacao import UsuarioAtual
from dependencies.database import get_db
from services.avaliacao import avaliar_consulta, obter_media_profissional
from schemas.avaliacao import (
    AvaliacaoCreate,
    AvaliacaoResponse,
    MediaProfissionalResponse,
)

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