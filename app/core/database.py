# Arquivo criado por Victor
"""Conexão com o PostgreSQL e a sessão usada em cada requisição."""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# O engine não conecta na importação. A conexão abre na primeira consulta.
# No PostgreSQL, connect_timeout corta a espera quando o banco está desligado.
_argumentos_conexao = {}
if settings.database_url.startswith("postgresql"):
    _argumentos_conexao["connect_timeout"] = 5

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args=_argumentos_conexao,
)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db() -> Iterator[Session]:
    """Abre uma sessão do banco para uma requisição e fecha no fim.

    Passo a passo:
    1. Abre uma sessão ligada ao PostgreSQL configurado em DATABASE_URL.
    2. Entrega essa sessão para a rota e para os services (o yield pausa aqui).
    3. Se a rota terminar sem erro, confirma o que ainda não foi commitado.
    4. Se der erro, desfaz só o que ainda não foi confirmado. Um commit feito
       dentro do service permanece.
    5. Fecha a sessão nos dois casos.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
