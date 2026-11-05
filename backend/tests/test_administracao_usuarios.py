"""Testes da listagem de usuários da administração (situação real da conta)."""

import pytest

from dependencies.autenticacao import administrador_atual
from models.models import Usuario
from routers.administracao import router as administracao_router


@pytest.fixture
def client_admin(app, client):
    """Cliente com as rotas da administração e um administrador logado."""
    app.include_router(administracao_router, prefix="/api/v1")
    app.dependency_overrides[administrador_atual] = lambda: None
    yield client
    app.dependency_overrides.pop(administrador_atual, None)


def test_lista_status_cpf_e_telefone(client_admin, db, cenario):
    pendente = db.get(Usuario, cenario["profissionais"][2].id_usuario)
    pendente.status = False
    db.commit()

    resposta = client_admin.get("/api/v1/administracao/usuarios/ids")

    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    status = {item["id_profissional"]: item["status"] for item in corpo["profissionais"]}
    assert status[cenario["profissionais"][1].id_profissional] == "ativo"
    assert status[cenario["profissionais"][2].id_profissional] == "pendente"
    paciente = corpo["pacientes"][0]
    assert paciente["status"] == "ativo"
    assert paciente["cpf"] == "000.000.0001"
    assert paciente["telefone"] == "(89) 99999-0001"
