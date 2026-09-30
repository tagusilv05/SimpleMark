# Arquivo criado por Victor
from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Endereco(Base):
    """Endereço do usuário: o CEP e o texto do endereço."""

    __tablename__ = "endereco"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuario.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    cep: Mapped[str] = mapped_column(String(8), nullable=False)
    endereco: Mapped[str] = mapped_column(String(200), nullable=False)

    usuario: Mapped[Usuario] = relationship("Usuario", back_populates="endereco")


from app.models.usuario import Usuario  # noqa: E402