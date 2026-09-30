# Arquivo criado por Gustavo
"""Funções de tempo compartilhadas pelo bloqueio de login e pela sessão."""

from datetime import datetime, timezone


def agora_utc() -> datetime:
    """Momento atual em UTC, com fuso horário."""
    return datetime.now(timezone.utc)


def como_utc(momento: datetime) -> datetime:
    """Garante que a data tem fuso horário (UTC).

    O PostgreSQL devolve datas com fuso. O SQLite, usado nos testes, devolve sem fuso.
    Python não compara as duas formas entre si, então padronizamos antes de comparar.
    """
    if momento.tzinfo is None:
        return momento.replace(tzinfo=timezone.utc)
    return momento
