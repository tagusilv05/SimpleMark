# Campos de login que não existem na tabela usuario do grupo.
# A senha, o bloqueio e a sessão ficam aqui para não alterar as colunas deles.
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database.connection import Base
from models.models import Usuario


class Credencial(Base):
    """Senha e bloqueio de login de uma conta já existente em usuario."""

    __tablename__ = "credencial"

    id_usuario = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="CASCADE"),
        primary_key=True,
    )
    senha_hash = Column(String(1024), nullable=False)
    consentimento_lgpd = Column(Boolean, nullable=False, default=True)
    tentativas_login_falhas = Column(Integer, nullable=False, default=0)
    bloqueado_ate = Column(DateTime(timezone=True), nullable=True)

    usuario = relationship(Usuario)


class SessaoLogin(Base):
    """Sessão aberta no login. Expira por inatividade e pode ser encerrada no logout."""

    __tablename__ = "sessao_login"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    criada_em = Column(DateTime(timezone=True), nullable=False)
    ultima_atividade_em = Column(DateTime(timezone=True), nullable=False)
    encerrada_em = Column(DateTime(timezone=True), nullable=True)

    usuario = relationship(Usuario)


class CodigoLogin(Base):
    """Código de confirmação do login, enviado por e-mail depois da senha.

    Vale uma vez só e por poucos minutos. Guarda apenas o HMAC do código.
    Fica encerrado quando é usado, quando um código mais novo o substitui
    ou quando a conta é bloqueada por tentativas.
    """

    __tablename__ = "codigo_login"
    __table_args__ = (
        # Um mesmo código nunca é gerado duas vezes para o mesmo usuário.
        UniqueConstraint("id_usuario", "codigo_hash", name="uq_codigo_login_usuario_hash"),
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
