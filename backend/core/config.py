"""URL de conexão com o banco, lida das variáveis de ambiente (.env).

Levanta ValueError na importação se DATABASE_URL não estiver definida.
"""

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL nao foi definida")
