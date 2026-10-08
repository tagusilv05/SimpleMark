# Consulta ao banco usada na busca de profissionais. Não aplica regra de
# negócio: recebe o filtro já normalizado pelo service e devolve as linhas.
from datetime import datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from models.models import (
    Consulta,
    DataHorario,
    Especialidade,
    Profissional,
    ProfissionalEspecialidade,
    Usuario,
)
from schemas.busca_profissional import FiltroBuscaProfissional

# Consulta cancelada devolve o horário para a agenda; as demais o mantêm preso.
_STATUS_QUE_OCUPAM = ("agendada", "confirmada", "realizada", "em andamento")


def _horario_ja_agendado():
    """Horário com consulta marcada em cima, mesmo com a flag `ocupado` falsa.

    A flag é o caminho normal, mas ela depende de quem agenda lembrar de marcá-la.
    Este EXISTS fecha a brecha: o paciente não enxerga um horário que já tem
    consulta naquele vínculo, data e hora.
    """
    return (
        select(Consulta.id_consulta)
        .where(
            Consulta.id_esp_prof == DataHorario.id_esp_prof,
            Consulta.data == DataHorario.data_consulta,
            Consulta.hora == DataHorario.hora_inicio,
            Consulta.status.in_(_STATUS_QUE_OCUPAM),
        )
        .exists()
    )


def _aplicar_especialidade(query, filtro: FiltroBuscaProfissional):
    if filtro.id_especialidade is not None:
        query = query.filter(
            ProfissionalEspecialidade.id_especialidade == filtro.id_especialidade
        )
    if filtro.especialidade:
        # Busca por parte do nome, sem diferenciar maiúsculas nem acentuação
        # digitada pelo paciente ("cardio" encontra "Cardiologia").
        query = query.filter(Especialidade.especialidade.ilike(f"%{filtro.especialidade}%"))
    return query


def _aplicar_periodo(query, filtro: FiltroBuscaProfissional, momento: datetime):
    if filtro.data_inicio is not None:
        query = query.filter(DataHorario.data_consulta >= filtro.data_inicio)
    if filtro.data_fim is not None:
        query = query.filter(DataHorario.data_consulta <= filtro.data_fim)
    if filtro.hora_inicio is not None:
        query = query.filter(DataHorario.hora_inicio >= filtro.hora_inicio)
    if filtro.hora_fim is not None:
        query = query.filter(DataHorario.hora_fim <= filtro.hora_fim)

    # Hoje só vale o que ainda não começou: um horário das 8h não é vaga às 14h.
    return query.filter(
        or_(
            DataHorario.data_consulta > momento.date(),
            DataHorario.hora_inicio >= momento.time(),
        )
    )


def _aplicar_valor(query, filtro: FiltroBuscaProfissional):
    if filtro.valor_min is not None:
        query = query.filter(ProfissionalEspecialidade.valor_consulta >= filtro.valor_min)
    if filtro.valor_max is not None:
        query = query.filter(ProfissionalEspecialidade.valor_consulta <= filtro.valor_max)
    return query


def buscar_horarios_disponiveis(
    db: Session,
    filtro: FiltroBuscaProfissional,
    momento: datetime,
) -> list[DataHorario]:
    """Horários livres que atendem ao filtro, já com profissional e especialidade.

    O join com data_horario também serve de filtro: profissional sem agenda
    aberta no período simplesmente não aparece na busca.
    """
    caminho_vinculo = joinedload(DataHorario.profissional_especialidade)
    query = (
        db.query(DataHorario)
        .join(
            ProfissionalEspecialidade,
            DataHorario.id_esp_prof == ProfissionalEspecialidade.id_esp_prof,
        )
        .join(
            Profissional,
            ProfissionalEspecialidade.id_profissional == Profissional.id_profissional,
        )
        .join(Usuario, Profissional.id_usuario == Usuario.id)
        .join(
            Especialidade,
            ProfissionalEspecialidade.id_especialidade == Especialidade.id_especialidade,
        )
        .filter(DataHorario.ocupado.is_(False))
        .filter(Usuario.status.is_(True))  # conta inativa não recebe agendamento
        .filter(~_horario_ja_agendado())
        .options(
            caminho_vinculo.joinedload(ProfissionalEspecialidade.profissional).joinedload(
                Profissional.usuario
            ),
            caminho_vinculo.joinedload(ProfissionalEspecialidade.especialidade),
            caminho_vinculo.joinedload(ProfissionalEspecialidade.conselho),
        )
    )

    query = _aplicar_especialidade(query, filtro)
    query = _aplicar_periodo(query, filtro, momento)
    query = _aplicar_valor(query, filtro)

    return query.order_by(
        Usuario.nome,
        DataHorario.data_consulta,
        DataHorario.hora_inicio,
    ).all()
