"""Pagamento da consulta pelo paciente via checkout do Mercado Pago.

A consulta é ligada ao pagamento pelo external_reference (id da consulta), e
o status do Mercado Pago é traduzido para o status local por STATUS_MP.
"""

import os

from models.models import Consulta, Paciente, Pagamento
from sqlalchemy.orm import Session

from core.excecoes import ErroNegocio
from repositories.pagamento import (
    atualizar_status_pagamento,
    buscar_consulta_por_id,
    buscar_pagamento_por_consulta,
    criar_pagamento,
)
from services.PagamentoService.api_mercado_pago import (
    buscar_pagamentos,
    criar_preferencia,
    obter_pagamento,
)

URL_RETORNO = os.getenv(
    "MERCADOPAGO_RETURN_URL",
    "http://localhost:8080/api/v1/pagamento/retorno",
).rstrip("/")

STATUS_MP = {
    "approved": "aprovado",
    "pending": "pendente",
    "in_process": "pendente",
    "authorized": "pendente",
    "rejected": "recusado",
    "cancelled": "cancelado",
    "refunded": "cancelado",
    "charged_back": "cancelado",
}


def criar_preferencia_consulta(id_consulta: int, paciente: Paciente, db: Session):
    """Cria o checkout do Mercado Pago para a consulta do paciente.

    Recusa com ErroNegocio 400 consulta cancelada, valor zerado ou negativo e
    consulta já paga; sem init_point na resposta, levanta 502. Cria o pagamento
    local como "pendente" ou volta para "pendente" o que já existia.
    """
    consulta = _consulta_do_paciente(id_consulta, paciente, db)

    if consulta.status == "cancelado":
        raise ErroNegocio("Nao e possivel pagar uma consulta cancelada.", 400)

    if float(consulta.valor) <= 0:
        raise ErroNegocio("O valor da consulta e invalido.", 400)

    pagamento = consulta.pagamento
    if pagamento and pagamento.status == "aprovado":
        raise ErroNegocio("Esta consulta ja foi paga.", 400)

    preferencia = criar_preferencia(_montar_preferencia(consulta))

    init_point = preferencia.get("init_point")
    sandbox_init_point = preferencia.get("sandbox_init_point")
    if not init_point:
        raise ErroNegocio("O Mercado Pago nao retornou o init_point.", 502)

    if pagamento is None:
        pagamento = criar_pagamento(consulta.id_consulta, "pendente", db)
    elif pagamento.status != "pendente":
        pagamento = atualizar_status_pagamento(pagamento, "pendente", db)

    return {
        "id": preferencia.get("id"),
        "init_point": init_point,
        "sandbox_init_point": sandbox_init_point or init_point,
        "status": pagamento.status,
        "id_consulta": consulta.id_consulta,
    }


def consultar_pagamento(id_consulta: int, paciente: Paciente, db: Session):
    """Status do pagamento da consulta, sincronizado com o Mercado Pago.

    Levanta ErroNegocio 404 se a consulta não for do paciente ou se não houver
    pagamento.
    """
    consulta = _consulta_do_paciente(id_consulta, paciente, db)
    pagamento = _sincronizar_por_referencia(consulta, db)
    if pagamento is None:
        raise ErroNegocio("Pagamento nao encontrado para esta consulta.", 404)
    return pagamento


def processar_retorno(payment_id: str | None, collection_id: str | None, external_reference: str | None, db: Session):
    """Trata o retorno do checkout (back_urls) e atualiza o pagamento local.

    Usa o payment_id (ou collection_id) para buscar o pagamento; sem ele, ou se
    não achar a consulta, sincroniza pelo external_reference.
    """
    id_mp = payment_id or collection_id
    pagamento = None
    status = "pendente"

    if id_mp and id_mp != "null":
        dados = obter_pagamento(str(id_mp))
        pagamento = _aplicar_pagamento_mp(dados, db)
        status = pagamento.status if pagamento else _status_local(dados.get("status"))
        if external_reference is None:
            external_reference = dados.get("external_reference")

    if pagamento is None and external_reference:
        consulta = buscar_consulta_por_id(_id_consulta(external_reference), db)
        if consulta:
            pagamento = _sincronizar_por_referencia(consulta, db)
            if pagamento:
                status = pagamento.status

    return {
        "id_consulta": pagamento.id_consulta if pagamento else _id_consulta_opcional(external_reference),
        "status": status,
        "payment_id": str(id_mp) if id_mp and id_mp != "null" else None,
    }


def processar_notificacao(id_pagamento: str | None, db: Session):
    """Trata a notificação (webhook) do Mercado Pago e atualiza o pagamento.

    Sem id ou sem consulta correspondente, devolve status "ignorado".
    """
    if not id_pagamento:
        return {"status": "ignorado"}

    dados = obter_pagamento(str(id_pagamento))
    pagamento = _aplicar_pagamento_mp(dados, db)
    if pagamento is None:
        return {"status": "ignorado"}
    return {"status": pagamento.status, "id_consulta": pagamento.id_consulta}


def _consulta_do_paciente(id_consulta: int, paciente: Paciente, db: Session) -> Consulta:
    """Consulta do paciente; 404 se não existir ou for de outro paciente."""
    consulta = buscar_consulta_por_id(id_consulta, db)
    if consulta is None:
        raise ErroNegocio("Consulta nao encontrada.", 404)
    if consulta.id_paciente != paciente.id_paciente:
        raise ErroNegocio("Consulta nao encontrada.", 404)
    return consulta


