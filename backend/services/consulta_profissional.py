from datetime import date
from sqlalchemy.orm import Session, joinedload
from models.models import Consulta, Paciente, Profissional, ProfissionalEspecialidade
from schemas.consulta_profissional import ConsultaProfissionalOut, PacienteConsultaOut


def _buscar_consultas_do_profissional(
    db: Session,
    id_profissional: int,
    status: str | None,
    data_inicio: date | None,
    data_fim: date | None,
) -> list[Consulta]:
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


def _para_schema(c: Consulta) -> ConsultaProfissionalOut:
    usuario = c.paciente.usuario
    return ConsultaProfissionalOut(
        id_consulta=c.id_consulta,
        data=c.data,
        hora=c.hora,
        tipo=c.tipo,
        status=c.status,
        especialidade=c.profissional_especialidade.especialidade.especialidade,
        paciente=PacienteConsultaOut(
            id_paciente=c.paciente.id_paciente,
            nome=usuario.nome,
            telefone=usuario.telefone,
            email=usuario.email,
            data_nascimento=usuario.data_nascimento,
            genero=usuario.genero,
        ),
    )


def listar_consultas_do_profissional(
    db: Session,
    id_profissional: int,
    status: str | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
) -> list[ConsultaProfissionalOut] | None:
    profissional = (
        db.query(Profissional)
        .filter(Profissional.id_profissional == id_profissional)
        .first()
    )
    if profissional is None:
        return None  # o router converte em 404

    consultas = _buscar_consultas_do_profissional(
        db, id_profissional, status, data_inicio, data_fim
    )
    return [_para_schema(c) for c in consultas]