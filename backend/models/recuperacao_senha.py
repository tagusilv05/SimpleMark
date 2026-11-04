"""Código de recuperação de senha, enviado por e-mail a quem esqueceu a senha."""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from database.connection import Base
from models.models import Usuario  # noqa: F401  (garante a tabela usuario no metadata)


class CodigoRecuperacaoSenha(Base):
    """Código de 6 dígitos que autoriza trocar a senha da conta.

    Vale uma vez só e por poucos minutos. Guarda apenas o HMAC do código.
    Fica encerrado quando é usado, quando um código mais novo o substitui
    ou quando a conta é bloqueada por tentativas.
    """

    __tablename__ = "codigo_recuperacao_senha"
    __table_args__ = (
        # Um mesmo código nunca é gerado duas vezes para o mesmo usuário.
        UniqueConstraint("id_usuario", "codigo_hash", name="uq_codigo_recuperacao_usuario_hash"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    codigo_hash = Column(String(64), nullable=False)
    criado_em = Column(DateTime(timezone=True), nullable=False)
    expira_em = Column(DateTime(timezone=True), nullable=False)
    encerrado_em = Column(DateTime(timezone=True), nullable=True)