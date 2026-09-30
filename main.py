# Arquivo criado por Victor
"""Ponto de entrada do uvicorn.

Passo a passo de `uvicorn main:app`:
1. O Python importa este arquivo.
2. A linha abaixo carrega app.main, que monta a API, o CORS e as rotas.
3. O uvicorn usa o objeto app para atender as requisições.
"""

from app.main import app

__all__ = ["app"]
