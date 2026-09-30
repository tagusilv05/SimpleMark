# Arquivo criado por Victor
from __future__ import annotations

from sqlalchemy import Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ProfissionalEspecialidade(Base):
    """Liga o profissional à especialidade e ao conselho (RN15).

    valor_consulta e avaliacao estão no modelo do banco e ficam vazios
    neste cadastro. O preço da consulta é outra funcionalidade (RF23).
    """

    __tablename__ = "profissional_especialidade"
    __table_args__ = (
        UniqueConstraint(
            "id_profissional",
            "id_especialidade",
            name="uq_profissional_especialidade_par",
        ),
    )

    id_esp_prof: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_especialidade: Mapped[int] = mapped_column(
        ForeignKey("especialidade.id_especialidade", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    id_profissional: Mapped[int] = mapped_column(
        ForeignKey("profissional.id_profissional", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    id_conselho: Mapped[int] = mapped_column(
        ForeignKey("info_conselho.id_conselho", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    valor_consulta: Mapped[float | None] = mapped_column(Float, nullable=True)
    avaliacao: Mapped[float | None] = mapped_column(Float, nullable=True)

    profissional: Mapped[Profissional] = relationship("Profissional", back_populates="vinculos")
    especialidade: Mapped[Especialidade] = relationship("Especialidade", lazy="selectin")
    conselho: Mapped[InfoConselho] = relationship("InfoConselho", lazy="selectin")


from app.models.especialidade import Especialidade  # noqa: E402
from app.models.info_conselho import InfoConselho  # noqa: E402
from app.models.profissional import Profissional  # noqa: E402