"""Horário UTC usado no bloqueio de login e na sessão."""

from datetime import datetime, timezone


def agora_utc() -> datetime:
    """Data e hora atuais com fuso UTC.

    Returns:
        datetime: Momento atual com ``tzinfo`` UTC.
    """
    return datetime.now(timezone.utc)


def como_utc(valor: datetime) -> datetime:
    """Garante fuso UTC. O SQLite devolve data sem fuso; o PostgreSQL devolve com fuso.

    Args:
        valor (datetime): Data e hora com ou sem fuso.

    Returns:
        datetime: O mesmo instante em UTC; valores sem fuso são tratados como UTC.
    """
    if valor.tzinfo is None:
        return valor.replace(tzinfo=timezone.utc)
    return valor.astimezone(timezone.utc)


def agora_local() -> datetime:
    """Relógio de parede do servidor, sem fuso.

    A agenda (data_horario) guarda data e hora sem fuso, do jeito que o
    profissional digitou. Comparar aquelas colunas com agora_utc() deslocaria o
    resultado, então a busca por horário livre usa este relógio.

    Returns:
        datetime: Data e hora locais do servidor, sem fuso (naive).
    """
    return datetime.now()
