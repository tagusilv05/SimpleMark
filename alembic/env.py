# Arquivo criado por Victor
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

import app.models  # noqa: F401
from app.core.config import settings
from app.models.base import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.database_url.replace("%", "%%"))
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Gera o SQL da migration sem abrir conexão.

    Passo a passo:
    1. Lê a URL já colocada a partir do DATABASE_URL.
    2. Configura o contexto com os modelos atuais.
    3. Escreve os comandos SQL. Não executa no PostgreSQL.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Aplica a migration no banco configurado em DATABASE_URL.

    Passo a passo:
    1. Cria um engine só para esta execução, sem pool reaproveitado.
    2. Abre a conexão.
    3. Compara a versão gravada em alembic_version com os arquivos de versions.
    4. Roda o upgrade que ainda falta e confirma a transação.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args={"connect_timeout": 5} if settings.database_url.startswith("postgresql") else {},
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
