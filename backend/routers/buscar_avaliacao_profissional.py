# CRIADO: JOAO MARCOS 

from fastapi import APIRouter,  HTTPException,  Depends
from sqlalchemy.orm import Session

from dependencies.database import get_db

from services.buscar_avaliacao_profissional import buscar_avaliacoes_profissional as service_buscar_avaliacoes_profissional


from schemas.buscar_avaliacao_profissional import (
    AvaliacaoConsultaInput,
    AvaliacaoConsultaOutput
)

router = APIRouter()

# Busca as avaliações do profissional por especialidade 
@router.post("/buscar-avaliacoes", response_model=AvaliacaoConsultaOutput)
def buscar_avaliacoes(dados: AvaliacaoConsultaInput, db: Session = Depends(get_db)):
    try:

        avaliacao, total, sub_total = service_buscar_avaliacoes_profissional(dados, db)

        return {
            "avaliacao": avaliacao,
            "total": total,
            "sub_total": sub_total
        }

    except ValueError as erro:
        print(f"VALUE ERROR: {erro}")
        raise HTTPException(status_code=400, detail=str(erro))

    except Exception as erro:
        print(f"ERRO REAL: {erro}")
        raise HTTPException(status_code=500, detail="Erro ao buscar avaliações")