# Consulta da tabela documento_clinico usada na validação pública do QR-Code.
# Não aplica regra de negócio.
from sqlalchemy.orm import Session, joinedload

from models.models import Consulta, DocumentoClinico, Profissional, ProfissionalEspecialidade


def buscar_documento_por_codigo(db: Session, codigo_verificacao: str) -> DocumentoClinico | None:
    """Documento pelo código do QR-Code, já com profissional, conselho e especialidade.

    Os joins vêm carregados de uma vez porque a resposta precisa de todos eles e
    esta rota é pública: quanto menos ida e volta ao banco, melhor.
    """
    caminho_esp_prof = (
        joinedload(DocumentoClinico.consulta)
        .joinedload(Consulta.profissional_especialidade)
    )
    return (
        db.query(DocumentoClinico)
        .filter(DocumentoClinico.codigo_verificacao == codigo_verificacao)
        .options(
            caminho_esp_prof.joinedload(ProfissionalEspecialidade.profissional).joinedload(
                Profissional.usuario
            ),
            caminho_esp_prof.joinedload(ProfissionalEspecialidade.especialidade),
            caminho_esp_prof.joinedload(ProfissionalEspecialidade.conselho),
        )
        .first()
    )
