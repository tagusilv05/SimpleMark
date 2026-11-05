"""Pagamento da consulta pelo paciente via checkout do Mercado Pago.

A consulta é ligada ao pagamento pelo external_reference (id da consulta), e
o status do Mercado Pago é traduzido para o status local por STATUS_MP.

Estados locais do pagamento:
    pendente   checkout aberto ou pagamento aguardando compensação (Pix/boleto)
    aprovado   pagamento confirmado pelo Mercado Pago
    recusado   pagamento recusado (o paciente pode tentar de novo)
    cancelado  pagamento cancelado, estornado ou consulta cancelada antes do pagamento

A forma de pagamento escolhida pelo paciente (pix, cartao, boleto) restringe os
meios aceitos no checkout pela configuração payment_methods da preferência.
"""

import logging
import os
from datetime import datetime

from models.models import Consulta, Paciente, Pagamento
from sqlalchemy.orm import Session

from core.excecoes import ErroNegocio
from core.tempo import agora_local
from repositories.pagamento import (
    atualizar_pagamento,
    buscar_consulta_por_id,
    buscar_pagamento_por_consulta,
    criar_pagamento,
)
from services.PagamentoService.api_mercado_pago import (
    buscar_pagamentos,
    criar_preferencia,
    obter_pagamento,
)

logger = logging.getLogger(__name__)

# Tela do frontend que recebe o paciente de volta do checkout.
URL_RETORNO = os.getenv(
    "MERCADOPAGO_RETURN_URL",
    "http://localhost/pagamento/retorno",
).rstrip("/")

# Webhook opcional (precisa ser uma URL pública para o Mercado Pago alcançar).
URL_NOTIFICACAO = os.getenv("MERCADOPAGO_NOTIFICATION_URL", "").strip()

STATUS_PENDENTE = "pendente"
STATUS_APROVADO = "aprovado"
STATUS_RECUSADO = "recusado"
STATUS_CANCELADO = "cancelado"
STATUS_PAGAMENTO = (STATUS_PENDENTE, STATUS_APROVADO, STATUS_RECUSADO, STATUS_CANCELADO)

STATUS_MP = {
    "approved": STATUS_APROVADO,
    "pending": STATUS_PENDENTE,
    "in_process": STATUS_PENDENTE,
    "in_mediation": STATUS_PENDENTE,
    "authorized": STATUS_PENDENTE,
    "rejected": STATUS_RECUSADO,
    "cancelled": STATUS_CANCELADO,
    "refunded": STATUS_CANCELADO,
    "charged_back": STATUS_CANCELADO,
}

# O banco tem as duas grafias de consulta cancelada.
STATUS_CONSULTA_CANCELADA = {"cancelada", "cancelado"}

# Tipos de pagamento do Mercado Pago (payment_type_id).
_TIPOS_MP = {"credit_card", "debit_card", "prepaid_card", "ticket", "bank_transfer", "atm", "digital_currency", "digital_wallet"}

METODOS = {
    # Pix é o tipo bank_transfer no Brasil.
    "pix": {"aceitos": {"bank_transfer"}, "parcelas": 1},
    "cartao": {"aceitos": {"credit_card", "debit_card", "prepaid_card"}, "parcelas": 10},
    "boleto": {"aceitos": {"ticket"}, "parcelas": 1},
}

_METODO_POR_TIPO_MP = {
    "bank_transfer": "pix",
    "credit_card": "cartao",
    "debit_card": "cartao",
    "prepaid_card": "cartao",
    "ticket": "boleto",
}


def criar_preferencia_consulta(id_consulta: int, metodo: str, paciente: Paciente, db: Session):
    """Cria o checkout do Mercado Pago para a consulta do paciente.

    O checkout só aceita a forma de pagamento escolhida. Recusa com ErroNegocio
    400 método inválido, consulta cancelada ou com horário já passado, valor
    zerado e consulta já paga; sem init_point na resposta, levanta 502. Grava o
    pagamento local como "pendente" com o método escolhido.
    """
    if metodo not in METODOS:
        raise ErroNegocio("Forma de pagamento inválida. Escolha Pix, cartão ou boleto.", 400)

    consulta = _consulta_do_paciente(id_consulta, paciente, db)

    if consulta.status in STATUS_CONSULTA_CANCELADA:
        raise ErroNegocio("Não é possível pagar uma consulta cancelada.", 400)

    if _inicio_consulta(consulta) <= agora_local():
        raise ErroNegocio("O horário desta consulta já passou.", 400)

    if float(consulta.valor) <= 0:
        raise ErroNegocio("O valor da consulta é inválido.", 400)

    pagamento = consulta.pagamento
    if pagamento and pagamento.status == STATUS_APROVADO:
        raise ErroNegocio("Esta consulta já foi paga.", 400)

    preferencia = criar_preferencia(_montar_preferencia(consulta, metodo))

    init_point = preferencia.get("init_point")
    sandbox_init_point = preferencia.get("sandbox_init_point")
    if not init_point:
        raise ErroNegocio("O Mercado Pago não retornou o link de pagamento.", 502)

    if pagamento is None:
        pagamento = criar_pagamento(consulta.id_consulta, STATUS_PENDENTE, db, metodo=metodo)
    else:
        pagamento = atualizar_pagamento(pagamento, db, status=STATUS_PENDENTE, metodo=metodo)

    return {
        "id": preferencia.get("id"),
        "init_point": init_point,
        "sandbox_init_point": sandbox_init_point or init_point,
        "status": pagamento.status,
        "metodo": pagamento.metodo,
        "id_consulta": consulta.id_consulta,
    }


