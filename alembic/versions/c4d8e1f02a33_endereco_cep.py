# Arquivo criado por Victor
"""Deixa o endereço só com CEP e o texto do endereço.

Revision ID: c4d8e1f02a33
Revises: b7c1e0a94d21
Create Date: 2026-09-28 23:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4d8e1f02a33"
down_revision: Union[str, Sequence[str], None] = "b7c1e0a94d21"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("endereco", sa.Column("endereco", sa.String(length=200), nullable=True))
    op.execute(
        """
        UPDATE endereco
        SET endereco = left(trim(both ' ' FROM concat_ws(', ',
            nullif(logradouro, ''),
            nullif(numero, ''),
            nullif(complemento, ''),
            nullif(municipio, '')
        )), 200)
        """
    )
    op.alter_column("endereco", "endereco", nullable=False)
    op.drop_column("endereco", "complemento")
    op.drop_column("endereco", "numero")
    op.drop_column("endereco", "logradouro")
    op.drop_column("endereco", "municipio")


def downgrade() -> None:
    op.add_column("endereco", sa.Column("municipio", sa.String(length=120), nullable=False, server_default=""))
    op.add_column("endereco", sa.Column("logradouro", sa.String(length=180), nullable=False, server_default=""))
    op.add_column("endereco", sa.Column("numero", sa.String(length=20), nullable=False, server_default=""))
    op.add_column("endereco", sa.Column("complemento", sa.String(length=120), nullable=True))
    op.execute("UPDATE endereco SET logradouro = endereco")
    op.alter_column("endereco", "municipio", server_default=None)
    op.alter_column("endereco", "logradouro", server_default=None)
    op.alter_column("endereco", "numero", server_default=None)
    op.drop_column("endereco", "endereco")
