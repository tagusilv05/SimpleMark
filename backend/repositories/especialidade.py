from sqlalchemy import select
from sqlalchemy.orm import Session

from models.models import Especialidade


class RepositorioEspecialidade:
    """Reaproveita a especialidade pelo nome, sem diferenciar maiúsculas."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def obter_ou_criar(self, nome: str) -> Especialidade:
        existentes = self.db.scalars(select(Especialidade)).all()
        for item in existentes:
            if item.especialidade.casefold() == nome.casefold():
                return item
        criada = Especialidade(especialidade=nome)
        self.db.add(criada)
        self.db.flush()
        return criada
