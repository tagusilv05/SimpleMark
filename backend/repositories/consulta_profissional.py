# services/consulta_service.py
"""Consultas da agenda do profissional."""

from datetime import date
from sqlalchemy.orm import Session, joinedload
from models import Consulta, Paciente, ProfissionalEspecialidade

def listar_consultas_do_profissional(
    db: Session,
    id_profissional: int,
    status: str | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
):
    """Consultas do profissional em todas as especialidades, com o paciente carregado.

    Filtros opcionais por status e intervalo de datas; ordena por data e hora
    crescentes.
    """
    query = (
        db.query(Consulta)
        .join(
            ProfissionalEspecialidade,
            Consulta.id_esp_prof == ProfissionalEspecialidade.id_esp_prof,
        )
        .filter(ProfissionalEspecialidade.id_profissional == id_profissional)
        .options(
            joinedload(Consulta.paciente).joinedload(Paciente.usuario),
            joinedload(Consulta.profissional_especialidade)
            .joinedload(ProfissionalEspecialidade.especialidade),
        )
    )

    if status:
        query = query.filter(Consulta.status == status)
    if data_inicio:
        query = query.filter(Consulta.data >= data_inicio)
    if data_fim:
        query = query.filter(Consulta.data <= data_fim)

    return query.order_by(Consulta.data, Consulta.hora).all()