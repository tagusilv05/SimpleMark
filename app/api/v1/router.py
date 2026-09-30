# Arquivo criado por Victor
from fastapi import APIRouter

from app.api.v1.endpoints import administracao, auth, cadastro

roteador = APIRouter()
roteador.include_router(cadastro.router)
roteador.include_router(auth.router)
roteador.include_router(administracao.router)
