# CRIADO: JOAO MARCOS 

"""Consultas usadas na busca das avaliações de um profissional."""

from sqlalchemy.orm import Session

from models.models import (
    Consulta,
    ProfissionalEspecialidade,
)

# Busca no banco a relação entre o profissional e a especialidade informados.
def buscar_profissional_especialidade(id_profissional, id_especialidade, db: Session):
    """Vínculo entre o profissional e a especialidade, ou None se não existir.

    Args:
        id_profissional (int): Id do profissional.
        id_especialidade (int): Id da especialidade.
        db (Session): Sessão do banco de dados.

    Returns:
        ProfissionalEspecialidade | None: Vínculo encontrado, ou None.
    """
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
   """Todas as consultas de um vínculo profissional-especialidade.

   Args:
       id_esp_prof (int): Id do vínculo profissional-especialidade.
       db (Session): Sessão do banco de dados.

   Returns:
       list[Consulta]: Consultas do vínculo (lista vazia se não houver).
   """
   return (
        db.query(Consulta)
        .filter(
            Consulta.id_esp_prof == id_esp_prof
        )
        .all()
    )

