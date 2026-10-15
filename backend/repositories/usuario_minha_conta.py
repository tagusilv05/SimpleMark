# CRIADO: JOAO MARCOS 

"""Consultas e exclusões usadas na conta do usuário."""

from sqlalchemy.orm import Session
from models.models import (
    Usuario, 
    Endereco,
    Consulta,
    DocumentoClinico,
    Avaliacao,
    Pagamento,
)

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
    """Apaga em lote documentos, avaliação e pagamento da consulta, sem commit."""
    db.query(DocumentoClinico).filter(
        DocumentoClinico.id_consulta == id_consulta
    ).delete(synchronize_session=False)

    db.query(Avaliacao).filter(
        Avaliacao.id_consulta == id_consulta
    ).delete(synchronize_session=False)

    db.query(Pagamento).filter(
        Pagamento.id_consulta == id_consulta
    ).delete(synchronize_session=False)

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
