"""Limites de login, sessão e recuperação de senha, e dados do envio de e-mail.

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


def ambiente() -> str:
    """desenvolvimento (padrão), teste ou producao."""
    return os.getenv("AMBIENTE", "desenvolvimento").strip().lower()


def recuperacao_codigo_minutos() -> int:
    return int(os.getenv("RECUPERACAO_CODIGO_MINUTOS", "5"))


def recuperacao_max_tentativas() -> int:
    return int(os.getenv("RECUPERACAO_MAX_TENTATIVAS", "5"))


def recuperacao_reenvio_segundos() -> int:
    """Tempo até poder pedir outro código. O padrão é a própria validade do código."""
    return int(os.getenv("RECUPERACAO_REENVIO_SEGUNDOS", "300"))


def recuperacao_redefinicao_minutos() -> int:
    """Tempo que a pessoa tem, depois de acertar o código, para digitar a nova senha."""
    return int(os.getenv("RECUPERACAO_REDEFINICAO_MINUTOS", "10"))


def smtp_host() -> str:
    """Vazio significa e-mail desligado: em desenvolvimento o código aparece no log da API."""
    return os.getenv("SMTP_HOST", "").strip()


def smtp_porta() -> int:
    return int(os.getenv("SMTP_PORTA", "587"))


def smtp_usuario() -> str:
    return os.getenv("SMTP_USUARIO", "").strip()


def smtp_senha() -> str:
    return os.getenv("SMTP_SENHA", "")


def smtp_usar_tls() -> bool:
    return os.getenv("SMTP_USAR_TLS", "false").strip().lower() in {"1", "true", "sim", "yes"}


def email_remetente() -> str:
    return os.getenv("EMAIL_REMETENTE", "Simple Mark <nao-responder@simplemark.local>").strip()
