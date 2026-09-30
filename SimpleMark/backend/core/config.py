# Configura a URL de conexão com o banco de dados usando variáveis de ambiente.
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL nao foi definida")