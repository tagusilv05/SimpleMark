"""Chamadas HTTP à API do Mercado Pago (preferências e pagamentos)."""

import os

import httpx

from core.excecoes import ErroNegocio

URL_PREFERENCIAS = "https://api.mercadopago.com/checkout/preferences"
URL_PAGAMENTOS = "https://api.mercadopago.com/v1/payments"


def _access_token() -> str:
    """Lê o Access Token do ambiente (MERCADOPAGO_ACCESS_TOKEN).

    Returns:
        str: O Access Token do Mercado Pago.

    Raises:
        ErroNegocio: Com status 500, quando o token não está configurado.
    """
    token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
    if not token:
        raise ErroNegocio("Access Token do Mercado Pago nao configurado.", 500)
    return token


def _cabecalhos() -> dict:
    """Cabeçalhos de autenticação e JSON das requisições ao Mercado Pago.

    Returns:
        dict: Cabeçalhos ``Authorization`` e ``Content-Type``.
    """
    return {
        "Authorization": f"Bearer {_access_token()}",
        "Content-Type": "application/json",
    }


def criar_preferencia(dados: dict) -> dict:
    """Cria a preferência de checkout e devolve o corpo da resposta.

    Args:
        dados (dict): Corpo da preferência.

    Returns:
        dict: Corpo JSON da resposta do Mercado Pago.

    Raises:
        ErroNegocio: Com status 502, em falha de conexão, ou 400, quando a API
            devolve erro.
    """
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
    """Busca um pagamento pelo id do Mercado Pago.

    Args:
        id_pagamento (str): ID do pagamento no Mercado Pago.

    Returns:
        dict: Corpo JSON do pagamento.

    Raises:
        ErroNegocio: Com status 502, em falha de conexão, ou 400, quando a API
            devolve erro.
    """
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
    """Lista os pagamentos com o external_reference informado.

    Args:
        external_reference (str): Referência da consulta (o ID dela).

    Returns:
        dict: Corpo JSON da busca, com os pagamentos em ``results``.

    Raises:
        ErroNegocio: Com status 502, em falha de conexão, ou 400, quando a API
            devolve erro.
    """
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
    """Corpo JSON da resposta; {} se não for objeto.

    Args:
        resposta (httpx.Response): Resposta HTTP do Mercado Pago.

    Returns:
        dict: O corpo JSON, ou ``{}`` se ele não for um objeto.

    Raises:
        ErroNegocio: Com status 502, quando o corpo não é JSON válido.
    """
    try:
        corpo = resposta.json()
    except ValueError:
        raise ErroNegocio("Resposta invalida do Mercado Pago.", 502)
    if not isinstance(corpo, dict):
        return {}
    return corpo


def _mensagem_erro(corpo: dict) -> str:
    """Mensagem de erro devolvida pelo Mercado Pago, ou uma genérica.

    Args:
        corpo (dict): Corpo JSON da resposta de erro.

    Returns:
        str: A mensagem de erro.
    """
    mensagem = corpo.get("message") or corpo.get("error") or "Erro ao processar o pagamento."
    return str(mensagem)