"""Testes do pagamento da consulta (rotas /api/v1/pagamento), com o Mercado Pago simulado."""

from datetime import date, time, timedelta

import pytest

from dependencies.autenticacao import usuario_atual
from models.models import Consulta, Pagamento, Usuario
from routers.pagamento import router as pagamento_router
from services.PagamentoService import pagamento as servico


@pytest.fixture
def client_pagamento(app, client):
    """Cliente com as rotas de pagamento registradas."""
    app.include_router(pagamento_router, prefix="/api/v1")
    return client


@pytest.fixture
def paciente_logado(app, db, cenario):
    """Loga o paciente do cenário."""
    usuario = db.get(Usuario, cenario["paciente"].id_usuario)
    app.dependency_overrides[usuario_atual] = lambda: usuario
    yield usuario
    app.dependency_overrides.pop(usuario_atual, None)


@pytest.fixture
def consulta_futura(db, cenario):
    """Consulta agendada do paciente daqui a 5 dias."""
    base = cenario["consultas"][1]
    consulta = Consulta(
        id_paciente=base.id_paciente,
        id_esp_prof=base.id_esp_prof,
        data=date.today() + timedelta(days=5),
        hora=time(9, 0),
        tipo="consulta",
        status="agendada",
        valor=180.00,
    )
    db.add(consulta)
    db.commit()
    return consulta


@pytest.fixture
def mercado_pago(monkeypatch):
    """Substitui as chamadas HTTP ao Mercado Pago e guarda o que foi enviado."""
    estado = {"preferencias": [], "pagamentos": {}, "busca": []}

    def criar_preferencia(dados):
        estado["preferencias"].append(dados)
        return {"id": "pref-1", "init_point": "https://mp.test/checkout", "sandbox_init_point": None}

    monkeypatch.setattr(servico, "criar_preferencia", criar_preferencia)
    monkeypatch.setattr(servico, "obter_pagamento", lambda id_mp: estado["pagamentos"][str(id_mp)])
    monkeypatch.setattr(servico, "buscar_pagamentos", lambda _ref: {"results": estado["busca"]})
    return estado


def _pagamento_mp(id_mp, id_consulta, status, tipo="bank_transfer"):
    return {"id": id_mp, "external_reference": str(id_consulta), "status": status, "payment_type_id": tipo}


@pytest.mark.parametrize(
    ("metodo", "aceito", "parcelas"),
    [("pix", "bank_transfer", 1), ("cartao", "credit_card", 10), ("boleto", "ticket", 1)],
)
def test_preferencia_aceita_somente_o_metodo_escolhido(
    client_pagamento, db, paciente_logado, consulta_futura, mercado_pago, metodo, aceito, parcelas
):
    resposta = client_pagamento.post(
        "/api/v1/pagamento/preferencia", json={"id_consulta": consulta_futura.id_consulta, "metodo": metodo}
    )

    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    assert corpo["status"] == "pendente"
    assert corpo["metodo"] == metodo
    preferencia = mercado_pago["preferencias"][0]
    excluidos = {item["id"] for item in preferencia["payment_methods"]["excluded_payment_types"]}
    assert aceito not in excluidos
    assert "ticket" in excluidos or metodo == "boleto"
    assert preferencia["payment_methods"]["installments"] == parcelas
    assert preferencia["items"][0]["unit_price"] == 180.0
    assert preferencia["external_reference"] == str(consulta_futura.id_consulta)

    pagamento = db.get(Pagamento, consulta_futura.id_consulta)
    assert (pagamento.status, pagamento.metodo) == ("pendente", metodo)


def test_metodo_invalido_responde_422(client_pagamento, paciente_logado, consulta_futura, mercado_pago):
    resposta = client_pagamento.post(
        "/api/v1/pagamento/preferencia", json={"id_consulta": consulta_futura.id_consulta, "metodo": "cheque"}
    )
    assert resposta.status_code == 422


def test_nao_paga_consulta_cancelada(client_pagamento, db, paciente_logado, consulta_futura, mercado_pago):
    consulta_futura.status = "cancelada"
    db.commit()
    resposta = client_pagamento.post(
        "/api/v1/pagamento/preferencia", json={"id_consulta": consulta_futura.id_consulta, "metodo": "pix"}
    )
    assert resposta.status_code == 400
    assert mercado_pago["preferencias"] == []


def test_nao_paga_consulta_que_ja_passou(client_pagamento, cenario, paciente_logado, mercado_pago):
    resposta = client_pagamento.post(
        "/api/v1/pagamento/preferencia", json={"id_consulta": cenario["consultas"][1].id_consulta, "metodo": "pix"}
    )
    assert resposta.status_code == 400