def consultar_pagamento(id_consulta: int, paciente: Paciente, db: Session):
    """Status do pagamento da consulta, sincronizado com o Mercado Pago.

    Se o Mercado Pago não responder, devolve o status local. Levanta
    ErroNegocio 404 se a consulta não for do paciente ou se não houver pagamento.
    """
    consulta = _consulta_do_paciente(id_consulta, paciente, db)
    try:
        pagamento = _sincronizar_por_referencia(consulta, db)
    except ErroNegocio as erro:
        logger.warning("Consulta %s: falha ao sincronizar o pagamento (%s).", id_consulta, erro)
        pagamento = consulta.pagamento or buscar_pagamento_por_consulta(id_consulta, db)
    if pagamento is None:
        raise ErroNegocio("Pagamento não encontrado para esta consulta.", 404)
    return pagamento


def processar_retorno(payment_id: str | None, collection_id: str | None, external_reference: str | None, db: Session):
    """Trata o retorno do checkout (back_urls) e atualiza o pagamento local.

    Usa o payment_id (ou collection_id) para buscar o pagamento; sem ele, ou se
    não achar a consulta, sincroniza pelo external_reference. O status vem
    sempre do Mercado Pago, nunca dos parâmetros da URL.
    """
    id_mp = payment_id or collection_id
    if id_mp in ("null", ""):
        id_mp = None
    pagamento = None
    status = STATUS_PENDENTE

    if id_mp:
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
        "metodo": pagamento.metodo if pagamento else None,
        "payment_id": str(id_mp) if id_mp else None,
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


def cancelar_pagamento_da_consulta(consulta: Consulta, db: Session) -> Pagamento | None:
    """Marca como cancelado o pagamento ainda não aprovado de uma consulta cancelada.

    Pagamento aprovado continua aprovado (o estorno é tratado no Mercado Pago e
    chega pela notificação como "cancelado"). Não faz nada sem pagamento.
    """
    pagamento = consulta.pagamento or buscar_pagamento_por_consulta(consulta.id_consulta, db)
    if pagamento is None or pagamento.status in (STATUS_APROVADO, STATUS_CANCELADO):
        return pagamento
    return atualizar_pagamento(pagamento, db, status=STATUS_CANCELADO)


def _consulta_do_paciente(id_consulta: int, paciente: Paciente, db: Session) -> Consulta:
    """Consulta do paciente; 404 se não existir ou for de outro paciente."""
    consulta = buscar_consulta_por_id(id_consulta, db)
    if consulta is None or consulta.id_paciente != paciente.id_paciente:
        raise ErroNegocio("Consulta não encontrada.", 404)
    return consulta


def _inicio_consulta(consulta: Consulta) -> datetime:
    """Data e hora de início da consulta (sem fuso, como a agenda grava)."""
    return datetime.combine(consulta.data, consulta.hora)


