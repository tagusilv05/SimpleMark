# CRIADO: JOAO MARCOS 

"""Consultas e exclusões usadas na conta do usuário."""

from sqlalchemy.orm import Session
from datetime import datetime

from sqlalchemy import update

from models.administracao import LogAcaoAdministrador
from models.models import (
    Usuario,
    Endereco,
    Consulta,
    DocumentoClinico,
    Avaliacao,
    Pagamento,
    Receita,
    ReceitaMedicamento,
    Atestado,
)

# Consultas que ainda vão acontecer e impedem a exclusão da conta
STATUS_CONSULTA_ENCERRADA = ("cancelada", "cancelado", "realizada", "realizado")

# Consulta um usuário pelo seu ID.
def buscar_usuario_por_id(id_usuario, db: Session):
    """Usuário pelo id, ou None se não existir."""
    return (
        db.query(Usuario)
        .filter(Usuario.id == id_usuario)
        .first()
    )

# Consulta o endereço associado a um usuário pelo ID do usuário.
def buscar_endereco_por_usuario(id_usuario, db: Session):
    """Endereço do usuário, ou None se não houver."""
    return (
        db.query(Endereco)
        .filter(Endereco.id_usuario == id_usuario)
        .first()
    )

# Busca todas as consultas vinculadas a um paciente
def buscar_consultas_por_paciente(id_paciente, db: Session):
    """Todas as consultas do paciente."""
    return (
        db.query(Consulta)
        .filter(Consulta.id_paciente == id_paciente)
        .all()
    )

# Exclui os dados relacionados a uma consulta
def excluir_dados_consulta(id_consulta , db: Session):
    """Apaga documentos (com receita, medicamentos e atestado), avaliação e pagamento, sem commit."""
    ids_documentos = [
        linha.id_documento
        for linha in db.query(DocumentoClinico.id_documento).filter(DocumentoClinico.id_consulta == id_consulta)
    ]
    if ids_documentos:
        db.query(ReceitaMedicamento).filter(
            ReceitaMedicamento.id_documento.in_(ids_documentos)
        ).delete(synchronize_session=False)
        db.query(Receita).filter(Receita.id_documento.in_(ids_documentos)).delete(synchronize_session=False)
        db.query(Atestado).filter(Atestado.id_documento.in_(ids_documentos)).delete(synchronize_session=False)
        db.query(DocumentoClinico).filter(
            DocumentoClinico.id_documento.in_(ids_documentos)
        ).delete(synchronize_session=False)

    db.query(Avaliacao).filter(
        Avaliacao.id_consulta == id_consulta
    ).delete(synchronize_session=False)

    db.query(Pagamento).filter(
        Pagamento.id_consulta == id_consulta
    ).delete(synchronize_session=False)


def consulta_ainda_vai_acontecer(consulta: Consulta, agora: datetime) -> bool:
    """True se a consulta não foi cancelada nem realizada e o horário ainda não passou."""
    if consulta.status in STATUS_CONSULTA_ENCERRADA:
        return False
    return datetime.combine(consulta.data, consulta.hora) >= agora


def desvincular_logs_do_usuario(id_usuario, db: Session):
    """Tira o usuário dos logs do administrador (a coluna não tem ON DELETE), sem commit."""
    db.execute(
        update(LogAcaoAdministrador)
        .where(LogAcaoAdministrador.id_usuario_alvo == id_usuario)
        .values(id_usuario_alvo=None)
        .execution_options(synchronize_session=False)
    )

# Exclui todas as consultas vinculadas a um paciente
def excluir_consultas_por_paciente(id_paciente , db: Session):
    """Apaga em lote todas as consultas do paciente, sem commit."""
    db.query(Consulta).filter(
        Consulta.id_paciente == id_paciente
    ).delete(synchronize_session=False)

# Exclui o endereço vinculado a um usuário
def excluir_endereco_por_usuario(id_usuario, db: Session):
    """Apaga em lote o endereço do usuário, sem commit."""
    db.query(Endereco).filter(
        Endereco.id_usuario == id_usuario
    ).delete(synchronize_session=False)
