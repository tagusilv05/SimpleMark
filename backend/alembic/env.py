"""Ambiente do Alembic: conecta com o usuário DONO do esquema e aponta os modelos.

As migrações usam MIGRATION_DATABASE_URL (usuário com permissão de criar e alterar
tabelas). A API usa DATABASE_URL, com um usuário que só lê e grava dados.
"""

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool, text

URL_MIGRACAO = os.getenv("MIGRATION_DATABASE_URL") or os.getenv("DATABASE_URL")
if not URL_MIGRACAO:
    raise RuntimeError("Defina MIGRATION_DATABASE_URL (ou DATABASE_URL) para rodar as migrações.")
# core.config exige DATABASE_URL na importação dos modelos.
os.environ.setdefault("DATABASE_URL", URL_MIGRACAO)

from database.connection import Base  # noqa: E402
import models.models  # noqa: E402,F401
import models.acesso  # noqa: E402,F401
import models.administracao  # noqa: E402,F401
import models.ouvidoria  # noqa: E402,F401
import models.recuperacao_senha  # noqa: E402,F401

config = context.config
config.set_main_option("sqlalchemy.url", URL_MIGRACAO.replace("%", "%%"))
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Gera o SQL das migrações sem conectar ao banco (``alembic upgrade head --sql``)."""
    context.configure(
        url=URL_MIGRACAO,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Aplica as migrações conectando ao banco."""
    conectavel = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with conectavel.connect() as conexao:
        context.configure(connection=conexao, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()
            _proteger_tabela_de_versao(conexao)


def _proteger_tabela_de_versao(conexao) -> None:
    """Só o dono do esquema mexe em alembic_version.

    As permissões padrão (banco/sql/usuario_app.sql) liberam toda tabela nova para o
    usuário da API, inclusive esta; aqui elas são retiradas.
    """
    if conexao.dialect.name != "postgresql":
        return
    conexao.execute(text(
        """
        DO $$
        DECLARE r record;
        BEGIN
            FOR r IN SELECT DISTINCT grantee FROM information_schema.role_table_grants
                     WHERE table_schema = 'public' AND table_name = 'alembic_version'
                       AND grantee <> current_user
            LOOP
                EXECUTE format('REVOKE ALL ON public.alembic_version FROM %I', r.grantee);
            END LOOP;
        END $$;
        """
    ))


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