def _montar_preferencia(consulta: Consulta, metodo: str) -> dict:
    """Monta o corpo da preferência: item, pagador, meios aceitos, back_urls e referência.

    O checkout expira no início da consulta. Telefone e endereço só entram
    quando o usuário tem dados suficientes.
    """
    usuario = consulta.paciente.usuario
    nome, sobrenome = _nome_e_sobrenome(usuario.nome)
    profissional_especialidade = consulta.profissional_especialidade
    nome_profissional = profissional_especialidade.profissional.usuario.nome
    especialidade = profissional_especialidade.especialidade.especialidade
    data_hora = f"{consulta.data.strftime('%d/%m/%Y')} às {consulta.hora.strftime('%H:%M')}"

    config_metodo = METODOS[metodo]
    preferencia = {
        "items": [
            {
                "id": str(consulta.id_consulta),
                "title": f"Teleconsulta - {especialidade}",
                "description": f"{nome_profissional} - {data_hora}",
                "category_id": "services",
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
        "payment_methods": {
            "excluded_payment_types": [
                {"id": tipo} for tipo in sorted(_TIPOS_MP - config_metodo["aceitos"])
            ],
            "installments": config_metodo["parcelas"],
        },
        "back_urls": {
            "success": f"{URL_RETORNO}?resultado=sucesso",
            "pending": f"{URL_RETORNO}?resultado=pendente",
            "failure": f"{URL_RETORNO}?resultado=falha",
        },
        "external_reference": str(consulta.id_consulta),
        "statement_descriptor": "SIMPLEMARK",
        "metadata": {"id_consulta": consulta.id_consulta, "metodo": metodo},
    }

    # O Mercado Pago só aceita auto_return com back_url pública (https).
    if URL_RETORNO.startswith("https://"):
        preferencia["auto_return"] = "approved"

    if URL_NOTIFICACAO:
        preferencia["notification_url"] = URL_NOTIFICACAO

    inicio = _inicio_consulta(consulta)
    preferencia["expires"] = True
    preferencia["expiration_date_to"] = inicio.astimezone().isoformat(timespec="milliseconds")

    telefone = _telefone(usuario.telefone)
    if telefone:
        preferencia["payer"]["phone"] = telefone

    endereco = _endereco(usuario.endereco)
    if endereco:
        preferencia["payer"]["address"] = endereco

    return preferencia


def _sincronizar_por_referencia(consulta: Consulta, db: Session) -> Pagamento | None:
    """Atualiza o pagamento local a partir da busca por external_reference.

    Pagamento já aprovado ou cancelado não é consultado de novo. Entre os
    resultados, vale o de status mais relevante.
    """
    pagamento = consulta.pagamento or buscar_pagamento_por_consulta(consulta.id_consulta, db)
    if pagamento and pagamento.status in (STATUS_APROVADO, STATUS_CANCELADO):
        return pagamento

    resultado = buscar_pagamentos(str(consulta.id_consulta))
    resultados = resultado.get("results") or []
    if not resultados:
        return pagamento

    escolhido = _pagamento_mais_relevante(resultados)
    return _aplicar_pagamento_mp(escolhido, db) or pagamento


def _aplicar_pagamento_mp(dados: dict, db: Session) -> Pagamento | None:
    """Grava no pagamento local o status de um pagamento do Mercado Pago.

    Cria o pagamento se ainda não existir. Um pagamento aprovado só pode virar
    cancelado pelo estorno da mesma transação. Devolve None se a referência não
    apontar para uma consulta.
    """
    id_consulta = _id_consulta_opcional(dados.get("external_reference"))
    if id_consulta is None:
        return None

    consulta = buscar_consulta_por_id(id_consulta, db)
    if consulta is None:
        return None

    status = _status_local(dados.get("status"))
    metodo = _METODO_POR_TIPO_MP.get(str(dados.get("payment_type_id")))
    id_transacao = str(dados["id"]) if dados.get("id") is not None else None

    pagamento = consulta.pagamento or buscar_pagamento_por_consulta(id_consulta, db)
    if pagamento is None:
        return criar_pagamento(id_consulta, status, db, metodo=metodo, id_transacao=id_transacao)

    if pagamento.status == STATUS_APROVADO and (
        status != STATUS_CANCELADO or (pagamento.id_transacao and pagamento.id_transacao != id_transacao)
    ):
        # Só o estorno da própria transação aprovada tira o pagamento de "aprovado";
        # tentativas antigas (um Pix que expirou, um cartão recusado) são ignoradas.
        return pagamento
    if pagamento.status == status and pagamento.id_transacao == id_transacao:
        return pagamento
    return atualizar_pagamento(pagamento, db, status=status, metodo=metodo, id_transacao=id_transacao)


def _pagamento_mais_relevante(resultados: list) -> dict:
    """Escolhe o resultado de status mais forte (aprovado antes de pendente etc.)."""
    ordem = {
        "approved": 0,
        "refunded": 1,
        "charged_back": 2,
        "authorized": 3,
        "in_process": 4,
        "in_mediation": 5,
        "pending": 6,
        "rejected": 7,
        "cancelled": 8,
    }
    return min(resultados, key=lambda item: ordem.get(str(item.get("status")), 99))


def _status_local(status_mp) -> str:
    """Traduz o status do Mercado Pago; desconhecido vira "pendente"."""
    return STATUS_MP.get(str(status_mp), STATUS_PENDENTE)


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
        raise ErroNegocio("Referência de pagamento inválida.", 400)


def _id_consulta_opcional(external_reference) -> int | None:
    """Converte o external_reference em id, ou None se for inválido."""
    try:
        return int(str(external_reference))
    except (TypeError, ValueError):
        return None
