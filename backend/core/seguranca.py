"""Hash Argon2 da senha e JWT ligado à sessão de login."""

import hashlib
import hmac
import secrets
import uuid
from datetime import timedelta

import jwt
from pwdlib import PasswordHash

from core.parametros import segredo_jwt
from core.tempo import agora_utc

_ALGORITMO = "HS256"

TAMANHO_CODIGO_LOGIN = 6
_hasher = PasswordHash.recommended()


class TokenInvalido(Exception):
    """Assinatura, prazo ou conteúdo do token não servem."""


def gerar_hash_senha(senha: str) -> str:
    """Gera o hash da senha com o algoritmo recomendado (Argon2).

    Args:
        senha (str): Senha em texto puro.

    Returns:
        str: Hash da senha.
    """
    return _hasher.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> tuple[bool, str | None]:
    """Confere a senha. O segundo item é um hash novo, se o algoritmo pedir atualização.

    Args:
        senha (str): Senha em texto puro informada.
        senha_hash (str): Hash guardado no banco.

    Returns:
        tuple[bool, str | None]: Se a senha confere e, quando for o caso, o novo hash
        a ser gravado (``None`` se não precisar de atualização).
    """
    return _hasher.verify_and_update(senha, senha_hash)


def gerar_token_acesso(id_usuario: uuid.UUID, id_sessao: uuid.UUID) -> str:
    """Assina o id do usuário (sub) e o id da sessão (sid).

    O prazo do JWT é folgado de propósito. Quem manda na expiração é a sessão:
    24 horas sem uso, ou o logout.

    Args:
        id_usuario (uuid.UUID): Id do usuário, gravado em ``sub``.
        id_sessao (uuid.UUID): Id da sessão de login, gravado em ``sid``.

    Returns:
        str: Token JWT assinado com HS256, válido por 7 dias.
    """
    expira = agora_utc() + timedelta(days=7)
    payload = {"sub": str(id_usuario), "sid": str(id_sessao), "exp": expira}
    token = jwt.encode(payload, segredo_jwt(), algorithm=_ALGORITMO)
    if isinstance(token, bytes):
        return token.decode("utf-8")
    return token


def ler_token_acesso(token: str) -> dict:
    """Valida assinatura e prazo do JWT e devolve o payload.

    Args:
        token (str): Token JWT recebido.

    Returns:
        dict: Payload decodificado, contendo ao menos ``sub`` e ``sid``.

    Raises:
        TokenInvalido: Se o token não decodificar ou não tiver ``sub`` e ``sid``.
    """
    try:
        dados = jwt.decode(token, segredo_jwt(), algorithms=[_ALGORITMO])
    except jwt.PyJWTError as exc:
        raise TokenInvalido("Token inválido.") from exc
    if "sub" not in dados or "sid" not in dados:
        raise TokenInvalido("Token inválido.")
    return dados


def gerar_codigo_login() -> str:
    """Código numérico de 6 dígitos, sorteado com o gerador seguro do sistema.

    Returns:
        str: Código de 6 dígitos, com zeros à esquerda.
    """
    return f"{secrets.randbelow(10 ** TAMANHO_CODIGO_LOGIN):0{TAMANHO_CODIGO_LOGIN}d}"


def calcular_hash_codigo_login(id_usuario: uuid.UUID, codigo: str) -> str:
    """HMAC do código, ligado ao usuário. O código em si nunca vai para o banco.

    Com só 1 milhão de combinações, nenhum hash esconde o código de quem tem o
    banco. A proteção real é o prazo curto, o uso único e o bloqueio por tentativas.

    Args:
        id_usuario (uuid.UUID): Id do usuário ao qual o código pertence.
        codigo (str): Código de login em texto puro.

    Returns:
        str: HMAC-SHA256 em hexadecimal, assinado com a chave do JWT.
    """
    mensagem = f"login:{id_usuario}:{codigo}".encode("utf-8")
    return hmac.new(segredo_jwt().encode("utf-8"), mensagem, hashlib.sha256).hexdigest()


def codigo_login_confere(hash_guardado: str, id_usuario: uuid.UUID, codigo: str) -> bool:
    """Compara o hash guardado com o do código informado, em tempo constante.

    Args:
        hash_guardado (str): Hash do código guardado no banco.
        id_usuario (uuid.UUID): Id do usuário dono do código.
        codigo (str): Código informado pelo usuário.

    Returns:
        bool: ``True`` se o código confere.
    """
    return hmac.compare_digest(hash_guardado, calcular_hash_codigo_login(id_usuario, codigo))
