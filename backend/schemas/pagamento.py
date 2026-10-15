"""Entradas e saídas do pagamento via Mercado Pago (/pagamento)."""

from datetime import date, time

from pydantic import BaseModel


class CriarPreferenciaEntrada(BaseModel):
    """Corpo de POST /pagamento/preferencia."""

    id_consulta: int


class PreferenciaSaida(BaseModel):
    """Resposta de POST /pagamento/preferencia: os links de checkout do
    Mercado Pago e o status local do pagamento.
    """

    id: str
    init_point: str
    sandbox_init_point: str
    status: str
    id_consulta: int


class PagamentoSaida(BaseModel):
    """Resposta de GET /pagamento/{id_consulta}."""

    id_consulta: int
    status: str
    data: date
    hora: time


class RetornoPagamentoSaida(BaseModel):
    """Resposta das rotas /pagamento/retorno/* (sucesso, pendente e falha)."""

    id_consulta: int | None = None
    status: str
    payment_id: str | None = None