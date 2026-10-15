"""Envio de e-mail por SMTP e os modelos das mensagens da teleconsulta ao paciente.

Usa só a biblioteca padrão (smtplib/email). O servidor vem das variáveis
SMTP_* de core/integracoes.py.

LGPD: as mensagens trazem apenas nome do paciente, nome do profissional, data,
hora e link. Nada de especialidade, queixa, diagnóstico ou outro dado clínico.
"""

import smtplib
from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage
from html import escape

from core.integracoes import (
    smtp_host,
    smtp_porta,
    smtp_remetente,
    smtp_senha,
    smtp_ssl,
    smtp_usar_tls,
    smtp_usuario,
)

_DIAS_SEMANA = (
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo",
)

_ORIENTACOES = (
    "Teste a câmera, o microfone e o fone de ouvido antes do horário.",
    "Entre na sala alguns minutos antes do início da consulta.",
    "Prefira um lugar reservado, silencioso e bem iluminado, com internet estável.",
)


class ErroEnvioEmail(Exception):
    """Falha ao enviar o e-mail. A mensagem não traz dado sensível."""


@dataclass
class DadosEmailConsulta:
    """O que as mensagens ao paciente precisam saber da consulta."""

    email_paciente: str
    nome_paciente: str
    nome_profissional: str
    inicio: datetime  # já no fuso America/Sao_Paulo
    meet_link: str | None = None


def formatar_data_hora(momento: datetime) -> str:
    """Ex.: "terça-feira, 20/01/2026 às 10:00 (horário de Brasília)"."""
    dia = _DIAS_SEMANA[momento.weekday()]
    return f"{dia}, {momento:%d/%m/%Y} às {momento:%H:%M} (horário de Brasília)"


def _montar(destinatario: str, assunto: str, paragrafos: list[str], dados: DadosEmailConsulta) -> EmailMessage:
    """Monta a mensagem em texto puro e HTML, com o link e as orientações quando houver link."""
    texto = [f"Olá, {dados.nome_paciente}!", "", *paragrafos]
    html = [f"<p>Olá, {escape(dados.nome_paciente)}!</p>"]
    html += [f"<p>{escape(p)}</p>" for p in paragrafos]

    if dados.meet_link:
        texto += ["", f"Link da videochamada: {dados.meet_link}", "", "Orientações:"]
        texto += [f"- {item}" for item in _ORIENTACOES]
        link = escape(dados.meet_link, quote=True)
        html.append(
            f'<p><strong>Link da videochamada:</strong> '
            f'<a href="{link}">{escape(dados.meet_link)}</a></p>'
        )
        html.append("<p><strong>Orientações:</strong></p><ul>")
        html += [f"<li>{escape(item)}</li>" for item in _ORIENTACOES]
        html.append("</ul>")

    rodape = "Esta é uma mensagem automática da SimpleMark. Não responda este e-mail."
    texto += ["", rodape]
    html.append(f"<p><small>{escape(rodape)}</small></p>")

    mensagem = EmailMessage()
    mensagem["Subject"] = assunto
    mensagem["From"] = smtp_remetente()
    mensagem["To"] = destinatario
    mensagem.set_content("\n".join(texto))
    mensagem.add_alternative("\n".join(html), subtype="html")
    return mensagem


def email_confirmacao(dados: DadosEmailConsulta) -> EmailMessage:
    """Consulta confirmada, com o link da videochamada."""
    return _montar(
        dados.email_paciente,
        "Sua teleconsulta está confirmada",
        [
            f"Sua teleconsulta com {dados.nome_profissional} está confirmada para "
            f"{formatar_data_hora(dados.inicio)}."
        ],
        dados,
    )


def email_reagendamento(dados: DadosEmailConsulta, inicio_anterior: datetime) -> EmailMessage:
    """Consulta movida para nova data; o link da videochamada continua o mesmo."""
    paragrafos = [
        f"Sua teleconsulta com {dados.nome_profissional}, que estava marcada para "
        f"{formatar_data_hora(inicio_anterior)}, foi reagendada.",
        f"Nova data: {formatar_data_hora(dados.inicio)}.",
    ]
    if dados.meet_link:
        paragrafos.append("O link da videochamada continua o mesmo.")
    else:
        paragrafos.append("O link da videochamada será enviado em outro e-mail assim que estiver pronto.")
    return _montar(dados.email_paciente, "Sua teleconsulta foi reagendada", paragrafos, dados)


def email_cancelamento(dados: DadosEmailConsulta) -> EmailMessage:
    """Consulta cancelada (sem link, que deixou de valer)."""
    sem_link = DadosEmailConsulta(
        email_paciente=dados.email_paciente,
        nome_paciente=dados.nome_paciente,
        nome_profissional=dados.nome_profissional,
        inicio=dados.inicio,
    )
    return _montar(
        dados.email_paciente,
        "Sua teleconsulta foi cancelada",
        [
            f"Sua teleconsulta com {dados.nome_profissional}, marcada para "
            f"{formatar_data_hora(dados.inicio)}, foi cancelada.",
            "Se precisar, você pode agendar um novo horário pela plataforma.",
        ],
        sem_link,
    )


def enviar_email(mensagem: EmailMessage) -> None:
    """Envia a mensagem pelo SMTP configurado. Qualquer falha vira ErroEnvioEmail."""
    host = smtp_host()
    if not host:
        raise ErroEnvioEmail("Envio de e-mail não configurado (SMTP_HOST).")
    try:
        if smtp_ssl():
            conexao = smtplib.SMTP_SSL(host, smtp_porta(), timeout=20)
        else:
            conexao = smtplib.SMTP(host, smtp_porta(), timeout=20)
        with conexao:
            if not smtp_ssl() and smtp_usar_tls():
                conexao.starttls()
            if smtp_usuario():
                conexao.login(smtp_usuario(), smtp_senha())
            conexao.send_message(mensagem)
    except (smtplib.SMTPException, OSError) as exc:
        raise ErroEnvioEmail(f"Falha no servidor de e-mail ({type(exc).__name__}).") from exc
