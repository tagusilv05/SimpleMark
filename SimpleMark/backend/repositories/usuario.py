import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.models import Usuario


class RepositorioUsuario:
    """Consultas da tabela usuario. Não aplica regra de negócio."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def buscar_por_id(self, id_usuario: uuid.UUID) -> Usuario | None:
        return self.db.get(Usuario, id_usuario)

    def buscar_por_email(self, email: str) -> Usuario | None:
        return self.db.scalar(select(Usuario).where(Usuario.email == email))

    def buscar_por_cpf(self, cpf: str) -> Usuario | None:
        return self.db.scalar(select(Usuario).where(Usuario.cpf == cpf))

    def adicionar(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        return usuario
