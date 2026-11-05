# Testes de POST /api/v1/avaliacoes/consultas/{id}/avaliacao (tela "Avaliar consulta").
"""O paciente avalia a consulta realizada com estrelas e/ou comentário."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from dependencies.autenticacao import paciente_atual
from dependencies.database import get_db
from dependencies.erros import registrar_erros
from routers.avaliacao import router as avaliacao_router


@pytest.fixture
def cliente_paciente(db, cenario):
    """App só com o router de avaliação e o paciente do cenário logado."""
    app = FastAPI()
    registrar_erros(app)
    app.include_router(avaliacao_router, prefix="/api/v1")
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[paciente_atual] = lambda: cenario["paciente"]
    return TestClient(app)


def _url(consulta):
    return f"/api/v1/avaliacoes/consultas/{consulta.id_consulta}/avaliacao"


def test_avalia_com_estrelas_e_comentario(cliente_paciente, cenario):
    """Corpo enviado pela tela: nota de 1 a 5 e comentário."""
    consulta = cenario["consultas"][1]

    resposta = cliente_paciente.post(_url(consulta), json={"nota": 5, "feedback": "Ótimo atendimento."})

    assert resposta.status_code == 201, resposta.text
    assert resposta.json()["nota"] == 5
    assert cliente_paciente.get(_url(consulta)).json()["feedback"] == "Ótimo atendimento."


def test_avalia_sem_comentario(cliente_paciente, cenario):
    """Comentário vazio vira null e a avaliação vale só pelas estrelas."""
    resposta = cliente_paciente.post(_url(cenario["consultas"][1]), json={"nota": 4, "feedback": None})
    assert resposta.status_code == 201, resposta.text


def test_nao_avalia_duas_vezes(cliente_paciente, cenario):
    """A segunda avaliação da mesma consulta responde 409."""
    consulta = cenario["consultas"][1]
    assert cliente_paciente.post(_url(consulta), json={"nota": 5}).status_code == 201
    assert cliente_paciente.post(_url(consulta), json={"nota": 3}).status_code == 409


def test_avalia_so_com_comentario(cliente_paciente, cenario):
    """Sem estrelas também vale (o backend aceita só o comentário)."""
    resposta = cliente_paciente.post(_url(cenario["consultas"][1]), json={"feedback": "Consulta tranquila."})
    assert resposta.status_code == 201, resposta.text
    assert resposta.json()["nota"] is None


def test_media_do_profissional_usa_a_nota(cliente_paciente, cenario):
    """A média exibida em "Meus agendamentos" reflete a nota recém-enviada."""
    consulta = cenario["consultas"][1]
    cliente_paciente.post(_url(consulta), json={"nota": 4})
    id_profissional = cenario["profissionais"][1].id_profissional

    media = cliente_paciente.get(f"/api/v1/avaliacoes/profissionais/{id_profissional}/media").json()

    assert media["total"] == 1
    assert media["media"] == 4
