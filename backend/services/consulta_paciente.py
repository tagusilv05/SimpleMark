from datetime import date
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.models import Consulta
from repositories.consulta_paciente import (
    buscar_por_id_e_paciente,
    listar_por_paciente,
)
from schemas.consulta_paciente import (
    AvaliacaoResumo,
    ConsultaPacienteResponse,
    ListaConsultasResponse,
    ProfissionalResumo,
)


def _to_response(consulta: Consulta) -> ConsultaPacienteResponse:
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
    consulta = buscar_por_id_e_paciente(db, id_consulta, id_paciente)
    if consulta is None:
        # Também retorna 404 para consultas de outros pacientes.
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "Consulta não encontrada."
        )
    return _to_response(consulta)
