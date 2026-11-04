"""Tabelas da Ouvidoria: manifestações abertas pelo site e seus anexos.

Ficam fora de models.py para não alterar as tabelas do grupo.
"""

import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database.connection import Base
from models.models import Usuario  # noqa: F401  (garante a tabela usuario no metadata)


class ManifestacaoOuvidoria(Base):
    """Reclamação, sugestão, elogio, dúvida ou problema em teleconsulta.

    Pode ser aberta sem login; se houver sessão válida, guarda o usuário.
    O protocolo é o número que a pessoa recebe para acompanhar a demanda.
    """

    __tablename__ = "manifestacao_ouvidoria"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    protocolo = Column(String(20), unique=True, nullable=False, index=True)
    solicitante = Column(String(20), nullable=False)  # paciente | profissional
    tipo = Column(String(20), nullable=False)  # reclamacao | teleconsulta | sugestao | elogio | duvida
    codigo_consulta = Column(String(20), nullable=True)
    assunto = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=False)
    aceite_lgpd = Column(Boolean, nullable=False)
    status = Column(String(20), nullable=False, default="aberta")
    id_usuario = Column(UUID(as_uuid=True), ForeignKey("usuario.id", ondelete="SET NULL"), nullable=True)
    criada_em = Column(DateTime(timezone=True), nullable=False)

    anexos = relationship(
        "AnexoOuvidoria",
        back_populates="manifestacao",
        cascade="all, delete-orphan",
    )


class AnexoOuvidoria(Base):
    """Arquivo (PDF, PNG ou JPEG) enviado junto com a manifestação."""

    __tablename__ = "anexo_ouvidoria"

    id = Column(Integer, primary_key=True, index=True)
    id_manifestacao = Column(
        UUID(as_uuid=True),
        ForeignKey("manifestacao_ouvidoria.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    nome_original = Column(String(255), nullable=False)
    caminho = Column(String(500), nullable=False)
    tipo_conteudo = Column(String(50), nullable=False)
    tamanho_bytes = Column(Integer, nullable=False)

    manifestacao = relationship("ManifestacaoOuvidoria", back_populates="anexos")
