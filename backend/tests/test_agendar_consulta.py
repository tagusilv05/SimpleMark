# Testes do agendamento de consulta pelo paciente (POST /consultas/agendar).
#
# O e-mail de confirmação roda como tarefa em segundo plano; aqui ele usa a
# sessão do teste e um SMTP falso, como nos testes da videochamada.
"""Testes do agendamento de consulta pelo paciente logado."""
from datetime import date, time, timedelta
from types import SimpleNamespace

import pytest

from dependencies.autenticacao import usuario_atual
from models.models import Consulta, DataHorario, Usuario
from services import videochamada
from tests.test_videochamada import _SessaoCompartilhada


@pytest.fixture
def integracoes(monkeypatch, db):
    """Troca sessão e envio de e-mail da videochamada por dublês."""
    monkeypatch.delenv("JITSI_BASE_URL", raising=False)
    dubles = SimpleNamespace(emails=[])
    monkeypatch.setattr(videochamada, "fabrica_sessao", lambda: _SessaoCompartilhada(db))
    monkeypatch.setattr(videochamada, "remetente_email", dubles.emails.append)
    monkeypatch.setattr(videochamada, "esperar", lambda _segundos: None)
    return dubles


@pytest.fixture
def paciente_logado(app, db, cenario):
    """Loga o paciente do cenário."""
    usuario = db.get(Usuario, cenario["paciente"].id_usuario)
    app.dependency_overrides[usuario_atual] = lambda: usuario
    yield usuario
    app.dependency_overrides.pop(usuario_atual, None)


@pytest.fixture
def horario(db, cenario):
    """Horário livre do profissional 1 daqui a 10 dias, às 14h."""
    item = DataHorario(
        id_esp_prof=cenario["consultas"][1].id_esp_prof,
        data_consulta=date.today() + timedelta(days=10),
        hora_inicio=time(14, 0),
        hora_fim=time(14, 30),
    )
    db.add(item)
    db.commit()
    return item


def test_agenda_consulta_no_horario_livre(client, db, paciente_logado, horario, integracoes):
    resposta = client.post("/consultas/agendar", json={"id_horario": horario.id_horario})

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["status"] == "agendada"
    assert corpo["data"] == horario.data_consulta.isoformat()
    assert corpo["hora"] == "14:00:00"
    assert float(corpo["valor"]) == 200.0
    assert corpo["profissional"]["nome"] == "Profissional 1"

    db.refresh(horario)
    assert horario.ocupado is True
    consulta = db.get(Consulta, corpo["id_consulta"])
    assert consulta.meet_link
    assert len(integracoes.emails) == 1


def test_horario_agendado_some_da_busca(client, paciente_logado, horario, integracoes):
    client.post("/consultas/agendar", json={"id_horario": horario.id_horario})

    busca = client.get("/api/v1/profissionais/busca").json()
    ids = [h["id_horario"] for ficha in busca for h in ficha["horarios_disponiveis"]]
    assert horario.id_horario not in ids


def test_nao_agenda_horario_ja_ocupado(client, paciente_logado, horario, integracoes):
    assert client.post("/consultas/agendar", json={"id_horario": horario.id_horario}).status_code == 201

    segunda = client.post("/consultas/agendar", json={"id_horario": horario.id_horario})
    assert segunda.status_code == 409


def test_nao_agenda_horario_que_ja_passou(client, db, cenario, paciente_logado, integracoes):
    passado = DataHorario(
        id_esp_prof=cenario["consultas"][1].id_esp_prof,
        data_consulta=date.today() - timedelta(days=1),
        hora_inicio=time(9, 0),
        hora_fim=time(9, 30),
    )
    db.add(passado)
    db.commit()

    resposta = client.post("/consultas/agendar", json={"id_horario": passado.id_horario})
    assert resposta.status_code == 409


def test_horario_inexistente(client, paciente_logado):
    assert client.post("/consultas/agendar", json={"id_horario": 999}).status_code == 404


def test_profissional_nao_pode_agendar(client, autenticar, horario):
    autenticar(1)
    resposta = client.post("/consultas/agendar", json={"id_horario": horario.id_horario})
    assert resposta.status_code == 403
