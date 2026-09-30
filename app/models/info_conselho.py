# Arquivo criado por Victor
from __future__ import annotations

from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class InfoConselho(Base):
    """Registro do profissional no conselho de classe (RF20, RN3)."""

    __tablename__ = "info_conselho"
    __table_args__ = (
        UniqueConstraint(
            "numero_conselho",
            "orgao_conselho",
            name="uq_info_conselho_numero_orgao",
        ),
    )

    id_conselho: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    numero_conselho: Mapped[str] = mapped_column(String(30), nullable=False)
    orgao_conselho: Mapped[str] = mapped_column(String(30), nullable=False)