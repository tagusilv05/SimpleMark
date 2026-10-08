# Tabelas só da tela de administração. Ficam fora de models.py para não
# alterar as tabelas do grupo (usuario, profissional, paciente, etc.).
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database.connection import Base
from models.models import Administrador, Usuario


class Banimento(Base):
    """Registro de profissional ou paciente banido, sem mudar a coluna status deles."""

    __tablename__ = "banimento"

    id_banimento = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    id_administrador = Column(
        Integer,
        ForeignKey("administrador.id_administrador"),
        nullable=False,
    )
    motivo = Column(Text, nullable=True)
    banido_em = Column(DateTime(timezone=True), nullable=False)

    usuario = relationship(Usuario)
    administrador = relationship(Administrador)


class LogAcaoAdministrador(Base):
    """Histórico das ações do administrador (validar, banir, etc.)."""

    __tablename__ = "log_acao_administrador"

    id_log = Column(Integer, primary_key=True, index=True)
    id_administrador = Column(
        Integer,
        ForeignKey("administrador.id_administrador"),
        nullable=False,
        index=True,
    )
    acao = Column(String(80), nullable=False)
    alvo_tipo = Column(String(30), nullable=False)
    alvo_id = Column(Integer, nullable=False)
    id_usuario_alvo = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=True)
    detalhe = Column(Text, nullable=True)
    realizada_em = Column(DateTime(timezone=True), nullable=False)

    administrador = relationship(Administrador)
    usuario_alvo = relationship(Usuario)
