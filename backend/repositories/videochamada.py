"""Acesso ao banco usado pela videochamada (Jitsi Meet) da consulta. Não aplica regra de negócio."""

from datetime import date, time

from sqlalchemy.orm import Session, joinedload

from models.models import Consulta, DataHorario, Paciente, Profissional, ProfissionalEspecialidade

# Mesmos status que prendem o horário na busca de profissionais, nas duas
# grafias que existem no banco ("agendado" vem do confirmar-consulta).
STATUS_QUE_OCUPAM = ("agendada", "agendado", "confirmada", "realizada", "realizado", "em andamento")


def buscar_para_atualizar(db: Session, id_consulta: int) -> Consulta | None:
    """Consulta pelo id com a linha travada até o commit (SELECT ... FOR UPDATE).

    A trava impede que duas requisições gravem links diferentes na mesma
    consulta ao mesmo tempo: a segunda espera a primeira e relê a linha já
    com o link (populate_existing descarta o que a sessão tinha em memória).
    No SQLite dos testes o FOR UPDATE é ignorado.
    """
    return (
        db.query(Consulta)
        .filter(Consulta.id_consulta == id_consulta)
        .populate_existing()
        .with_for_update()
        .first()
    )


def buscar_com_participantes(db: Session, id_consulta: int) -> Consulta | None:
    """Consulta pelo id com paciente e profissional (e seus usuários) carregados, ou None."""
    return (
        db.query(Consulta)
        .filter(Consulta.id_consulta == id_consulta)
        .options(
            joinedload(Consulta.paciente).joinedload(Paciente.usuario),
            joinedload(Consulta.profissional_especialidade)
            .joinedload(ProfissionalEspecialidade.profissional)
            .joinedload(Profissional.usuario),
        )
        .first()
    )


def buscar_horario(db: Session, id_esp_prof: int, data_consulta: date, hora_inicio: time) -> DataHorario | None:
    """Horário da agenda do profissional que começa na data e hora informadas, ou None."""
    return (
        db.query(DataHorario)
        .filter(
            DataHorario.id_esp_prof == id_esp_prof,
            DataHorario.data_consulta == data_consulta,
            DataHorario.hora_inicio == hora_inicio,
        )
        .first()
    )


def horario_tem_outra_consulta(
    db: Session, id_esp_prof: int, data_consulta: date, hora: time, id_consulta: int
) -> bool:
    """True se outra consulta ativa já ocupa esse vínculo, data e hora."""
    return (
        db.query(Consulta.id_consulta)
        .filter(
            Consulta.id_esp_prof == id_esp_prof,
            Consulta.data == data_consulta,
            Consulta.hora == hora,
            Consulta.id_consulta != id_consulta,
            Consulta.status.in_(STATUS_QUE_OCUPAM),
        )
        .first()
        is not None
    )

