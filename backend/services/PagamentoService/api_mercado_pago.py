import os

import httpx

from core.excecoes import ErroNegocio

URL_PREFERENCIAS = "https://api.mercadopago.com/checkout/preferences"
URL_PAGAMENTOS = "https://api.mercadopago.com/v1/payments"


def _access_token() -> str:
    token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
    if not token:
        raise ErroNegocio("Access Token do Mercado Pago nao configurado.", 500)
    return token


def _cabecalhos() -> dict:
    return {
        "Authorization": f"Bearer {_access_token()}",
        "Content-Type": "application/json",
    }


def criar_preferencia(dados: dict) -> dict:
    try:
        resposta = httpx.post(
            URL_PREFERENCIAS,
            json=dados,
            headers=_cabecalhos(),
            timeout=20.0,
        )
    except httpx.RequestError as erro:
        raise ErroNegocio("Nao foi possivel conectar ao Mercado Pago.", 502) from erro

    corpo = _corpo_json(resposta)
    if resposta.status_code >= 400:
        raise ErroNegocio(_mensagem_erro(corpo), 400)
    return corpo


def obter_pagamento(id_pagamento: str) -> dict:
    try:
        resposta = httpx.get(
            f"{URL_PAGAMENTOS}/{id_pagamento}",
            headers=_cabecalhos(),
            timeout=20.0,
        )
    except httpx.RequestError as erro:
        raise ErroNegocio("Nao foi possivel conectar ao Mercado Pago.", 502) from erro

    corpo = _corpo_json(resposta)
    if resposta.status_code >= 400:
        raise ErroNegocio(_mensagem_erro(corpo), 400)
    return corpo


def buscar_pagamentos(external_reference: str) -> dict:
    try:
        resposta = httpx.get(
            f"{URL_PAGAMENTOS}/search",
            params={"external_reference": external_reference},
            headers=_cabecalhos(),
            timeout=20.0,
        )
    except httpx.RequestError as erro:
        raise ErroNegocio("Nao foi possivel conectar ao Mercado Pago.", 502) from erro

    corpo = _corpo_json(resposta)
    if resposta.status_code >= 400:
        raise ErroNegocio(_mensagem_erro(corpo), 400)
    return corpo


def _corpo_json(resposta: httpx.Response) -> dict:
    try:
        corpo = resposta.json()
    except ValueError:
        raise ErroNegocio("Resposta invalida do Mercado Pago.", 502)
    if not isinstance(corpo, dict):
        return {}
    return corpo


def _mensagem_erro(corpo: dict) -> str:
    mensagem = corpo.get("message") or corpo.get("error") or "Erro ao processar o pagamento."
    return str(mensagem)