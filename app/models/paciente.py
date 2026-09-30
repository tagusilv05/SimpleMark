# Arquivo criado por Victor
from __future__ import annotations

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Paciente(Base):
    """Perfil de paciente. Os dados pessoais ficam em usuario (RF1)."""

    __tablename__ = "paciente"

    id_paciente: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuario.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    usuario: Mapped[Usuario] = relationship("Usuario", back_populates="paciente")


from app.models.usuario import Usuario  # noqa: E402