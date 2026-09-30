import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.acesso import Credencial


class RepositorioCredencial:
    """Senha e contador de falhas. A trava da linha evita duas tentativas ao mesmo tempo."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def buscar_para_atualizar(self, id_usuario: uuid.UUID) -> Credencial | None:
        comando = (
            select(Credencial)
            .where(Credencial.id_usuario == id_usuario)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return self.db.execute(comando).scalar_one_or_none()

    def adicionar(self, credencial: Credencial) -> Credencial:
        self.db.add(credencial)
        return credencial
