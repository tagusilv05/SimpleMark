from sqlalchemy import select
from sqlalchemy.orm import Session

from models.models import InfoConselho


class RepositorioConselho:
    def __init__(self, db: Session) -> None:
        self.db = db

    def buscar(self, numero_conselho: str, orgao_conselho: str) -> InfoConselho | None:
        return self.db.scalar(
            select(InfoConselho).where(
                InfoConselho.numero_conselho == numero_conselho,
                InfoConselho.orgao_conselho == orgao_conselho,
            )
        )
