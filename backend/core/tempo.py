"""Horário UTC usado no bloqueio de login e na sessão."""

from datetime import datetime, timezone


def agora_utc() -> datetime:
    return datetime.now(timezone.utc)


def como_utc(valor: datetime) -> datetime:
    """Garante fuso UTC. O SQLite devolve data sem fuso; o PostgreSQL devolve com fuso."""
    if valor.tzinfo is None:
        return valor.replace(tzinfo=timezone.utc)
    return valor.astimezone(timezone.utc)


def agora_local() -> datetime:
    """Relógio de parede do servidor, sem fuso.

    A agenda (data_horario) guarda data e hora sem fuso, do jeito que o
    profissional digitou. Comparar aquelas colunas com agora_utc() deslocaria o
    resultado, então a busca por horário livre usa este relógio.
    """
    return datetime.now()
