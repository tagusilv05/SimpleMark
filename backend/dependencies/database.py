"""Dependência que fornece a sessão do banco para cada requisição."""

from database.connection import SessionLocal


def get_db():
    """Abre uma sessão do banco e a fecha ao fim da requisição."""
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()