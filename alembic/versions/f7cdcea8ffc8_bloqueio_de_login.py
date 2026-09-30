# Arquivo criado por Gustavo
"""Bloqueio temporário de login após tentativas inválidas (RNF15).

Acrescenta em usuario o contador de falhas e a data até a qual a conta fica bloqueada.

Revision ID: f7cdcea8ffc8
Revises: c4d8e1f02a33
Create Date: 2026-09-30 02:51:25.711721

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f7cdcea8ffc8'
down_revision: Union[str, Sequence[str], None] = 'c4d8e1f02a33'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('usuario', sa.Column('tentativas_login_falhas', sa.Integer(), server_default='0', nullable=False))
    op.add_column('usuario', sa.Column('bloqueado_ate', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('usuario', 'bloqueado_ate')
    op.drop_column('usuario', 'tentativas_login_falhas')
