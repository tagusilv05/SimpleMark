from datetime import date, time

from pydantic import BaseModel


class CriarPreferenciaEntrada(BaseModel):
    id_consulta: int


class PreferenciaSaida(BaseModel):
    id: str
    init_point: str
    sandbox_init_point: str
    status: str
    id_consulta: int


class PagamentoSaida(BaseModel):
    id_consulta: int
    status: str
    data: date
    hora: time


class RetornoPagamentoSaida(BaseModel):
    id_consulta: int | None = None
    status: str
    payment_id: str | None = None