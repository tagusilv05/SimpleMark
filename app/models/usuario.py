# Arquivo criado por Victor e Gustavo
from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Usuario(Base):
    """Pessoa cadastrada na plataforma.

    Campos do diagrama de classes e do modelo entidade-relacionamento:
    nome, cpf, orgao_emissor, data_nascimento, genero, telefone, email,
    senha_hash e status.

    O diagrama de entidade-relacionamento não desenhou a senha; o diagrama
    de classes traz senhaHash, e sem isso o login não existe.
    consentimento_lgpd registra o consentimento do cadastro.
    """

    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    cpf: Mapped[str] = mapped_column(String(11), unique=True, nullable=False)
    orgao_emissor: Mapped[str] = mapped_column(String(40), nullable=False)
    data_nascimento: Mapped[date] = mapped_column(Date, nullable=False)
    genero: Mapped[str] = mapped_column(String(30), nullable=False)
    telefone: Mapped[str] = mapped_column(String(11), nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(1024), nullable=False)
    status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    consentimento_lgpd: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Bloqueio por tentativas de login inválidas de acordo com o requisito nao funcional 15 que estabelecemos no inicio do projeto.
    # tentativas_login_falhas: quantas senhas erradas seguidas desde o último acerto.
    # bloqueado_ate: enquanto for uma data futura, a conta não consegue entrar.
    tentativas_login_falhas: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    bloqueado_ate: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    endereco: Mapped[Endereco | None] = relationship(
        "Endereco",
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    paciente: Mapped[Paciente | None] = relationship(
        "Paciente",
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    profissional: Mapped[Profissional | None] = relationship(
        "Profissional",
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    administrador: Mapped[Administrador | None] = relationship(
        "Administrador",
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )


from app.models.administrador import Administrador  # noqa: E402
from app.models.endereco import Endereco  # noqa: E402
from app.models.paciente import Paciente  # noqa: E402
from app.models.profissional import Profissional  # noqa: E402