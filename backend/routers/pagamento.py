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
    resultado = criar_preferencia_consulta(dados.id_consulta, _paciente_logado(usuario), db)
    return PreferenciaSaida(**resultado)


@router.get("/retorno/sucesso", response_model=RetornoPagamentoSaida)
def retorno_sucesso(
    db: Session = Depends(get_db),
    payment_id: str | None = Query(default=None),
    collection_id: str | None = Query(default=None),
    external_reference: str | None = Query(default=None),
):
    return processar_retorno(payment_id, collection_id, external_reference, db)


@router.get("/retorno/pendente", response_model=RetornoPagamentoSaida)
def retorno_pendente(
    db: Session = Depends(get_db),
    payment_id: str | None = Query(default=None),
    collection_id: str | None = Query(default=None),
    external_reference: str | None = Query(default=None),
):
    return processar_retorno(payment_id, collection_id, external_reference, db)


@router.get("/retorno/falha", response_model=RetornoPagamentoSaida)
def retorno_falha(
    db: Session = Depends(get_db),
    payment_id: str | None = Query(default=None),
    collection_id: str | None = Query(default=None),
    external_reference: str | None = Query(default=None),
):
    return processar_retorno(payment_id, collection_id, external_reference, db)


@router.post("/notificacao")
async def notificacao(request: Request, db: Session = Depends(get_db)):
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
    paciente = _paciente_logado(usuario)
    pagamento = consultar_pagamento(id_consulta, paciente, db)
    return PagamentoSaida(
        id_consulta=pagamento.id_consulta,
        status=pagamento.status,
        data=pagamento.data,
        hora=pagamento.hora,
    )
