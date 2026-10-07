from typing import Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.models import Avaliacao, Consulta, ProfissionalEspecialidade


def buscar_consulta(db: Session, id_consulta: int) -> Optional[Consulta]:
    return (
        db.query(Consulta)
        .filter(Consulta.id_consulta == id_consulta)
        .first()
    )


def buscar_avaliacao(db: Session, id_consulta: int) -> Optional[Avaliacao]:
    return (
        db.query(Avaliacao)
        .filter(Avaliacao.id_consulta == id_consulta)
        .first()
    )


def criar_avaliacao(db: Session, avaliacao: Avaliacao) -> Avaliacao:
    db.add(avaliacao)
    db.commit()
    db.refresh(avaliacao)
    return avaliacao


def calcular_media_profissional(
    db: Session, id_profissional: int
) -> Tuple[Optional[float], int]:
    media, total = (
        db.query(func.avg(Avaliacao.avaliacao), func.count(Avaliacao.id_consulta))
        .join(Consulta, Consulta.id_consulta == Avaliacao.id_consulta)
        .join(
            ProfissionalEspecialidade,
            ProfissionalEspecialidade.id_esp_prof == Consulta.id_esp_prof,
        )
        .filter(ProfissionalEspecialidade.id_profissional == id_profissional)
        .one()
    )
    return (round(float(media), 2) if media is not None else None), total
