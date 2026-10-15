import smtplib
from email.message import EmailMessage

from core.parametros import (
    codigo_login_validade_minutos,
    smtp_email,
    smtp_host,
    smtp_porta,
    smtp_senha_app,
)

# Sem prazo, um servidor de e-mail que não responde prenderia o login para sempre.
TIMEOUT_SMTP_SEGUNDOS = 15


def enviar_codigo_login(destinatario: str, codigo: str) -> None:
    remetente = smtp_email()
    senha_app = smtp_senha_app()

    if not remetente or not senha_app:
        raise RuntimeError(
            "As configurações de envio de e-mail não foram definidas."
        )

    mensagem = EmailMessage()
    mensagem["Subject"] = "Código de confirmação - SimpleMark"
    mensagem["From"] = remetente
    mensagem["To"] = destinatario
    mensagem.set_content(
        f"""Olá!

Seu código de confirmação de login no SimpleMark é: {codigo}

Ele é válido por {codigo_login_validade_minutos()} minutos e pode ser utilizado apenas uma vez.

Se você não tentou entrar na sua conta, ignore este e-mail.
"""
    )

    with smtplib.SMTP_SSL(smtp_host(), smtp_porta(), timeout=TIMEOUT_SMTP_SEGUNDOS) as servidor:
        servidor.login(remetente, senha_app)
        servidor.send_message(mensagem)
