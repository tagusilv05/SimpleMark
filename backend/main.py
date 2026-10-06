from fastapi import FastAPI

from database.connection import Base, engine
from models import models
from routers.porfissional_minha_conta import router as routers_porfissional_minha_conta
from routers.usuario_minha_conta import router as routers_usuario_minha_conta
from seed.seed import criar_seed

Base.metadata.create_all(bind=engine)

criar_seed()

app = FastAPI()

app.include_router(routers_porfissional_minha_conta, prefix="/profissionais", tags=["Profissionais"])
app.include_router(routers_usuario_minha_conta, prefix="/paciente", tags=["Paciente"])