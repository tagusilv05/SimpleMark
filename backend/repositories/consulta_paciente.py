from datetime import date
from typing import Optional, Tuple

from sqlalchemy.orm import Session, joinedload

from models.models import Consulta, Profissional, ProfissionalEspecialidade


def _base_query(db: Session):
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
    return (
        _base_query(db)
        .filter(
            Consulta.id_consulta == id_consulta,
            Consulta.id_paciente == id_paciente,
        )
        .first()
    )
