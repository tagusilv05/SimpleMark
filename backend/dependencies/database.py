# Cria e fornece uma sessão do banco de dados para as requisições,
# garantindo que a sessão seja fechada após o uso.

from database.connection import SessionLocal


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()