"""Listagem e detalhe das consultas do paciente."""

from datetime import date
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.tempo import agora_local
from models.models import Consulta
from repositories.consulta_paciente import (
    buscar_horario_para_agendar,
    buscar_por_id_e_paciente,
    criar_consulta_no_horario,
    existe_consulta_no_horario,
    listar_por_paciente,
)
from schemas.consulta_paciente import (
    AvaliacaoResumo,
    ConsultaPacienteResponse,
    ListaConsultasResponse,
    ProfissionalResumo,
)
from schemas.videochamada import link_visivel


def _to_response(consulta: Consulta) -> ConsultaPacienteResponse:
    """Monta a resposta da consulta para o paciente.

    Inclui o profissional, o status do pagamento, a avaliação, se ainda pode
    avaliar e o link da videochamada quando visível.
    """
    profissional_especialidade = consulta.profissional_especialidade
    profissional = profissional_especialidade.profissional

    return ConsultaPacienteResponse(
        id_consulta=consulta.id_consulta,
        data=consulta.data,
        hora=consulta.hora,
        tipo=consulta.tipo,
        status=consulta.status,
        valor=consulta.valor,
        profissional=ProfissionalResumo(
            id_profissional=profissional.id_profissional,
            nome=profissional.usuario.nome,
            path_imagem=profissional.path_imagem,
            especialidade=profissional_especialidade.especialidade.especialidade,
        ),
        pagamento_status=consulta.pagamento.status if consulta.pagamento else None,
        avaliacao=(
            AvaliacaoResumo(
                avaliacao=consulta.avaliacao.avaliacao,
                feedback=consulta.avaliacao.feedback,
            )
            if consulta.avaliacao
            else None
        ),
        pode_avaliar=(
            consulta.status == "realizada" and consulta.avaliacao is None
        ),
        meet_link=link_visivel(consulta),
    )


def listar_consultas(
    db: Session,
    id_paciente: int,
    status_consulta: Optional[str],
    data_inicio: Optional[date],
    data_fim: Optional[date],
    skip: int,
    limit: int,
) -> ListaConsultasResponse:
    """Consultas do paciente com filtros de status e período, paginadas.

    Levanta HTTPException 400 se data_inicio for maior que data_fim.
    """
    if data_inicio and data_fim and data_inicio > data_fim:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "data_inicio não pode ser maior que data_fim.",
        )

    consultas, total = listar_por_paciente(
        db, id_paciente, status_consulta, data_inicio, data_fim, skip, limit
    )
    return ListaConsultasResponse(
        total=total,
        itens=[_to_response(consulta) for consulta in consultas],
    )


def detalhar_consulta(
    db: Session, id_consulta: int, id_paciente: int
) -> ConsultaPacienteResponse:
    """Detalhe de uma consulta do paciente; 404 se não existir ou for de outro."""
    consulta = buscar_por_id_e_paciente(db, id_consulta, id_paciente)
    if consulta is None:
        # Também retorna 404 para consultas de outros pacientes.
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "Consulta não encontrada."
        )
    return _to_response(consulta)


def agendar_consulta(
    db: Session, id_horario: int, id_paciente: int
) -> Consulta:
    """Agenda a consulta do paciente num horário livre da agenda do profissional.

    Profissional, especialidade, data, hora e valor saem do próprio horário, então
    o paciente não escolhe o preço. Responde 404 se o horário não existir e 409 se
    ele já passou, já foi ocupado ou o profissional está inativo.
    """
    horario = buscar_horario_para_agendar(db, id_horario)
    if horario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Horário não encontrado.")

    agora = agora_local()
    ja_passou = horario.data_consulta < agora.date() or (
        horario.data_consulta == agora.date() and horario.hora_inicio < agora.time()
    )
    profissional_ativo = horario.profissional_especialidade.profissional.usuario.status

    if ja_passou or not profissional_ativo:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Este horário não está mais disponível.")
    if horario.ocupado or existe_consulta_no_horario(db, horario):
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Este horário acabou de ser reservado. Escolha outro.")

    try:
        consulta = criar_consulta_no_horario(db, horario, id_paciente)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return consulta
