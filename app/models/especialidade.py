# Arquivo criado por Victor
from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Especialidade(Base):
    """Especialidade oferecida na plataforma.

    A coluna no banco chama-se especialidade, como na figura do modelo.
    O atributo Python é nome para não colidir com a classe.
    """

    __tablename__ = "especialidade"

    id_especialidade: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column("especialidade", String(80), unique=True, nullable=False)