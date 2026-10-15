"""Rotas de pagamento das consultas pelo Mercado Pago."""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from core.excecoes import ErroNegocio
from dependencies.autenticacao import UsuarioAtual
from dependencies.database import get_db
from models.models import Paciente
from schemas.pagamento import (
    CriarPreferenciaEntrada,
    PagamentoSaida,
    PreferenciaSaida,
    RetornoPagamentoSaida,
)
from services.PagamentoService.pagamento import (
    consultar_pagamento,
    criar_preferencia_consulta,
    processar_notificacao,
    processar_retorno,
)

router = APIRouter(prefix="/pagamento", tags=["Pagamento"])


def _paciente_logado(usuario: UsuarioAtual) -> Paciente:
    """Devolve o paciente da conta logada; outros perfis recebem 403."""
    paciente = usuario.paciente
    if paciente is None:
        raise ErroNegocio("Apenas pacientes podem realizar o pagamento.", 403)
    return paciente


@router.post("/preferencia", response_model=PreferenciaSaida)
def criar_preferencia(
    dados: CriarPreferenciaEntrada,
    usuario: UsuarioAtual,
    db: Session = Depends(get_db),
):
    """Cria a preferência de pagamento da consulta no Mercado Pago.

    Somente o paciente da consulta (403 para outros perfis). Responde 404 se a
    consulta não existir ou for de outro paciente, 400 se estiver cancelada, sem
    valor ou já paga e 502 se o Mercado Pago não devolver o link. O pagamento
    local fica pendente.
    """
    resultado = criar_preferencia_consulta(dados.id_consulta, _paciente_logado(usuario), db)
    return PreferenciaSaida(**resultado)


@router.get("/retorno/sucesso", response_model=RetornoPagamentoSaida)
def retorno_sucesso(
    db: Session = Depends(get_db),
    payment_id: str | None = Query(default=None),
    collection_id: str | None = Query(default=None),
    external_reference: str | None = Query(default=None),
):
    """Retorno do Mercado Pago depois do pagamento aprovado.

    Rota pública. Consulta o pagamento no Mercado Pago, atualiza o status local e
    devolve o resultado. Responde 400 se o external_reference não for um id de
    consulta.
    """
    return processar_retorno(payment_id, collection_id, external_reference, db)


@router.get("/retorno/pendente", response_model=RetornoPagamentoSaida)
def retorno_pendente(
    db: Session = Depends(get_db),
    payment_id: str | None = Query(default=None),
    collection_id: str | None = Query(default=None),
    external_reference: str | None = Query(default=None),
):
    """Retorno do Mercado Pago com pagamento pendente; mesmo tratamento do sucesso."""
    return processar_retorno(payment_id, collection_id, external_reference, db)


@router.get("/retorno/falha", response_model=RetornoPagamentoSaida)
def retorno_falha(
    db: Session = Depends(get_db),
    payment_id: str | None = Query(default=None),
    collection_id: str | None = Query(default=None),
    external_reference: str | None = Query(default=None),
):
    """Retorno do Mercado Pago com pagamento recusado; mesmo tratamento do sucesso."""
    return processar_retorno(payment_id, collection_id, external_reference, db)


@router.post("/notificacao")
async def notificacao(request: Request, db: Session = Depends(get_db)):
    """Webhook do Mercado Pago: atualiza o status local do pagamento notificado.

    Rota pública. Lê o id do pagamento da query string ou do corpo; notificação
    que não é de pagamento, ou sem id, é ignorada.
    """
    id_pagamento = request.query_params.get("data.id") or request.query_params.get("id")

    try:
        corpo = await request.json()
    except Exception:
        corpo = {}

    if isinstance(corpo, dict):
        dados = corpo.get("data") or {}
        if isinstance(dados, dict) and dados.get("id"):
            id_pagamento = str(dados.get("id"))
        elif corpo.get("id"):
            id_pagamento = str(corpo.get("id"))

    tipo = request.query_params.get("type") or request.query_params.get("topic")
    if isinstance(corpo, dict):
        tipo = corpo.get("type") or corpo.get("topic") or tipo

    if tipo and str(tipo) not in {"payment", "payment.created", "payment.updated"}:
        return {"status": "ignorado"}

    return processar_notificacao(id_pagamento, db)


@router.get("/{id_consulta}", response_model=PagamentoSaida)
def obter_pagamento(
    id_consulta: int,
    usuario: UsuarioAtual,
    db: Session = Depends(get_db),
):
    """Devolve o pagamento da consulta, sincronizado com o Mercado Pago.

    Somente o paciente da consulta (403 para outros perfis). Responde 404 se a
    consulta não existir, for de outro paciente ou não tiver pagamento.
    """
    paciente = _paciente_logado(usuario)
    pagamento = consultar_pagamento(id_consulta, paciente, db)
    return PagamentoSaida(
        id_consulta=pagamento.id_consulta,
        status=pagamento.status,
        data=pagamento.data,
        hora=pagamento.hora,
    )
