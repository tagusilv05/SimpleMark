"""Parâmetros das integrações: videochamada (Jitsi Meet) e envio de e-mail.

Tudo vem das variáveis de ambiente, no mesmo padrão de core/parametros.py.
Nenhuma credencial fica no código.
"""

import os

# Fuso em que a agenda (data_horario e consulta) é digitada e exibida.
FUSO_CONSULTAS = "America/Sao_Paulo"


def jitsi_base_url() -> str:
    """Endereço do servidor Jitsi onde as salas são abertas (padrão: o público, https://meet.jit.si).

    Trocar por um servidor Jitsi próprio é só mudar JITSI_BASE_URL.
    """
    return (os.getenv("JITSI_BASE_URL", "").strip() or "https://meet.jit.si").rstrip("/")


def videochamada_tentativas() -> int:
    """Quantas vezes cada envio de e-mail é tentado antes de desistir (padrão 3)."""
    return max(1, int(os.getenv("VIDEOCHAMADA_TENTATIVAS", "3")))


def videochamada_backoff_segundos() -> float:
    """Espera antes da 2ª tentativa; dobra a cada nova falha (padrão 2s: 2, 4, 8...)."""
    return float(os.getenv("VIDEOCHAMADA_BACKOFF_SEGUNDOS", "2"))


def smtp_host() -> str:
    """Servidor SMTP. Vazio desliga o envio (a falha é registrada em log)."""
    return os.getenv("SMTP_HOST", "").strip()


def smtp_porta() -> int:
    """Porta do servidor SMTP (padrão 587, STARTTLS)."""
    return int(os.getenv("SMTP_PORT", "587"))


def smtp_usuario() -> str:
    """Usuário de login no SMTP (vazio = servidor sem autenticação)."""
    return os.getenv("SMTP_USUARIO", "").strip()


def smtp_senha() -> str:
    """Senha (ou senha de app) do SMTP."""
    return os.getenv("SMTP_SENHA", "")


def smtp_remetente() -> str:
    """Endereço que aparece no "De" dos e-mails (padrão: o usuário do SMTP)."""
    return os.getenv("SMTP_REMETENTE", "").strip() or smtp_usuario()


def smtp_usar_tls() -> bool:
    """Liga o STARTTLS (padrão true). Com SMTP_SSL=true, usa SSL direto (porta 465)."""
    return os.getenv("SMTP_USAR_TLS", "true").strip().lower() in {"1", "true", "sim"}


def smtp_ssl() -> bool:
    """Conexão SSL desde o início (porta 465), em vez de STARTTLS."""
    return os.getenv("SMTP_SSL", "false").strip().lower() in {"1", "true", "sim"}
