# Consultas usadas na emissão de receitas e atestados.
# Não aplica regra de negócio.
from sqlalchemy.orm import Session, joinedload

from models.models import Consulta, DocumentoClinico, Paciente, ProfissionalEspecialidade, Profissional


def _carregar_contexto():
    """Joins que a resposta do documento sempre precisa: paciente e profissional."""
    esp_prof = joinedload(Consulta.profissional_especialidade)
    return (
        joinedload(Consulta.paciente).joinedload(Paciente.usuario),
        esp_prof.joinedload(ProfissionalEspecialidade.profissional).joinedload(Profissional.usuario),
        esp_prof.joinedload(ProfissionalEspecialidade.especialidade),
        esp_prof.joinedload(ProfissionalEspecialidade.conselho),
    )


def buscar_consulta(db: Session, id_consulta: int) -> Consulta | None:
    return (
        db.query(Consulta)
        .filter(Consulta.id_consulta == id_consulta)
        .options(*_carregar_contexto())
        .first()
    )


def buscar_documento(db: Session, id_documento: int) -> DocumentoClinico | None:
    return (
        db.query(DocumentoClinico)
        .filter(DocumentoClinico.id_documento == id_documento)
        .options(
            joinedload(DocumentoClinico.receita),
            joinedload(DocumentoClinico.atestado),
            joinedload(DocumentoClinico.consulta).options(*_carregar_contexto()),
        )
        .first()
    )


def listar_documentos_da_consulta(db: Session, id_consulta: int) -> list[DocumentoClinico]:
    return (
        db.query(DocumentoClinico)
        .filter(DocumentoClinico.id_consulta == id_consulta)
        .order_by(DocumentoClinico.id_documento)
        .all()
    )
