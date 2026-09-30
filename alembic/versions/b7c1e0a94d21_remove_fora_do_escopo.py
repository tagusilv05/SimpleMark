# Arquivo criado por Victor
"""Remove o que não faz parte do cadastro, do login e da autenticação.

Revision ID: b7c1e0a94d21
Revises: 468f96218ac2
Create Date: 2026-09-28 22:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7c1e0a94d21"
down_revision: Union[str, Sequence[str], None] = "468f96218ac2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index(op.f("ix_token_recuperacao_senha_id_usuario"), table_name="token_recuperacao_senha")
    op.drop_table("token_recuperacao_senha")
    op.drop_index(op.f("ix_sessao_id_usuario"), table_name="sessao")
    op.drop_table("sessao")
    op.drop_index(op.f("ix_log_auditoria_id_usuario"), table_name="log_auditoria")
    op.drop_table("log_auditoria")
    op.drop_column("usuario", "tentativas_login")
    op.drop_column("usuario", "bloqueado_ate")
    op.drop_column("profissional", "registro_validado")


def downgrade() -> None:
    op.add_column("profissional", sa.Column("registro_validado", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.alter_column("profissional", "registro_validado", server_default=None)
    op.add_column("usuario", sa.Column("bloqueado_ate", sa.DateTime(timezone=True), nullable=True))
    op.add_column("usuario", sa.Column("tentativas_login", sa.Integer(), nullable=False, server_default="0"))
    op.alter_column("usuario", "tentativas_login", server_default=None)
    op.create_table(
        "log_auditoria",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_usuario", sa.Integer(), nullable=True),
        sa.Column("acao", sa.String(length=40), nullable=False),
        sa.Column("data_hora", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ip", sa.String(length=45), nullable=True),
        sa.ForeignKeyConstraint(["id_usuario"], ["usuario.id"], name=op.f("fk_log_auditoria_id_usuario_usuario"), ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_log_auditoria")),
    )
    op.create_index(op.f("ix_log_auditoria_id_usuario"), "log_auditoria", ["id_usuario"], unique=False)
    op.create_table(
        "sessao",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_usuario", sa.Integer(), nullable=False),
        sa.Column("ultimo_acesso", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expira_em", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["id_usuario"], ["usuario.id"], name=op.f("fk_sessao_id_usuario_usuario"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sessao")),
    )
    op.create_index(op.f("ix_sessao_id_usuario"), "sessao", ["id_usuario"], unique=False)
    op.create_table(
        "token_recuperacao_senha",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_usuario", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expira_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("utilizado", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["id_usuario"], ["usuario.id"], name=op.f("fk_token_recuperacao_senha_id_usuario_usuario"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_token_recuperacao_senha")),
        sa.UniqueConstraint("token_hash", name=op.f("uq_token_recuperacao_senha_token_hash")),
    )
    op.create_index(op.f("ix_token_recuperacao_senha_id_usuario"), "token_recuperacao_senha", ["id_usuario"], unique=False)
