"""Hash Argon2 da senha e JWT ligado à sessão de login."""

import uuid
from datetime import timedelta

import jwt
from pwdlib import PasswordHash

from core.parametros import segredo_jwt
from core.tempo import agora_utc

_ALGORITMO = "HS256"
_hasher = PasswordHash.recommended()


class TokenInvalido(Exception):
    """Assinatura, prazo ou conteúdo do token não servem."""


def gerar_hash_senha(senha: str) -> str:
    return _hasher.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> tuple[bool, str | None]:
    """Confere a senha. O segundo item é um hash novo, se o algoritmo pedir atualização."""
    return _hasher.verify_and_update(senha, senha_hash)


def gerar_token_acesso(id_usuario: uuid.UUID, id_sessao: uuid.UUID) -> str:
    """Assina o id do usuário (sub) e o id da sessão (sid).

    O prazo do JWT é folgado de propósito. Quem manda na expiração é a sessão:
    24 horas sem uso, ou o logout.
    """
    expira = agora_utc() + timedelta(days=7)
    payload = {"sub": str(id_usuario), "sid": str(id_sessao), "exp": expira}
    token = jwt.encode(payload, segredo_jwt(), algorithm=_ALGORITMO)
    if isinstance(token, bytes):
        return token.decode("utf-8")
    return token


def ler_token_acesso(token: str) -> dict:
    try:
        dados = jwt.decode(token, segredo_jwt(), algorithms=[_ALGORITMO])
    except jwt.PyJWTError as exc:
        raise TokenInvalido("Token inválido.") from exc
    if "sub" not in dados or "sid" not in dados:
        raise TokenInvalido("Token inválido.")
    return dados