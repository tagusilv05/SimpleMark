# Campos de login que não existem na tabela usuario do grupo.
# A senha, o bloqueio e a sessão ficam aqui para não alterar as colunas deles.
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
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


class CodigoRecuperacao(Base):
    """Código de 6 caracteres enviado por e-mail para redefinir a senha.

    O código e o token de redefinição ficam gravados só como hash.
    encerrado_em preenchido significa que o registro não serve mais para nada:
    foi usado, substituído por um código novo ou esgotou as tentativas.
    """

    __tablename__ = "codigo_recuperacao"

    id = Column(Integer, primary_key=True)
    id_usuario = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    codigo_hash = Column(String(64), nullable=False, index=True)
    criado_em = Column(DateTime(timezone=True), nullable=False)
    expira_em = Column(DateTime(timezone=True), nullable=False)
    tentativas = Column(Integer, nullable=False, default=0)
    verificado_em = Column(DateTime(timezone=True), nullable=True)
    token_hash = Column(String(64), nullable=True, unique=True)
    redefinir_ate = Column(DateTime(timezone=True), nullable=True)
    encerrado_em = Column(DateTime(timezone=True), nullable=True)
