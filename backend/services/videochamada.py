"""Videochamada (Jitsi Meet) da consulta: geração do link, reagendamento, cancelamento e e-mails.

Fluxo:
- O link é gerado no próprio backend, sem chamada externa, na mesma
  requisição que confirma a consulta. Só o e-mail ao paciente vai para
  segundo plano.
- Consulta ativa sem link (antiga, ou cujo link não chegou a ser gravado)
  recebe o link sob demanda quando o profissional ou o paciente o consultam,
  ou pelo reprocessamento, que também reenvia o e-mail.
- Reagendar (só o profissional) mantém o mesmo link e avisa o paciente da nova data.
- Cancelar (profissional ou paciente) esconde o link da API e avisa o paciente.
  O Jitsi não tem como "fechar" a sala: a proteção é o link deixar de ser
  exibido e o nome da sala ser imprevisível.
- Cada envio de e-mail tem retentativas com backoff exponencial.

Um link por consulta: a linha fica travada (SELECT ... FOR UPDATE) enquanto o
link é gravado, um link existente nunca é trocado e o banco tem índice único
em meet_link.

Sala: "simplemark-" + 16 bytes aleatórios (secrets). Nada de id da consulta,
nome ou outro dado pessoal, porque quem souber o nome da sala consegue entrar.

Logs: só id da consulta, etapa e tipo do erro. Sem nome, e-mail, link ou dado clínico.
"""

import logging
import secrets
import time as relogio
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from core.excecoes import ErroNegocio
from core.integracoes import (
    FUSO_CONSULTAS,
    jitsi_base_url,
    videochamada_backoff_segundos,
    videochamada_tentativas,
)
from core.tempo import agora_local, agora_utc
from database.connection import SessionLocal
from models.models import Consulta, Usuario
from repositories import videochamada as repositorio
from services.envio_email import (
    DadosEmailConsulta,
    ErroEnvioEmail,
    email_cancelamento,
    email_confirmacao,
    email_reagendamento,
    enviar_email,
)

logger = logging.getLogger("simplemark.videochamada")

PREFIXO_SALA = "simplemark-"
BYTES_ALEATORIOS_SALA = 16  # 128 bits: inviável de adivinhar

STATUS_CONSULTA_CANCELADA = "cancelada"
# O banco tem as duas grafias: "cancelado"/"realizado" vêm do confirmar-consulta.
STATUS_CANCELADOS = {"cancelada", "cancelado"}
STATUS_REALIZADOS = {"realizada", "realizado"}

# Pontos de troca usados pelos testes para injetar banco e SMTP falsos.
fabrica_sessao = SessionLocal
remetente_email = enviar_email
esperar = relogio.sleep


def gerar_link_sala() -> str:
    """Link de uma sala nova e imprevisível no servidor Jitsi configurado (JITSI_BASE_URL)."""
    return f"{jitsi_base_url()}/{PREFIXO_SALA}{secrets.token_urlsafe(BYTES_ALEATORIOS_SALA)}"


# ---------------------------------------------------------------------------
# Apoio
# ---------------------------------------------------------------------------


def _momento(data_consulta: date, hora: time) -> datetime:
    return datetime.combine(data_consulta, hora, tzinfo=ZoneInfo(FUSO_CONSULTAS))


def inicio_da_consulta(consulta: Consulta) -> datetime:
    """Início da consulta no fuso America/Sao_Paulo."""
    return _momento(consulta.data, consulta.hora)


def _usuario_paciente(consulta: Consulta) -> Usuario:
    return consulta.paciente.usuario


def _usuario_profissional(consulta: Consulta) -> Usuario:
    return consulta.profissional_especialidade.profissional.usuario


def eh_profissional_da_consulta(usuario: Usuario, consulta: Consulta) -> bool:
    """True se o usuário é o profissional responsável pela consulta."""
    profissional = usuario.profissional
    return (
        profissional is not None
        and consulta.profissional_especialidade.id_profissional == profissional.id_profissional
    )


def eh_paciente_da_consulta(usuario: Usuario, consulta: Consulta) -> bool:
    """True se o usuário é o paciente da consulta."""
    paciente = usuario.paciente
    return paciente is not None and consulta.id_paciente == paciente.id_paciente


def _ativa(consulta: Consulta) -> bool:
    """Consulta que ainda vai acontecer: nem cancelada nem realizada."""
    return consulta.status not in STATUS_CANCELADOS | STATUS_REALIZADOS


def _dados_email(consulta: Consulta) -> DadosEmailConsulta:
    paciente = _usuario_paciente(consulta)
    link = None if consulta.status in STATUS_CANCELADOS else consulta.meet_link
    return DadosEmailConsulta(
        email_paciente=paciente.email,
        nome_paciente=paciente.nome,
        nome_profissional=_usuario_profissional(consulta).nome,
        inicio=inicio_da_consulta(consulta),
        meet_link=link,
    )


