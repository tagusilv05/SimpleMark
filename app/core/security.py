# Arquivo criado por Victor
import jwt
from fastapi_users.jwt import decode_jwt, generate_jwt
from fastapi_users.password import PasswordHelper

from app.core.config import settings

# Audiência gravada no token para que um JWT de outro sistema não seja aceito aqui.
AUDIENCIA_TOKEN = ["simplemark:auth"]

_senhas = PasswordHelper()


class TokenInvalido(Exception):
    """Token ausente, adulterado ou com formato que esta API não emite."""


def gerar_hash_senha(senha: str) -> str:
    """Hash com Argon2 e salt, conforme o RNF12.

    O PasswordHelper do FastAPI Users usa Argon2 como algoritmo principal
    e ainda reconhece bcrypt na verificação.
    """
    return _senhas.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> tuple[bool, str | None]:
    """Confere a senha digitada contra o hash gravado.

    Passo a passo:
    1. O PasswordHelper recalcula o hash com o salt que já está dentro do texto gravado.
    2. Compara sem revelar em quanto tempo a senha divergiu.
    3. Devolve um par: se a senha confere, e um hash novo quando o algoritmo antigo
       precisa ser atualizado. Hoje o segundo valor costuma vir vazio.
    """
    return _senhas.verify_and_update(senha, senha_hash)


def gerar_token_acesso(id_usuario: int) -> str:
    """Monta o JWT que o cliente manda no cabeçalho Authorization.

    Passo a passo:
    1. Coloca o id do usuário em sub, como texto.
    2. Grava a audiência simplemark:auth para recusar token de outro sistema.
    3. Assina com SECRET_KEY, sem prazo neste token.
    4. Devolve o texto do token.
    """
    dados = {
        "sub": str(id_usuario),
        "aud": AUDIENCIA_TOKEN,
    }
    return generate_jwt(dados, settings.secret_key, lifetime_seconds=None)


def ler_token_acesso(token: str) -> dict:
    """Lê o JWT e devolve o id do usuário, ou recusa o token.

    Passo a passo:
    1. decode_jwt confere a assinatura com SECRET_KEY.
    2. Confere se a audiência é simplemark:auth.
    3. Se a assinatura, o formato ou a audiência falhar, vira TokenInvalido.
    4. Se passar, devolve o dicionário com sub.
    """
    try:
        return decode_jwt(token, settings.secret_key, AUDIENCIA_TOKEN)
    except jwt.PyJWTError as exc:
        raise TokenInvalido from exc
