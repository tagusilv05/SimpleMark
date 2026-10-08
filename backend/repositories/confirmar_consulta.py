# CRIADO: JOAO MARCOS 

from sqlalchemy.orm import Session

from models.models import Consulta

# Adiciona uma nova consulta ao banco de dados e retorna a consulta cadastrada.
def adicionar_consulta(dados, id_paciente, id_esp_prof, db: Session):

    consulta = Consulta(
        id_paciente=id_paciente,
        id_esp_prof=id_esp_prof,
        data=dados.data,
        hora=dados.hora,
        tipo=dados.tipo,
        status=dados.status,
        valor=dados.valor
    )

    db.add(consulta)
    db.commit()
    db.refresh(consulta)

    return consulta