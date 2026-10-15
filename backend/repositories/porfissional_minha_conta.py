# CRIADO: JOAO MARCOS 

"""Consultas de especialidades, conselhos e horários da conta do profissional."""

from sqlalchemy.orm import Session
from models.models import (
    Especialidade, 
    InfoConselho, 
    ProfissionalEspecialidade, 
    DataHorario
)

# Busca uma especialidade pelo seu ID
def buscar_especialidade_por_id(id_especialidade: int, db: Session):
    """Especialidade pelo id, ou None se não existir."""
    return (
        db.query(Especialidade)
        .filter(
            Especialidade.id_especialidade == id_especialidade
        )
        .first()
    )


# Busca no banco todas as especialidades vinculadas a um profissional
def buscar_especialidades_profissional(id_profissional, db: Session):
    """Vínculos profissional-especialidade do profissional."""
    especialidades = (
        db.query(ProfissionalEspecialidade)
        .filter(
            ProfissionalEspecialidade.id_profissional == id_profissional
        )
        .all()
    )
    return especialidades


# Cria um novo conselho profissional no banco de dados
def criar_conselho(numero_conselho: str, orgao_conselho: str, db: Session):
    """Cria o conselho e faz flush para o id já ficar disponível, sem commit."""
    conselho = InfoConselho(numero_conselho=numero_conselho, orgao_conselho=orgao_conselho)

    db.add(conselho)
    db.flush()

    return conselho


# Cria uma ligação entre profissional, especialidade e conselho
def criar_profissional_especialidade(id_profissional: int, id_especialidade: int, id_conselho: int, valor_consulta: float, db: Session):
    """Cria o vínculo entre profissional, especialidade e conselho, com flush e sem commit."""
    profissional_especialidade = ProfissionalEspecialidade(
        id_profissional=id_profissional,
        id_especialidade=id_especialidade,
        id_conselho=id_conselho,
        valor_consulta=valor_consulta
    )

    db.add(profissional_especialidade)
    db.flush()

    return profissional_especialidade


# Busca a especialidade vinculada a um profissional
def buscar_profissional_especialidade(id_profissional, id_especialidade, db: Session):
    """Vínculo entre o profissional e a especialidade, ou None se não existir."""
    return db.query(ProfissionalEspecialidade).filter(
        ProfissionalEspecialidade.id_profissional == id_profissional,
        ProfissionalEspecialidade.id_especialidade == id_especialidade
    ).first()


# Busca todas as especialidades vinculadas a um profissional
def buscar_especialidades_do_profissional(id_profissional, db: Session):
    """Vínculos profissional-especialidade do profissional."""
    return (
        db.query(ProfissionalEspecialidade)
        .filter(
            ProfissionalEspecialidade.id_profissional== id_profissional
        )
        .all()
    )


# Exclui todos os horários vinculados a uma especialidade do profissional
def excluir_horarios_por_especialidade(id_esp_prof, db: Session):
    """Apaga em lote os horários do vínculo, sem commit."""
    db.query(DataHorario).filter(
        DataHorario.id_esp_prof == id_esp_prof
    ).delete(synchronize_session=False)


# Exclui todas as especialidades vinculadas a um profissional
def excluir_especialidades_por_profissional(id_profissional,db: Session):
    """Apaga em lote os vínculos de especialidade do profissional, sem commit."""
    db.query(ProfissionalEspecialidade).filter(
        ProfissionalEspecialidade.id_profissional == id_profissional
    ).delete(synchronize_session=False)


# Exclui um conselho profissional pelo seu ID
def excluir_conselho(id_conselho, db: Session):
    """Apaga o conselho pelo id, sem commit."""
    db.query(InfoConselho).filter(
        InfoConselho.id_conselho == id_conselho
    ).delete(synchronize_session=False)


# Lista todas as especialidades cadastradas
def listar_especialidades(db: Session):
    """Todas as especialidades cadastradas, sem ordem definida."""
    return (
        db.query(Especialidade)
        .all()
    )


def buscar_profissional_especialidade(id_profissional, id_especialidade, db: Session):
    """Vínculo entre o profissional e a especialidade, ou None se não existir.

    Redefine a função de mesmo nome declarada acima neste módulo.
    """
    return (
        db.query(ProfissionalEspecialidade)
        .filter(
            ProfissionalEspecialidade.id_profissional == id_profissional,
            ProfissionalEspecialidade.id_especialidade == id_especialidade
        )
        .first()
    )