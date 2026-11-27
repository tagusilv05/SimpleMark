"""A consulta só é confirmada (e-mail de confirmação) depois do pagamento aprovado."""

from datetime import date, time, timedelta

import pytest

from models.models import Consulta
from services.PagamentoService import pagamento as servico


@pytest.fixture
def consulta_futura(db, cenario):
    """Consulta agendada do paciente daqui a 5 dias, ainda sem pagamento."""
    base = cenario["consultas"][1]
    consulta = Consulta(
        id_paciente=base.id_paciente,
        id_esp_prof=base.id_esp_prof,
        data=date.today() + timedelta(days=5),
        hora=time(9, 0),
        tipo="teleconsulta",
        status="agendada",
        valor=180.00,
    )
    db.add(consulta)
    db.commit()
    return consulta


@pytest.fixture
def confirmadas(monkeypatch):
    """Guarda as consultas cuja confirmação foi disparada, no lugar do e-mail real."""
    lista = []
    monkeypatch.setattr(servico, "disparar_confirmacao", lista.append)
    return lista


def _pagamento_mp(id_mp, id_consulta, status):
    return {"id": id_mp, "external_reference": str(id_consulta), "status": status}


def test_urls_de_retorno_abrem_pagamento_no_frontend(cenario, monkeypatch):
    consulta = cenario["consultas"][1]
    monkeypatch.setattr(servico, "URL_FRONTEND", "https://simplemark-frontend.onrender.com")

    preferencia = servico._montar_preferencia(consulta)
    url_pagamento = f"https://simplemark-frontend.onrender.com/pagamento/{consulta.id_consulta}"

    assert preferencia["back_urls"] == {
        "success": url_pagamento,
        "pending": url_pagamento,
        "failure": url_pagamento,
    }


@pytest.mark.parametrize("status_mp", ["pending", "rejected", "cancelled"])
def test_pagamento_nao_aprovado_nao_confirma(db, consulta_futura, confirmadas, status_mp):
    servico._aplicar_pagamento_mp(_pagamento_mp(7, consulta_futura.id_consulta, status_mp), db)

    assert confirmadas == []


def test_pagamento_aprovado_confirma_uma_vez(db, consulta_futura, confirmadas):
    servico._aplicar_pagamento_mp(_pagamento_mp(7, consulta_futura.id_consulta, "pending"), db)
    assert confirmadas == []

    # Pix compensou: o pagamento vira aprovado e a consulta é confirmada.
    servico._aplicar_pagamento_mp(_pagamento_mp(7, consulta_futura.id_consulta, "approved"), db)
    # Retorno e notificação repetidos não reenviam a confirmação.
    servico._aplicar_pagamento_mp(_pagamento_mp(7, consulta_futura.id_consulta, "approved"), db)

    assert confirmadas == [consulta_futura.id_consulta]


def test_aprovado_direto_confirma(db, consulta_futura, confirmadas):
    servico._aplicar_pagamento_mp(_pagamento_mp(8, consulta_futura.id_consulta, "approved"), db)

    assert confirmadas == [consulta_futura.id_consulta]