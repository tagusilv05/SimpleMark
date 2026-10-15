"""Limites de login e sessão.

Os valores padrão seguem a regra da parte 1. Se a variável existir no ambiente,
ela vale. O .env e o compose do grupo não são alterados: lá só entra DATABASE_URL.
"""

import os


def segredo_jwt() -> str:
    """Chave de assinatura do JWT (SECRET_KEY), com valor de desenvolvimento como padrão."""
    return os.getenv("SECRET_KEY", "simplemark-dev-secret-troque-em-producao")


def login_max_tentativas() -> int:
    """Tentativas de login com falha antes do bloqueio (padrão 5)."""
    return int(os.getenv("LOGIN_MAX_TENTATIVAS", "5"))


def login_bloqueio_minutos() -> int:
    """Duração do bloqueio de login, em minutos (padrão 60)."""
    return int(os.getenv("LOGIN_BLOQUEIO_MINUTOS", "60"))


def sessao_inatividade_horas() -> int:
    """Horas sem uso até a sessão expirar (padrão 24)."""
    return int(os.getenv("SESSAO_INATIVIDADE_HORAS", "24"))

def base_url_validacao() -> str:
    """Base da URL pública que o QR-Code do documento clínico aponta."""
    return os.getenv("BASE_URL_VALIDACAO", "http://localhost:8080/api/v1")