def _com_retentativas(acao, etapa: str, id_consulta: int):
    """Executa a ação com retentativas e backoff exponencial (2s, 4s, 8s...).

    Só repete falhas de envio de e-mail; na última, relança o erro.
    """
    tentativas = videochamada_tentativas()
    espera = videochamada_backoff_segundos()
    for tentativa in range(1, tentativas + 1):
        try:
            return acao()
        except ErroEnvioEmail as erro:
            logger.warning(
                "Consulta %s: %s falhou (tentativa %s/%s): %s",
                id_consulta, etapa, tentativa, tentativas, erro,
            )
            if tentativa == tentativas:
                raise
            esperar(espera * 2 ** (tentativa - 1))


def _enviar(mensagem, etapa: str, id_consulta: int) -> bool:
    """Envia o e-mail com retentativas. Falha final só fica no log: não desfaz a consulta."""
    try:
        _com_retentativas(lambda: remetente_email(mensagem), etapa, id_consulta)
    except ErroEnvioEmail:
        logger.error("Consulta %s: %s não enviado após todas as tentativas.", id_consulta, etapa)
        return False
    logger.info("Consulta %s: %s enviado.", id_consulta, etapa)
    return True


# ---------------------------------------------------------------------------
# Geração do link
# ---------------------------------------------------------------------------


def _atribuir_link(consulta: Consulta) -> bool:
    """Grava um link novo na consulta ativa que ainda não tem. Não faz commit.

    True se atribuiu agora. Um link existente nunca é trocado.
    """
    if consulta.meet_link or not _ativa(consulta):
        return False
    consulta.meet_link = gerar_link_sala()
    consulta.data_geracao_link = agora_utc()
    logger.info("Consulta %s: link da videochamada gerado.", consulta.id_consulta)
    return True


def garantir_link(db: Session, id_consulta: int) -> bool:
    """Gera e grava o link da consulta, se ela estiver ativa e ainda não tiver um.

    A linha fica travada até o commit, então duas chamadas simultâneas não
    gravam links diferentes. True se gerou agora.
    """
    consulta = repositorio.buscar_para_atualizar(db, id_consulta)
    if consulta is None or not _atribuir_link(consulta):
        db.rollback()
        return False
    db.commit()
    return True


# ---------------------------------------------------------------------------
# Tarefas em segundo plano (BackgroundTasks): só e-mail. Cada uma abre sua sessão.
# ---------------------------------------------------------------------------


def enviar_email_confirmacao(id_consulta: int) -> None:
    """Manda ao paciente o e-mail de confirmação com o link.

    Se o link ainda não existir (ex.: falhou ao gravar na requisição), gera aqui.
    Consulta cancelada ou realizada não recebe o e-mail.
    """
    db = fabrica_sessao()
    try:
        garantir_link(db, id_consulta)
        consulta = repositorio.buscar_com_participantes(db, id_consulta)
        if consulta is None or not _ativa(consulta) or not consulta.meet_link:
            logger.info("Consulta %s: sem videochamada ativa; e-mail de confirmação não enviado.", id_consulta)
            return
        _enviar(email_confirmacao(_dados_email(consulta)), "e-mail de confirmação", id_consulta)
    except Exception:
        logger.exception("Consulta %s: erro inesperado ao enviar a confirmação.", id_consulta)
    finally:
        db.close()


def enviar_email_reagendamento(id_consulta: int, data_anterior: date, hora_anterior: time) -> None:
    """Avisa o paciente da nova data, com o mesmo link."""
    db = fabrica_sessao()
    try:
        consulta = repositorio.buscar_com_participantes(db, id_consulta)
        if consulta is None:
            return
        mensagem = email_reagendamento(_dados_email(consulta), _momento(data_anterior, hora_anterior))
        _enviar(mensagem, "e-mail de reagendamento", id_consulta)
    except Exception:
        logger.exception("Consulta %s: erro inesperado ao enviar o reagendamento.", id_consulta)
    finally:
        db.close()


def enviar_email_cancelamento(id_consulta: int) -> None:
    """Avisa o paciente do cancelamento (o e-mail não leva o link)."""
    db = fabrica_sessao()
    try:
        consulta = repositorio.buscar_com_participantes(db, id_consulta)
        if consulta is None:
            return
        _enviar(email_cancelamento(_dados_email(consulta)), "e-mail de cancelamento", id_consulta)
    except Exception:
        logger.exception("Consulta %s: erro inesperado ao enviar o cancelamento.", id_consulta)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Regras chamadas pelas rotas
# ---------------------------------------------------------------------------


def gerar_link_nova_consulta(db: Session, id_consulta: int) -> None:
    """Gera o link logo após a consulta ser confirmada.

    Uma falha aqui não desfaz a consulta, que já foi gravada: o link é gerado
    de novo na tarefa do e-mail ou quando alguém consultar a videochamada.
    """
    try:
        garantir_link(db, id_consulta)
    except Exception:
        db.rollback()
        logger.exception("Consulta %s: falha ao gravar o link; será gerado sob demanda.", id_consulta)


