"""Envio de e-mail por SMTP.

Sem SMTP_HOST configurado, em desenvolvimento o e-mail aparece no terminal da API
(modo desenvolvimento). Em produção, sem SMTP, nada é impresso: o erro vai para o log.
"""

import logging
import smtplib
import ssl
from email.message import EmailMessage

from core.parametros import (
    ambiente,
    email_remetente,
    smtp_host,
    smtp_porta,
    smtp_senha,
    smtp_usar_tls,
    smtp_usuario,
)

logger = logging.getLogger("simplemark.email")


def _mascarar(email: str) -> str:
    """maria@example.com vira m***@example.com, para o log não expor o e-mail inteiro."""
    local, _, dominio = email.partition("@")
    return f"{local[:1]}***@{dominio}"


def enviar_email(destinatario: str, assunto: str, texto: str) -> None:
    """Envia o e-mail sem nunca levantar erro.

    Roda depois da resposta da API. Se o envio falhar, a pessoa já recebeu a resposta
    padrão, e o motivo fica no log. Ela pode pedir um novo código depois do intervalo.
    """
    try:
        _enviar(destinatario, assunto, texto)
    except Exception:
        logger.exception("Não foi possível enviar o e-mail para %s.", _mascarar(destinatario))


def _enviar(destinatario: str, assunto: str, texto: str) -> None:
    if not smtp_host():
        if ambiente() == "producao":
            logger.error("SMTP_HOST não configurado. E-mail para %s não enviado.", _mascarar(destinatario))
            return
        print(
            "\n[MODO DESENVOLVIMENTO] SMTP_HOST não configurado. E-mail NÃO enviado.\n"
            f"Para: {destinatario}\nAssunto: {assunto}\n\n{texto}\n",
            flush=True,
        )
        return

    mensagem = EmailMessage()
    mensagem["From"] = email_remetente()
    mensagem["To"] = destinatario
    mensagem["Subject"] = assunto
    mensagem.set_content(texto)

    with smtplib.SMTP(smtp_host(), smtp_porta(), timeout=15) as servidor:
        if smtp_usar_tls():
            servidor.starttls(context=ssl.create_default_context())
        if smtp_usuario():
            servidor.login(smtp_usuario(), smtp_senha())
        servidor.send_message(mensagem)
