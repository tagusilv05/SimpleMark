"""Consultas do paciente, com profissional, especialidade, avaliação e pagamento carregados."""

from datetime import date
from typing import Optional, Tuple

from sqlalchemy.orm import Session, joinedload

from models.models import Consulta, DataHorario, Profissional, ProfissionalEspecialidade

# Consulta cancelada devolve o horário para a agenda; as demais o mantêm preso.
STATUS_QUE_OCUPAM = ("agendada", "confirmada", "realizada", "em andamento")


def _base_query(db: Session):
    """Query de consulta com profissional, especialidade, avaliação e pagamento."""
    return (
        db.query(Consulta)
        .options(
            joinedload(Consulta.profissional_especialidade)
            .joinedload(ProfissionalEspecialidade.profissional)
            .joinedload(Profissional.usuario),
            joinedload(Consulta.profissional_especialidade)
            .joinedload(ProfissionalEspecialidade.especialidade),
            joinedload(Consulta.avaliacao),
            joinedload(Consulta.pagamento),
        )
    )


def listar_por_paciente(
    db: Session,
    id_paciente: int,
    status: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    skip: int = 0,
    limit: int = 20,
) -> Tuple[list[Consulta], int]:
    """Página de consultas do paciente e o total sem paginação.

    Filtros opcionais por status e intervalo de datas; ordena da consulta mais
    recente para a mais antiga.
    """
    query = _base_query(db).filter(Consulta.id_paciente == id_paciente)

    if status:
        query = query.filter(Consulta.status == status)
    if data_inicio:
        query = query.filter(Consulta.data >= data_inicio)
    if data_fim:
        query = query.filter(Consulta.data <= data_fim)

    total = query.count()
    itens = (
        query.order_by(Consulta.data.desc(), Consulta.hora.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return itens, total


def buscar_por_id_e_paciente(
    db: Session, id_consulta: int, id_paciente: int
) -> Optional[Consulta]:
    """Consulta pelo id, só se pertencer ao paciente; senão None."""
    return (
        _base_query(db)
        .filter(
            Consulta.id_consulta == id_consulta,
            Consulta.id_paciente == id_paciente,
        )
        .first()
    )


def buscar_horario_para_agendar(db: Session, id_horario: int) -> Optional[DataHorario]:
    """Horário da agenda com profissional e especialidade, travado até o commit.

    O FOR UPDATE impede que dois pacientes agendem o mesmo horário ao mesmo tempo.
    """
    return (
        db.query(DataHorario)
        .options(
            joinedload(DataHorario.profissional_especialidade)
            .joinedload(ProfissionalEspecialidade.profissional)
            .joinedload(Profissional.usuario),
        )
        .filter(DataHorario.id_horario == id_horario)
        .with_for_update(of=DataHorario)
        .first()
    )


def existe_consulta_no_horario(db: Session, horario: DataHorario) -> bool:
    """Se já há consulta ativa no vínculo, data e hora do horário."""
    return (
        db.query(Consulta.id_consulta)
        .filter(
            Consulta.id_esp_prof == horario.id_esp_prof,
            Consulta.data == horario.data_consulta,
            Consulta.hora == horario.hora_inicio,
            Consulta.status.in_(STATUS_QUE_OCUPAM),
        )
        .first()
        is not None
    )


def criar_consulta_no_horario(db: Session, horario: DataHorario, id_paciente: int) -> Consulta:
    """Grava a consulta no horário e marca o horário como ocupado (sem commit)."""
    consulta = Consulta(
        id_paciente=id_paciente,
        id_esp_prof=horario.id_esp_prof,
        data=horario.data_consulta,
        hora=horario.hora_inicio,
        tipo="consulta",
        status="agendada",
        valor=horario.profissional_especialidade.valor_consulta,
    )
    db.add(consulta)
    horario.ocupado = True
    db.flush()
    return consulta
