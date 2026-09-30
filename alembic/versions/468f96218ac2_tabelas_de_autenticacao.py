# Arquivo criado por Victor
"""tabelas de autenticacao

Revision ID: 468f96218ac2
Revises: 
Create Date: 2026-09-28 11:10:59.482742

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '468f96218ac2'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('especialidade',
    sa.Column('id_especialidade', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('especialidade', sa.String(length=80), nullable=False),
    sa.PrimaryKeyConstraint('id_especialidade', name=op.f('pk_especialidade')),
    sa.UniqueConstraint('especialidade', name=op.f('uq_especialidade_especialidade'))
    )
    op.create_table('info_conselho',
    sa.Column('id_conselho', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('numero_conselho', sa.String(length=30), nullable=False),
    sa.Column('orgao_conselho', sa.String(length=30), nullable=False),
    sa.PrimaryKeyConstraint('id_conselho', name=op.f('pk_info_conselho')),
    sa.UniqueConstraint('numero_conselho', 'orgao_conselho', name='uq_info_conselho_numero_orgao')
    )
    op.create_table('usuario',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('nome', sa.String(length=150), nullable=False),
    sa.Column('cpf', sa.String(length=11), nullable=False),
    sa.Column('orgao_emissor', sa.String(length=40), nullable=False),
    sa.Column('data_nascimento', sa.Date(), nullable=False),
    sa.Column('genero', sa.String(length=30), nullable=False),
    sa.Column('telefone', sa.String(length=11), nullable=False),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('senha_hash', sa.String(length=1024), nullable=False),
    sa.Column('status', sa.Boolean(), nullable=False),
    sa.Column('consentimento_lgpd', sa.Boolean(), nullable=False),
    sa.Column('tentativas_login', sa.Integer(), nullable=False),
    sa.Column('bloqueado_ate', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_usuario')),
    sa.UniqueConstraint('cpf', name=op.f('uq_usuario_cpf')),
    sa.UniqueConstraint('email', name=op.f('uq_usuario_email'))
    )
    op.create_table('administrador',
    sa.Column('id_administrador', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('id_usuario', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id_usuario'], ['usuario.id'], name=op.f('fk_administrador_id_usuario_usuario'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id_administrador', name=op.f('pk_administrador'))
    )
    op.create_index(op.f('ix_administrador_id_usuario'), 'administrador', ['id_usuario'], unique=True)
    op.create_table('endereco',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('id_usuario', sa.Integer(), nullable=False),
    sa.Column('cep', sa.String(length=8), nullable=False),
    sa.Column('municipio', sa.String(length=120), nullable=False),
    sa.Column('logradouro', sa.String(length=180), nullable=False),
    sa.Column('numero', sa.String(length=20), nullable=False),
    sa.Column('complemento', sa.String(length=120), nullable=True),
    sa.ForeignKeyConstraint(['id_usuario'], ['usuario.id'], name=op.f('fk_endereco_id_usuario_usuario'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_endereco'))
    )
    op.create_index(op.f('ix_endereco_id_usuario'), 'endereco', ['id_usuario'], unique=True)
    op.create_table('log_auditoria',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('id_usuario', sa.Integer(), nullable=True),
    sa.Column('acao', sa.String(length=40), nullable=False),
    sa.Column('data_hora', sa.DateTime(timezone=True), nullable=False),
    sa.Column('ip', sa.String(length=45), nullable=True),
    sa.ForeignKeyConstraint(['id_usuario'], ['usuario.id'], name=op.f('fk_log_auditoria_id_usuario_usuario'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_log_auditoria'))
    )
    op.create_index(op.f('ix_log_auditoria_id_usuario'), 'log_auditoria', ['id_usuario'], unique=False)
    op.create_table('paciente',
    sa.Column('id_paciente', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('id_usuario', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id_usuario'], ['usuario.id'], name=op.f('fk_paciente_id_usuario_usuario'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id_paciente', name=op.f('pk_paciente'))
    )
    op.create_index(op.f('ix_paciente_id_usuario'), 'paciente', ['id_usuario'], unique=True)
    op.create_table('profissional',
    sa.Column('id_profissional', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('id_usuario', sa.Integer(), nullable=False),
    sa.Column('info_profissional', sa.Text(), nullable=False),
    sa.Column('registro_validado', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['id_usuario'], ['usuario.id'], name=op.f('fk_profissional_id_usuario_usuario'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id_profissional', name=op.f('pk_profissional'))
    )
    op.create_index(op.f('ix_profissional_id_usuario'), 'profissional', ['id_usuario'], unique=True)
    op.create_table('sessao',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('id_usuario', sa.Integer(), nullable=False),
    sa.Column('ultimo_acesso', sa.DateTime(timezone=True), nullable=False),
    sa.Column('expira_em', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['id_usuario'], ['usuario.id'], name=op.f('fk_sessao_id_usuario_usuario'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_sessao'))
    )
    op.create_index(op.f('ix_sessao_id_usuario'), 'sessao', ['id_usuario'], unique=False)
    op.create_table('token_recuperacao_senha',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('id_usuario', sa.Integer(), nullable=False),
    sa.Column('token_hash', sa.String(length=64), nullable=False),
    sa.Column('expira_em', sa.DateTime(timezone=True), nullable=False),
    sa.Column('utilizado', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['id_usuario'], ['usuario.id'], name=op.f('fk_token_recuperacao_senha_id_usuario_usuario'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_token_recuperacao_senha')),
    sa.UniqueConstraint('token_hash', name=op.f('uq_token_recuperacao_senha_token_hash'))
    )
    op.create_index(op.f('ix_token_recuperacao_senha_id_usuario'), 'token_recuperacao_senha', ['id_usuario'], unique=False)
    op.create_table('profissional_especialidade',
    sa.Column('id_esp_prof', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('id_especialidade', sa.Integer(), nullable=False),
    sa.Column('id_profissional', sa.Integer(), nullable=False),
    sa.Column('id_conselho', sa.Integer(), nullable=False),
    sa.Column('valor_consulta', sa.Float(), nullable=True),
    sa.Column('avaliacao', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['id_conselho'], ['info_conselho.id_conselho'], name=op.f('fk_profissional_especialidade_id_conselho_info_conselho'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['id_especialidade'], ['especialidade.id_especialidade'], name=op.f('fk_profissional_especialidade_id_especialidade_especialidade'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['id_profissional'], ['profissional.id_profissional'], name=op.f('fk_profissional_especialidade_id_profissional_profissional'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id_esp_prof', name=op.f('pk_profissional_especialidade')),
    sa.UniqueConstraint('id_profissional', 'id_especialidade', name='uq_profissional_especialidade_par')
    )
    op.create_index(op.f('ix_profissional_especialidade_id_conselho'), 'profissional_especialidade', ['id_conselho'], unique=False)
    op.create_index(op.f('ix_profissional_especialidade_id_especialidade'), 'profissional_especialidade', ['id_especialidade'], unique=False)
    op.create_index(op.f('ix_profissional_especialidade_id_profissional'), 'profissional_especialidade', ['id_profissional'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_profissional_especialidade_id_profissional'), table_name='profissional_especialidade')
    op.drop_index(op.f('ix_profissional_especialidade_id_especialidade'), table_name='profissional_especialidade')
    op.drop_index(op.f('ix_profissional_especialidade_id_conselho'), table_name='profissional_especialidade')
    op.drop_table('profissional_especialidade')
    op.drop_index(op.f('ix_token_recuperacao_senha_id_usuario'), table_name='token_recuperacao_senha')
    op.drop_table('token_recuperacao_senha')
    op.drop_index(op.f('ix_sessao_id_usuario'), table_name='sessao')
    op.drop_table('sessao')
    op.drop_index(op.f('ix_profissional_id_usuario'), table_name='profissional')
    op.drop_table('profissional')
    op.drop_index(op.f('ix_paciente_id_usuario'), table_name='paciente')
    op.drop_table('paciente')
    op.drop_index(op.f('ix_log_auditoria_id_usuario'), table_name='log_auditoria')
    op.drop_table('log_auditoria')
    op.drop_index(op.f('ix_endereco_id_usuario'), table_name='endereco')
    op.drop_table('endereco')
    op.drop_index(op.f('ix_administrador_id_usuario'), table_name='administrador')
    op.drop_table('administrador')
    op.drop_table('usuario')
    op.drop_table('info_conselho')
    op.drop_table('especialidade')
