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