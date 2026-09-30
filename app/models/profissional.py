# Arquivo criado por Victor
from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Profissional(Base):
    """Perfil do profissional de saúde.

    Os dados pessoais ficam em usuario. Aqui ficam as informações
    profissionais e os vínculos com especialidade e conselho.
    """

    __tablename__ = "profissional"

    id_profissional: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuario.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    info_profissional: Mapped[str] = mapped_column(Text, nullable=False)

    usuario: Mapped[Usuario] = relationship("Usuario", back_populates="profissional")
    vinculos: Mapped[list[ProfissionalEspecialidade]] = relationship(
        "ProfissionalEspecialidade",
        back_populates="profissional",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


from app.models.profissional_especialidade import ProfissionalEspecialidade  # noqa: E402
from app.models.usuario import Usuario  # noqa: E402