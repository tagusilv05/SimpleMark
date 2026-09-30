# Criado por: Victor Rodrigues Luz
"""Arquivo de inicialização da API Simple Mark.

Este módulo configura o servidor FastAPI, middlewares de CORS,
logs do sistema e registra as rotas principais.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models  # noqa: F401
from app.api.erros import registrar_erros
from app.api.v1.router import roteador
from app.core.config import settings
from app.services.admin_inicial import criar_admin_inicial

# Configuração do logging - Aqui mostro mensagens de erro e sucesso na API.
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def ciclo_de_vida(_app: FastAPI):
    """Roda na subida e na parada do uvicorn.

    Passo a passo:
    1. Antes de aceitar requisição, garante a administradora Helena no banco.
    2. O yield libera a API para atender.
    3. Depois do yield, o processo está encerrando.
    """
    criar_admin_inicial()
    yield


# Configuração da API - Criei a API com o FastAPI e defini o nome, descrição e versão
app = FastAPI(
    title="Simple Mark",
    description=(
        "Cadastro de paciente e de profissional de saúde, "
        "login e autenticação de paciente, profissional de saúde e administrador. "
        "O profissional de saúde só entra depois que o administrador valida o cadastro. "
        "A administradora inicial é inserida no banco na subida da API."
    ),
    version="0.1.0",
    lifespan=ciclo_de_vida,
)

# Configuração do CORS, que serve para permitir que a API seja acessada por outros domínios (ex: frontend).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.lista_cors,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# allow_origins lista de domínios autorizados (vinda da config).
# allow_credentials=True permite cookies/Authorization header entre origens.
# allow_methods=["*"] aceita GET, POST, PUT, DELETE, PATCH, OPTIONS.
# allow_headers=["*"] aceita qualquer cabeçalho (ex.: Authorization).


# Registro de erros - Aqui registro os erros da API.
registrar_erros(app)
# Inclusão do roteador - É onde fica tudo que estiver dentro do arquivo router.py (ex: rotas de login, cadastro, etc.)
app.include_router(roteador, prefix="/api/v1")

# Rota raiz - Aqui defino a rota raiz da API.
@app.get("/", tags=["Sistema"], summary="Situação da API")
def raiz() -> dict[str, str]:
    """Responde na raiz para mostrar que o processo está no ar.

    Passo a passo:
    1. Não consulta o banco.
    2. Devolve um JSON curto. Quem testa a API vê 200 antes de cadastrar alguém.
    """
    return {"mensagem": "API Simple Mark em execução"}
