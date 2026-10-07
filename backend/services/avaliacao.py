from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.models import Avaliacao
from repositories.avaliacao import (buscar_avaliacao,buscar_consulta, calcular_media_profissional, criar_avaliacao)
from schemas.avaliacao import (AvaliacaoCreate, AvaliacaoResponse, MediaProfissionalResponse)

def avaliar_consulta(
    db: Session, dados: AvaliacaoCreate, id_paciente: int
) -> AvaliacaoResponse:
    consulta = buscar_consulta(db, dados.id_consulta)

    if consulta is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Consulta não encontrada.")
    if consulta.id_paciente != id_paciente:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "Você não pode avaliar esta consulta."
        )
    if consulta.status != "realizada":
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Só é possível avaliar consultas realizadas.",
        )
    if buscar_avaliacao(db, dados.id_consulta) is not None:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Esta consulta já foi avaliada."
        )

    agora = datetime.now()
    nova = criar_avaliacao(
        db,
        Avaliacao(
            id_consulta=dados.id_consulta,
            avaliacao=dados.avaliacao,
            feedback=dados.feedback,
            data=agora.date(),
            hora=agora.time().replace(microsecond=0),
        ),
    )

    return AvaliacaoResponse(
        id_consulta=nova.id_consulta,
        id_profissional=consulta.profissional_especialidade.id_profissional,
        avaliacao=nova.avaliacao,
        feedback=nova.feedback,
        data=nova.data,
        hora=nova.hora,
    )


def obter_media_profissional(
    db: Session, id_profissional: int
) -> MediaProfissionalResponse:
    media, total = calcular_media_profissional(db, id_profissional)
    return MediaProfissionalResponse(
        id_profissional=id_profissional,
        media=media,
        total=total,
    )
