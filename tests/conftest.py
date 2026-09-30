# Arquivo criado por Victor
import os

os.environ["SECRET_KEY"] = "chave-de-teste-simple-mark-com-folga"
os.environ["AMBIENTE"] = "teste"
os.environ["DATABASE_URL"] = "sqlite://"

from dataclasses import dataclass
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import database
from app.core.security import gerar_hash_senha
from app.main import app
from app.models.administrador import Administrador
from app.models.base import Base
from app.models.endereco import Endereco
from app.models.usuario import Usuario
from tests.apoio import CPF_ADMIN, SENHA, dados_usuario


@dataclass
class AmbienteTeste:
    cliente: TestClient
    sessoes: sessionmaker


@pytest.fixture
def ambiente():
    """Monta um banco SQLite só na memória para um teste e derruba no fim.

    Passo a passo:
    1. Cria as tabelas no SQLite, sem usar o PostgreSQL.
    2. Troca a sessão da API por essa fábrica.
    3. Entrega o cliente HTTP do teste.
    4. Depois do teste, apaga as tabelas.
    """
    motor = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    fabrica = sessionmaker(bind=motor, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(motor)
    original = database.SessionLocal
    database.SessionLocal = fabrica
    with TestClient(app) as cliente:
        yield AmbienteTeste(cliente=cliente, sessoes=fabrica)
    database.SessionLocal = original
    Base.metadata.drop_all(motor)
    motor.dispose()


def autorizar(token: str) -> dict[str, str]:
    """Monta o cabeçalho Authorization no formato Bearer."""
    return {"Authorization": f"Bearer {token}"}


def entrar(ambiente: AmbienteTeste, identificador: str, senha: str = SENHA) -> dict:
    """Faz login e devolve o JSON do token.

    Passo a passo:
    1. Envia identificador e senha para /api/v1/auth/login.
    2. Exige status 200. Se falhar, o teste para mostrando o JSON.
    3. Devolve o corpo, com access_token e o usuário.
    """
    resposta = ambiente.cliente.post(
        "/api/v1/auth/login",
        json={"identificador": identificador, "senha": senha},
    )
    assert resposta.status_code == 200, resposta.json()
    return resposta.json()


def gravar_administrador(ambiente: AmbienteTeste, email: str = "admin@example.com") -> None:
    """Insere o administrador direto no banco, como no sistema real.

    Passo a passo:
    1. Monta o usuário com CPF, e-mail e hash da senha.
    2. Liga o endereço e a linha da tabela administrador.
    3. Confirma a gravação. Não existe rota de cadastro para este perfil.
    """
    dados = dados_usuario(
        nome="Helena Duarte",
        email=email,
        cpf=CPF_ADMIN,
        telefone="86955554444",
    )
    db = ambiente.sessoes()
    try:
        usuario = Usuario(
            nome=dados["nome"],
            cpf=dados["cpf"],
            orgao_emissor=dados["orgao_emissor"],
            data_nascimento=date.fromisoformat(dados["data_nascimento"]),
            genero=dados["genero"],
            telefone=dados["telefone"],
            email=dados["email"],
            senha_hash=gerar_hash_senha(SENHA),
            status=True,
            consentimento_lgpd=True,
        )
        usuario.endereco = Endereco(
            cep="64000000",
            endereco=dados["endereco"],
        )
        usuario.administrador = Administrador()
        db.add(usuario)
        db.commit()
    finally:
        db.close()