def _montar_preferencia(consulta: Consulta) -> dict:
    """Monta o corpo da preferência: item, pagador, back_urls e referência.

    Telefone e endereço só entram quando o usuário tem dados suficientes.
    """
    usuario = consulta.paciente.usuario
    nome, sobrenome = _nome_e_sobrenome(usuario.nome)
    preferencia = {
        "items": [
            {
                "id": str(consulta.id_consulta),
                "title": "Consulta",
                "description": "Consulta medica",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": float(consulta.valor),
            }
        ],
        "payer": {
            "name": nome,
            "surname": sobrenome,
            "email": usuario.email,
            "identification": {
                "type": "CPF",
                "number": _somente_digitos(usuario.cpf),
            },
        },
        "back_urls": {
            "success": f"{URL_RETORNO}/sucesso",
            "pending": f"{URL_RETORNO}/pendente",
            "failure": f"{URL_RETORNO}/falha",
        },
        "auto_return": "approved",
        "external_reference": str(consulta.id_consulta),
        "expires": False,
    }

    telefone = _telefone(usuario.telefone)
    if telefone:
        preferencia["payer"]["phone"] = telefone

    endereco = _endereco(usuario.endereco)
    if endereco:
        preferencia["payer"]["address"] = endereco

    return preferencia


def _sincronizar_por_referencia(consulta: Consulta, db: Session) -> Pagamento | None:
    """Atualiza o pagamento local a partir da busca por external_reference.

    Pagamento já aprovado não é consultado de novo. Entre os resultados, vale o
    de status mais relevante.
    """
    pagamento = consulta.pagamento or buscar_pagamento_por_consulta(consulta.id_consulta, db)
    if pagamento and pagamento.status == "aprovado":
        return pagamento

    resultado = buscar_pagamentos(str(consulta.id_consulta))
    resultados = resultado.get("results") or []
    if not resultados:
        return pagamento

    escolhido = _pagamento_mais_relevante(resultados)
    return _aplicar_pagamento_mp(escolhido, db) or pagamento


def _aplicar_pagamento_mp(dados: dict, db: Session) -> Pagamento | None:
    """Grava no pagamento local o status de um pagamento do Mercado Pago.

    Cria o pagamento se ainda não existir. Devolve None se a referência não
    apontar para uma consulta.
    """
    id_consulta = _id_consulta_opcional(dados.get("external_reference"))
    if id_consulta is None:
        return None

    consulta = buscar_consulta_por_id(id_consulta, db)
    if consulta is None:
        return None

    status = _status_local(dados.get("status"))
    pagamento = consulta.pagamento or buscar_pagamento_por_consulta(id_consulta, db)
    if pagamento is None:
        return criar_pagamento(id_consulta, status, db)
    return atualizar_status_pagamento(pagamento, status, db)


def _pagamento_mais_relevante(resultados: list) -> dict:
    """Escolhe o resultado de status mais forte (aprovado antes de pendente etc.)."""
    ordem = {
        "approved": 0,
        "authorized": 1,
        "in_process": 2,
        "pending": 3,
        "rejected": 4,
        "cancelled": 5,
        "refunded": 6,
        "charged_back": 7,
    }
    return min(resultados, key=lambda item: ordem.get(str(item.get("status")), 99))


def _status_local(status_mp) -> str:
    """Traduz o status do Mercado Pago; desconhecido vira "pendente"."""
    return STATUS_MP.get(str(status_mp), "pendente")


def _nome_e_sobrenome(nome_completo: str):
    """Separa o primeiro nome do resto, com valores padrão se faltar."""
    partes = (nome_completo or "").strip().split()
    if not partes:
        return "Paciente", "SimpleMark"
    if len(partes) == 1:
        return partes[0], partes[0]
    return partes[0], " ".join(partes[1:])


def _somente_digitos(valor: str) -> str:
    """Mantém só os dígitos do texto."""
    return "".join(caractere for caractere in (valor or "") if caractere.isdigit())


def _telefone(telefone: str) -> dict | None:
    """Telefone no formato do Mercado Pago, ou None se tiver menos de 10 dígitos."""
    digitos = _somente_digitos(telefone)
    if len(digitos) < 10:
        return None
    return {
        "area_code": digitos[:2],
        "number": digitos[2:],
    }


def _endereco(endereco) -> dict | None:
    """Endereço no formato do Mercado Pago; o número só entra se tiver dígitos."""
    if endereco is None:
        return None

    dados = {
        "zip_code": endereco.cep,
        "street_name": endereco.logradouro,
    }
    numero = _somente_digitos(endereco.numero)
    if numero:
        dados["street_number"] = int(numero)
    return dados


def _id_consulta(external_reference: str) -> int:
    """Converte o external_reference em id; inválido levanta ErroNegocio 400."""
    try:
        return int(str(external_reference))
    except (TypeError, ValueError):
        raise ErroNegocio("external_reference invalida.", 400)


def _id_consulta_opcional(external_reference) -> int | None:
    """Converte o external_reference em id, ou None se for inválido."""
    try:
        return int(str(external_reference))
    except (TypeError, ValueError):
        return None