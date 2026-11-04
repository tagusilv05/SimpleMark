"""Envio por SMTP do e-mail com o código de recuperação de senha.

Usa a mesma configuração do e-mail do código de login (SMTP_HOST, SMTP_PORT,
SMTP_EMAIL e SMTP_SENHA_APP).
"""

import smtplib
from email.message import EmailMessage

from core.parametros import smtp_email, smtp_host, smtp_porta, smtp_senha_app

# Sem prazo, um servidor de e-mail que não responde prenderia o pedido para sempre.
TIMEOUT_SMTP_SEGUNDOS = 15


def enviar_codigo_recuperacao(destinatario: str, codigo: str, validade_minutos: int) -> None:
    """Manda o código de recuperação de senha ao destinatário por SMTP com SSL.

    Levanta RuntimeError se o remetente ou a senha de app não estiverem
    configurados. Erros de conexão e de envio do smtplib sobem para quem chama.
    """
    remetente = smtp_email()
    senha_app = smtp_senha_app()

    if not remetente or not senha_app:
        raise RuntimeError("As configurações de envio de e-mail não foram definidas.")

    mensagem = EmailMessage()
    mensagem["Subject"] = "Recuperação de senha - SimpleMark"
    mensagem["From"] = remetente
    mensagem["To"] = destinatario
    mensagem.set_content(
        f"""Olá!

Recebemos um pedido para redefinir a senha da sua conta no SimpleMark.

Seu código de recuperação é: {codigo}

Ele é válido por {validade_minutos} minutos e pode ser utilizado apenas uma vez.

Se você não pediu a redefinição, ignore este e-mail: sua senha continua a mesma.
"""
    )

    with smtplib.SMTP_SSL(smtp_host(), smtp_porta(), timeout=TIMEOUT_SMTP_SEGUNDOS) as servidor:
        servidor.login(remetente, senha_app)
        servidor.send_message(mensagem)