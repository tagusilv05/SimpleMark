# CRIADO: JOAO MARCOS 

from sqlalchemy.orm import Session

from models.models import (
    Consulta,
    ProfissionalEspecialidade,
)

# Busca no banco a relação entre o profissional e a especialidade informados.
def buscar_profissional_especialidade(id_profissional, id_especialidade, db: Session):
    return (
        db.query(ProfissionalEspecialidade)
        .filter(
            ProfissionalEspecialidade.id_profissional == id_profissional,
            ProfissionalEspecialidade.id_especialidade == id_especialidade
        )
        .first()
    )

# Busca no banco todas as consultas vinculadas ao profissional e à especialidade.
def buscar_consultas_do_profissional(id_esp_prof, db: Session):
   return (
        db.query(Consulta)
        .filter(
            Consulta.id_esp_prof == id_esp_prof
        )
        .all()
    )

