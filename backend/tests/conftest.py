# Base dos testes do QR-Code do documento clínico.
#
# Os testes não importam o main.py: lá o create_all, o admin inicial e o seed
# rodam no import e exigem o PostgreSQL de verdade. Aqui subimos um app enxuto,
# só com o router do QR-Code e o handler de erro do projeto, sobre um SQLite
# em memória.
import os
import uuid
from datetime import date, time

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("BASE_URL_VALIDACAO", "https://simplemark.test/api/v1")

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database.connection import Base
from dependencies.autenticacao import usuario_atual
from dependencies.database import get_db
from dependencies.erros import registrar_erros
from models.models import (
    Consulta,
    DocumentoClinico,
    Especialidade,
    InfoConselho,
    Paciente,
    Profissional,
    ProfissionalEspecialidade,
    Usuario,
)
from routers.busca_profissional import router as busca_profissional_router
from routers.documento_qrcode import router as documento_qrcode_router
from routers.documento_emissao import router as documento_emissao_router
from routers.documento_validacao import router as documento_validacao_router


@pytest.fixture
def engine():
    motor = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # O driver do SQLite abre transação por conta própria e isso quebra o
    # SAVEPOINT usado no retry. Workaround recomendado pelo SQLAlchemy.
    @event.listens_for(motor, "connect")
    def _sem_begin_implicito(conexao_dbapi, _registro):
        conexao_dbapi.isolation_level = None

    @event.listens_for(motor, "begin")
    def _begin_explicito(conexao):
        conexao.exec_driver_sql("BEGIN")

    Base.metadata.create_all(bind=motor)
    yield motor
    motor.dispose()


@pytest.fixture
def db(engine):
    Sessao = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    sessao = Sessao()
    try:
        yield sessao
    finally:
        sessao.close()


@pytest.fixture
def app(db):
    aplicacao = FastAPI()
    registrar_erros(aplicacao)
    aplicacao.include_router(busca_profissional_router, prefix="/api/v1")
    aplicacao.include_router(documento_qrcode_router, prefix="/api/v1")
    aplicacao.include_router(documento_validacao_router, prefix="/api/v1")
    aplicacao.include_router(documento_emissao_router, prefix="/api/v1")
    aplicacao.dependency_overrides[get_db] = lambda: db
    return aplicacao


@pytest.fixture
def client(app):
    return TestClient(app)


def _criar_profissional(db, sufixo: int) -> Profissional:
    usuario = Usuario(
        id=uuid.uuid4(),
        nome=f"Profissional {sufixo}",
        cpf=f"111.111.11{sufixo:02d}",
        orgao_emissor="SSP-PI",
        data_nascimento=date(1980, 1, 15),
        genero="Não informado",
        telefone=f"(89) 98888-{sufixo:04d}",
        email=f"profissional{sufixo}@email.com",
        status=True,
    )
    db.add(usuario)
    db.flush()

    profissional = Profissional(id_usuario=usuario.id)
    db.add(profissional)
    db.flush()
    return profissional


@pytest.fixture
def cenario(db):
    """Dois profissionais, um paciente e uma consulta de cada profissional."""
    especialidade = Especialidade(especialidade="Cardiologia")
    db.add(especialidade)
    conselho = InfoConselho(numero_conselho="12345", orgao_conselho="CRM-PI")
    db.add(conselho)
    db.flush()

    usuario_paciente = Usuario(
        id=uuid.uuid4(),
        nome="Paciente 1",
        cpf="000.000.0001",
        orgao_emissor="SSP-PI",
        data_nascimento=date(1990, 1, 10),
        genero="Não informado",
        telefone="(89) 99999-0001",
        email="paciente1@email.com",
        status=True,
    )
    db.add(usuario_paciente)
    db.flush()

    paciente = Paciente(id_usuario=usuario_paciente.id)
    db.add(paciente)
    db.flush()

    dados = {"paciente": paciente, "consultas": {}, "profissionais": {}}

    for sufixo in (1, 2):
        profissional = _criar_profissional(db, sufixo)
        esp_prof = ProfissionalEspecialidade(
            id_profissional=profissional.id_profissional,
            id_especialidade=especialidade.id_especialidade,
            id_conselho=conselho.id_conselho,
            valor_consulta=200.0,
        )
        db.add(esp_prof)
        db.flush()

        consulta = Consulta(
            id_paciente=paciente.id_paciente,
            id_esp_prof=esp_prof.id_esp_prof,
            data=date(2026, 1, 20),
            hora=time(10, 0),
            tipo="online",
            status="realizada",
            valor=200.00,
        )
        db.add(consulta)
        db.flush()

        dados["profissionais"][sufixo] = profissional
        dados["consultas"][sufixo] = consulta

    db.commit()
    return dados


@pytest.fixture
def criar_documento(db, cenario):
    def _criar(dono: int = 1, tipo: bool = True) -> DocumentoClinico:
        documento = DocumentoClinico(
            id_consulta=cenario["consultas"][dono].id_consulta,
            observacoes="Receita do paciente.",
            tipo=tipo,
        )
        db.add(documento)
        db.commit()
        db.refresh(documento)
        return documento

    return _criar


@pytest.fixture
def autenticar(app, db, cenario):
    """Simula o profissional logado trocando a dependência real de sessão."""

    def _autenticar(sufixo: int):
        profissional = cenario["profissionais"][sufixo]
        usuario = db.get(Usuario, profissional.id_usuario)
        app.dependency_overrides[usuario_atual] = lambda: usuario
        return usuario

    yield _autenticar
    app.dependency_overrides.pop(usuario_atual, None)
