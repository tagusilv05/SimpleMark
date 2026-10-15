# CRIADO: JOAO MARCOS 

from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from sqlalchemy.orm import Session

from dependencies.database import get_db

from services.confirmar_consulta import confirmar_consulta as service_confirmar_consulta
from services.videochamada import enviar_email_confirmacao, gerar_link_nova_consulta

from schemas.confirmar_consulta import ConfirmarConsultaInput

router = APIRouter()

# Esse endpoint é responsável por receber os dados para confirmar e criar uma consulta
# O link da videochamada (Jitsi) é gerado na hora; o e-mail ao paciente sai em segundo plano, depois da resposta
@router.post("/confirmar-consulta")
def confirmar_consulta(dados: ConfirmarConsultaInput, tarefas: BackgroundTasks, db: Session = Depends(get_db)):
    try:

        consulta = service_confirmar_consulta(dados, db)

        gerar_link_nova_consulta(db, consulta.id_consulta)
        tarefas.add_task(enviar_email_confirmacao, consulta.id_consulta)

        return {
            "mensagem": "Consulta confirmada com sucesso",
            "id_consulta": consulta.id_consulta
        }

    except ValueError as erro:
        print(f"VALUE ERROR: {erro}")
        raise HTTPException(status_code=400, detail=str(erro))

    except Exception as erro:
        print(f"ERRO REAL: {erro}")
        raise HTTPException(status_code=500, detail="Erro ao confirmar consulta")