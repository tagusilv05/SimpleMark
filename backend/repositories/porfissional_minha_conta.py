# CRIADO: JOAO MARCOS 

from sqlalchemy.orm import Session
from models.models import (
    Especialidade, 
    InfoConselho, 
    ProfissionalEspecialidade, 
    DataHorario
)

# Busca uma especialidade pelo seu ID
def buscar_especialidade_por_id(id_especialidade: int, db: Session):
    return (
        db.query(Especialidade)
        .filter(
            Especialidade.id_especialidade == id_especialidade
        )
        .first()
    )


# Busca no banco todas as especialidades vinculadas a um profissional
def buscar_especialidades_profissional(id_profissional, db: Session):
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
    conselho = InfoConselho(numero_conselho=numero_conselho, orgao_conselho=orgao_conselho)

    db.add(conselho)
    db.flush()

    return conselho


# Cria uma ligação entre profissional, especialidade e conselho
def criar_profissional_especialidade(id_profissional: int, id_especialidade: int, id_conselho: int, valor_consulta: float, db: Session):
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
    return db.query(ProfissionalEspecialidade).filter(
        ProfissionalEspecialidade.id_profissional == id_profissional,
        ProfissionalEspecialidade.id_especialidade == id_especialidade
    ).first()


# Busca todas as especialidades vinculadas a um profissional
def buscar_especialidades_do_profissional(id_profissional, db: Session):
    return (
        db.query(ProfissionalEspecialidade)
        .filter(
            ProfissionalEspecialidade.id_profissional== id_profissional
        )
        .all()
    )


# Exclui todos os horários vinculados a uma especialidade do profissional
def excluir_horarios_por_especialidade(id_esp_prof, db: Session):
    db.query(DataHorario).filter(
        DataHorario.id_esp_prof == id_esp_prof
    ).delete(synchronize_session=False)


# Exclui todas as especialidades vinculadas a um profissional
def excluir_especialidades_por_profissional(id_profissional,db: Session):
    db.query(ProfissionalEspecialidade).filter(
        ProfissionalEspecialidade.id_profissional == id_profissional
    ).delete(synchronize_session=False)


# Exclui um conselho profissional pelo seu ID
def excluir_conselho(id_conselho, db: Session):
    db.query(InfoConselho).filter(
        InfoConselho.id_conselho == id_conselho
    ).delete(synchronize_session=False)


# Lista todas as especialidades cadastradas
def listar_especialidades(db: Session):
    return (
        db.query(Especialidade)
        .all()
    )