def _consulta_do_participante(db: Session, id_consulta: int, usuario: Usuario) -> Consulta:
    """Consulta travada para alteração, só se o usuário for o profissional ou o paciente dela.

    Para qualquer outra pessoa responde 404, sem revelar se a consulta existe.
    """
    consulta = repositorio.buscar_para_atualizar(db, id_consulta)
    if consulta is None or not (
        eh_profissional_da_consulta(usuario, consulta) or eh_paciente_da_consulta(usuario, consulta)
    ):
        db.rollback()
        raise ErroNegocio("Consulta não encontrada.", 404)
    return consulta


def consultar_videochamada(db: Session, id_consulta: int, usuario: Usuario) -> tuple[Consulta, bool]:
    """Consulta com os dados da videochamada, visível só ao profissional e ao paciente dela.

    Consulta ativa sem link (ex.: criada antes desta integração) ganha o link
    agora. Devolve a consulta e se o link acabou de ser gerado.
    """
    consulta = repositorio.buscar_com_participantes(db, id_consulta)
    if consulta is None or not (
        eh_profissional_da_consulta(usuario, consulta) or eh_paciente_da_consulta(usuario, consulta)
    ):
        raise ErroNegocio("Consulta não encontrada.", 404)
    gerado_agora = False
    if _ativa(consulta) and not consulta.meet_link:
        gerado_agora = garantir_link(db, id_consulta)
        db.refresh(consulta)
    return consulta, gerado_agora


def reprocessar(db: Session, id_consulta: int, usuario: Usuario) -> Consulta:
    """Garante o link da consulta ativa (gera se faltar). A rota reenvia o e-mail de confirmação.

    Serve para consultas antigas, para link que não chegou a ser gravado e
    para e-mail que não chegou ao paciente.
    """
    consulta = _consulta_do_participante(db, id_consulta, usuario)
    if not _ativa(consulta):
        db.rollback()
        raise ErroNegocio("Esta consulta não tem videochamada para reprocessar.")
    _atribuir_link(consulta)
    db.commit()
    db.refresh(consulta)
    logger.info("Consulta %s: reprocessamento da videochamada solicitado.", id_consulta)
    return consulta


def reagendar(db: Session, id_consulta: int, usuario: Usuario, nova_data: date, nova_hora: time) -> tuple[Consulta, date, time]:
    """Muda data e hora da consulta. Só o profissional responsável pode reagendar.

    O novo horário tem de estar na agenda do profissional (data_horario), livre
    e no futuro. O link continua o mesmo (se não houver, é gerado agora).
    Devolve a consulta e a data/hora anteriores.
    """
    consulta = _consulta_do_participante(db, id_consulta, usuario)
    try:
        if not eh_profissional_da_consulta(usuario, consulta):
            raise ErroNegocio("Somente o profissional responsável pode reagendar a consulta.", 403)
        if consulta.status in STATUS_CANCELADOS:
            raise ErroNegocio("Não é possível reagendar uma consulta cancelada.")
        if consulta.status in STATUS_REALIZADOS:
            raise ErroNegocio("Não é possível reagendar uma consulta já realizada.")
        if (consulta.data, consulta.hora) == (nova_data, nova_hora):
            raise ErroNegocio("A nova data e hora são iguais às atuais.")
        if datetime.combine(nova_data, nova_hora) <= agora_local():
            raise ErroNegocio("A nova data e hora devem estar no futuro.")

        horario = repositorio.buscar_horario(db, consulta.id_esp_prof, nova_data, nova_hora)
        if horario is None:
            raise ErroNegocio("O novo horário não existe na agenda do profissional.")
        if horario.ocupado or repositorio.horario_tem_outra_consulta(
            db, consulta.id_esp_prof, nova_data, nova_hora, consulta.id_consulta
        ):
            raise ErroNegocio("O novo horário já está ocupado.", 409)
    except ErroNegocio:
        db.rollback()
        raise

    data_anterior, hora_anterior = consulta.data, consulta.hora
    consulta.data = nova_data
    consulta.hora = nova_hora
    _atribuir_link(consulta)
    db.commit()
    db.refresh(consulta)
    logger.info("Consulta %s: reagendada pelo profissional.", id_consulta)
    return consulta, data_anterior, hora_anterior


def cancelar(db: Session, id_consulta: int, usuario: Usuario) -> Consulta:
    """Cancela a consulta (status "cancelada"). Profissional ou paciente da consulta podem cancelar.

    O link fica gravado (auditoria), mas deixa de ser exibido pela API.
    """
    consulta = _consulta_do_participante(db, id_consulta, usuario)
    if consulta.status in STATUS_CANCELADOS:
        db.rollback()
        raise ErroNegocio("A consulta já está cancelada.")
    if consulta.status in STATUS_REALIZADOS:
        db.rollback()
        raise ErroNegocio("Não é possível cancelar uma consulta já realizada.")

    consulta.status = STATUS_CONSULTA_CANCELADA
    db.commit()
    db.refresh(consulta)
    logger.info("Consulta %s: cancelada.", id_consulta)
    return consulta
