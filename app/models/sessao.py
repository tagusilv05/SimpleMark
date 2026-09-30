# Arquivo criado por Gustavo
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Sessao(Base):
    """Sessão de login (RNF14). Cada login cria uma linha, e o token aponta para ela.

    ultima_atividade_em: atualizada quando a conta usa a API. Passadas 24h sem uso,
    a sessão vale como expirada e é preciso entrar de novo.
    encerrada_em: preenchida quando a pessoa sai (logout). Sessão encerrada nunca volta a valer.
    """

    __tablename__ = "sessao"

    # O id vai dentro do token (campo sid). É um UUID aleatório, impossível de adivinhar.
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuario.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    criada_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    ultima_atividade_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    encerrada_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
