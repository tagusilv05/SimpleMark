"""Limites de login e sessão.

Os valores padrão seguem a regra da parte 1. Se a variável existir no ambiente,
ela vale. O .env e o compose do grupo não são alterados: lá só entra DATABASE_URL.
"""

import os


def segredo_jwt() -> str:
    return os.getenv("SECRET_KEY", "simplemark-dev-secret-troque-em-producao")


def login_max_tentativas() -> int:
    return int(os.getenv("LOGIN_MAX_TENTATIVAS", "5"))


def login_bloqueio_minutos() -> int:
    return int(os.getenv("LOGIN_BLOQUEIO_MINUTOS", "60"))


def sessao_inatividade_horas() -> int:
    return int(os.getenv("SESSAO_INATIVIDADE_HORAS", "24"))

def base_url_validacao() -> str:
    """Base da URL pública que o QR-Code do documento clínico aponta."""
    return os.getenv("BASE_URL_VALIDACAO", "http://localhost:8080/api/v1")

def smtp_host() -> str:
    return os.getenv("SMTP_HOST", "smtp.gmail.com")


def smtp_porta() -> int:
    return int(os.getenv("SMTP_PORT", "465"))


def smtp_email() -> str:
    return os.getenv("SMTP_EMAIL", "")


def smtp_senha_app() -> str:
    return os.getenv("SMTP_SENHA_APP", "")


def codigo_login_validade_minutos() -> int:
    """Quanto tempo o código de confirmação do login vale, em minutos."""
    return int(os.getenv("CODIGO_LOGIN_VALIDADE_MINUTOS", "5"))
