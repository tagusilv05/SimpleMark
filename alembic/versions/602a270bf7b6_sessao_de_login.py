# Arquivo criado por Gustavo
"""Sessão de login com expiração por inatividade (RNF14).

Cria a tabela sessao. Cada login grava uma linha, e o token aponta para ela.

Revision ID: 602a270bf7b6
Revises: f7cdcea8ffc8
Create Date: 2026-09-30 06:47:47.624976

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '602a270bf7b6'
down_revision: Union[str, Sequence[str], None] = 'f7cdcea8ffc8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('sessao',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('id_usuario', sa.Integer(), nullable=False),
    sa.Column('criada_em', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('ultima_atividade_em', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('encerrada_em', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['id_usuario'], ['usuario.id'], name=op.f('fk_sessao_id_usuario_usuario'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_sessao'))
    )
    op.create_index(op.f('ix_sessao_id_usuario'), 'sessao', ['id_usuario'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_sessao_id_usuario'), table_name='sessao')
    op.drop_table('sessao')
