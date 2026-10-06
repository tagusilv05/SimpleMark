from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.connection import Base, engine
from models import models
import models.acesso  # registra credencial e sessao_login sem alterar as tabelas do grupo

from routers.horarios_profissional import router as horarios_profissional_router
from routers.administracao import router as administracao_router
from routers.auth import router as auth_router
from routers.cadastro import router as cadastro_router
from routers.consulta_profissional import router as consulta_profissional_router
from routers.recuperacao_senha import router as recuperacao_senha_router
from dependencies.erros import registrar_erros
from services.CadastroService.admin_inicial import criar_admin_inicial

Base.metadata.create_all(bind=engine)
criar_admin_inicial()

app = FastAPI()

registrar_erros(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(horarios_profissional_router)
app.include_router(cadastro_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(recuperacao_senha_router, prefix="/api/v1")
app.include_router(administracao_router, prefix="/api/v1")
app.include_router(consulta_profissional_router, prefix="/api/v1")

@app.get("/")
def home():
    return {"msg": "API funcionando!"}
