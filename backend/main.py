from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.connection import Base, engine
from database.migracoes import aplicar_migracoes
from models import models
import models.acesso  # registra credencial e sessao_login sem alterar as tabelas do grupo
import models.administracao  # registra banimento e logs da administração sem alterar as tabelas do grupo

from routers.horarios_profissional import router as horarios_profissional_router
from routers.administracao import router as administracao_router
from routers.auth import router as auth_router
from routers.cadastro import router as cadastro_router
from routers.consulta_profissional import router as consulta_profissional_router
from dependencies.erros import registrar_erros
from services.CadastroService.admin_inicial import criar_admin_inicial
from routers.porfissional_minha_conta import router as routers_porfissional_minha_conta
from routers.usuario_minha_conta import router as routers_usuario_minha_conta
from seed.seed import criar_seed

from routers.consulta_paciente import router as consulta_paciente_router

# from routers import avaliacao
from routers.avaliacao import router as avaliacao_router

Base.metadata.create_all(bind=engine)
aplicar_migracoes()
criar_admin_inicial()

criar_seed()

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
app.include_router(administracao_router, prefix="/api/v1")
app.include_router(consulta_profissional_router, prefix="/api/v1")


# app.include_router(avaliacao.router)
app.include_router(consulta_paciente_router)
app.include_router(avaliacao_router, prefix="/api/v1")


app.include_router(routers_porfissional_minha_conta, prefix="/profissionais", tags=["Profissionais"])
app.include_router(routers_usuario_minha_conta, prefix="/usuario", tags=["usuario"])

@app.get("/")
def home():
    return {"msg": "API funcionando!"}