def test_profissional_nao_paga(client_pagamento, autenticar, consulta_futura, mercado_pago):
    autenticar(1)
    resposta = client_pagamento.post(
        "/api/v1/pagamento/preferencia", json={"id_consulta": consulta_futura.id_consulta, "metodo": "pix"}
    )
    assert resposta.status_code == 403


@pytest.mark.parametrize(
    ("status_mp", "esperado"),
    [("approved", "aprovado"), ("pending", "pendente"), ("rejected", "recusado"), ("cancelled", "cancelado")],
)
def test_retorno_grava_o_status_real(client_pagamento, db, consulta_futura, mercado_pago, status_mp, esperado):
    mercado_pago["pagamentos"]["99"] = _pagamento_mp(99, consulta_futura.id_consulta, status_mp, "credit_card")

    # O status da URL é ignorado: vale o que o Mercado Pago responde.
    resposta = client_pagamento.get("/api/v1/pagamento/retorno", params={"payment_id": "99", "status": "approved"})

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["status"] == esperado
    pagamento = db.get(Pagamento, consulta_futura.id_consulta)
    assert (pagamento.status, pagamento.metodo, pagamento.id_transacao) == (esperado, "cartao", "99")


def test_tentativa_antiga_nao_desfaz_aprovacao(client_pagamento, db, consulta_futura, mercado_pago):
    mercado_pago["pagamentos"]["1"] = _pagamento_mp(1, consulta_futura.id_consulta, "approved", "credit_card")
    mercado_pago["pagamentos"]["2"] = _pagamento_mp(2, consulta_futura.id_consulta, "cancelled")  # Pix expirado
    client_pagamento.get("/api/v1/pagamento/retorno", params={"payment_id": "1"})

    client_pagamento.post("/api/v1/pagamento/notificacao", json={"type": "payment", "data": {"id": "2"}})

    assert db.get(Pagamento, consulta_futura.id_consulta).status == "aprovado"


def test_estorno_da_transacao_aprovada_cancela(client_pagamento, db, consulta_futura, mercado_pago):
    mercado_pago["pagamentos"]["1"] = _pagamento_mp(1, consulta_futura.id_consulta, "approved", "credit_card")
    client_pagamento.get("/api/v1/pagamento/retorno", params={"payment_id": "1"})
    mercado_pago["pagamentos"]["1"] = _pagamento_mp(1, consulta_futura.id_consulta, "refunded", "credit_card")

    client_pagamento.post("/api/v1/pagamento/notificacao", json={"type": "payment", "data": {"id": "1"}})

    assert db.get(Pagamento, consulta_futura.id_consulta).status == "cancelado"


def test_nao_cria_novo_checkout_para_consulta_paga(client_pagamento, paciente_logado, consulta_futura, mercado_pago):
    mercado_pago["pagamentos"]["1"] = _pagamento_mp(1, consulta_futura.id_consulta, "approved")
    client_pagamento.get("/api/v1/pagamento/retorno", params={"payment_id": "1"})

    resposta = client_pagamento.post(
        "/api/v1/pagamento/preferencia", json={"id_consulta": consulta_futura.id_consulta, "metodo": "pix"}
    )
    assert resposta.status_code == 400


def test_consultar_status_sincroniza_pela_referencia(client_pagamento, paciente_logado, consulta_futura, mercado_pago):
    client_pagamento.post(
        "/api/v1/pagamento/preferencia", json={"id_consulta": consulta_futura.id_consulta, "metodo": "boleto"}
    )
    mercado_pago["busca"] = [_pagamento_mp(5, consulta_futura.id_consulta, "approved", "ticket")]

    resposta = client_pagamento.get(f"/api/v1/pagamento/{consulta_futura.id_consulta}")

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "aprovado"
    assert resposta.json()["metodo"] == "boleto"


def test_cancelar_consulta_cancela_pagamento_pendente(client_pagamento, db, paciente_logado, consulta_futura, mercado_pago):
    client_pagamento.post(
        "/api/v1/pagamento/preferencia", json={"id_consulta": consulta_futura.id_consulta, "metodo": "pix"}
    )

    resposta = client_pagamento.patch(f"/api/v1/consultas/{consulta_futura.id_consulta}/cancelar")

    assert resposta.status_code == 200, resposta.text
    db.expire_all()
    assert db.get(Pagamento, consulta_futura.id_consulta).status == "cancelado"
