"""Rotas da videochamada (Jitsi Meet) da consulta: link, reprocessamento, reagendamento e cancelamento.

Todas exigem login (Bearer). Só o profissional responsável e o paciente da
consulta enxergam o link; para qualquer outra pessoa a consulta "não existe" (404).
O link é gerado na própria requisição; só o envio de e-mail roda em segundo
plano, depois da resposta.
"""

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session

from dependencies.autenticacao import UsuarioAtual
from dependencies.database import get_db
from schemas.comum import MensagemResposta
from schemas.videochamada import OperacaoVideochamadaOutput, ReagendarConsultaInput, VideochamadaOutput
from services import videochamada as servico

router = APIRouter(prefix="/consultas", tags=["Videochamada da consulta"])

_ERROS = {
    401: {"model": MensagemResposta, "description": "Sem token ou sessão expirada."},
    404: {"model": MensagemResposta, "description": "Consulta inexistente ou de outra pessoa."},
}


@router.get(
    "/{id_consulta}/videochamada",
    response_model=VideochamadaOutput,
    summary="Ver o link da videochamada (Jitsi Meet) da consulta",
    responses=_ERROS,
)
def ver_videochamada(
    id_consulta: int,
    usuario: UsuarioAtual,
    tarefas: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Link da videochamada, para o profissional responsável ou o paciente da consulta.

    Consulta ativa ainda sem link (ex.: criada antes desta integração) ganha o
    link agora, e o paciente recebe o e-mail de confirmação com ele.
    """
    consulta, gerado_agora = servico.consultar_videochamada(db, id_consulta, usuario)
    if gerado_agora:
        tarefas.add_task(servico.enviar_email_confirmacao, consulta.id_consulta)
    return VideochamadaOutput.da_consulta(consulta)


@router.post(
    "/{id_consulta}/videochamada/reprocessar",
    response_model=OperacaoVideochamadaOutput,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Garantir o link e reenviar o e-mail da videochamada",
    responses={
        **_ERROS,
        400: {"model": MensagemResposta, "description": "Consulta cancelada ou realizada."},
    },
)
def reprocessar_videochamada(
    id_consulta: int,
    usuario: UsuarioAtual,
    tarefas: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Gera o link se a consulta ainda não tiver (nunca troca um existente) e
    reenvia ao paciente, em segundo plano, o e-mail de confirmação.

    Aceito para o profissional ou o paciente de uma consulta ativa.
    """
    consulta = servico.reprocessar(db, id_consulta, usuario)
    tarefas.add_task(servico.enviar_email_confirmacao, consulta.id_consulta)
    return OperacaoVideochamadaOutput(
        mensagem="Link da videochamada garantido. O e-mail ao paciente será reenviado.",
        consulta=VideochamadaOutput.da_consulta(consulta),
    )


@router.patch(
    "/{id_consulta}/reagendar",
    response_model=OperacaoVideochamadaOutput,
    summary="Reagendar a consulta (somente o profissional)",
    responses={
        **_ERROS,
        400: {"model": MensagemResposta, "description": "Consulta cancelada/realizada ou horário inválido."},
        403: {"model": MensagemResposta, "description": "Quem pediu não é o profissional da consulta."},
        409: {"model": MensagemResposta, "description": "Novo horário já ocupado."},
    },
)
def reagendar_consulta(
    id_consulta: int,
    dados: ReagendarConsultaInput,
    usuario: UsuarioAtual,
    tarefas: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Move a consulta para um horário livre da agenda do profissional.

    O link da videochamada continua o mesmo, e o paciente recebe um e-mail com
    a data antiga e a nova.
    """
    consulta, data_anterior, hora_anterior = servico.reagendar(db, id_consulta, usuario, dados.data, dados.hora)
    tarefas.add_task(servico.enviar_email_reagendamento, consulta.id_consulta, data_anterior, hora_anterior)
    return OperacaoVideochamadaOutput(
        mensagem="Consulta reagendada com sucesso.",
        consulta=VideochamadaOutput.da_consulta(consulta),
    )


@router.patch(
    "/{id_consulta}/cancelar",
    response_model=OperacaoVideochamadaOutput,
    summary="Cancelar a consulta",
    responses={
        **_ERROS,
        400: {"model": MensagemResposta, "description": "Consulta já cancelada ou já realizada."},
    },
)
def cancelar_consulta(
    id_consulta: int,
    usuario: UsuarioAtual,
    tarefas: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Cancela a consulta (profissional ou paciente dela) e avisa o paciente.

    O link deixa de ser devolvido pela API. A sala do Jitsi não pode ser
    fechada; a proteção é o link sumir e o nome da sala ser imprevisível.
    """
    consulta = servico.cancelar(db, id_consulta, usuario)
    tarefas.add_task(servico.enviar_email_cancelamento, consulta.id_consulta)
    return OperacaoVideochamadaOutput(
        mensagem="Consulta cancelada com sucesso.",
        consulta=VideochamadaOutput.da_consulta(consulta),
    )
