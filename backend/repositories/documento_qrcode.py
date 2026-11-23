# Consultas da tabela documento_clinico usadas na geração do QR-Code.
# Não aplica regra de negócio.
"""Consultas de documento_clinico usadas na geração do QR-Code."""

from sqlalchemy.orm import Session

from models.models import Consulta, DocumentoClinico, ProfissionalEspecialidade


def buscar_documento_para_atualizacao(db: Session, id_documento: int) -> DocumentoClinico | None:
    """Busca o documento travando a linha até o fim da transação.

    A trava evita que duas requisições simultâneas gerem dois QR-Codes para o
    mesmo documento. O SELECT é simples de propósito: no PostgreSQL o FOR UPDATE
    não pode ser aplicado junto de um LEFT JOIN.

    Args:
        db (Session): Sessão do banco de dados.
        id_documento (int): Id do documento.

    Returns:
        DocumentoClinico | None: Documento travado, ou None se não existir.
    """
    return (
        db.query(DocumentoClinico)
        .filter(DocumentoClinico.id_documento == id_documento)
        .with_for_update()
        .first()
    )


def buscar_profissional_da_consulta(db: Session, id_consulta: int) -> int | None:
    """Id do profissional responsável pela consulta, via profissional_especialidade.

    Args:
        db (Session): Sessão do banco de dados.
        id_consulta (int): Id da consulta.

    Returns:
        int | None: Id do profissional, ou None se a consulta não existir.
    """
    return (
        db.query(ProfissionalEspecialidade.id_profissional)
        .join(
            Consulta,
            Consulta.id_esp_prof == ProfissionalEspecialidade.id_esp_prof,
        )
        .filter(Consulta.id_consulta == id_consulta)
        .scalar()
    )


def existe_codigo_verificacao(db: Session, codigo: str) -> bool:
    """Indica se o código de verificação já pertence a algum documento.

    Args:
        db (Session): Sessão do banco de dados.
        codigo (str): Código de verificação.

    Returns:
        bool: True se o código já está em uso.
    """
    return (
        db.query(DocumentoClinico.id_documento)
        .filter(DocumentoClinico.codigo_verificacao == codigo)
        .first()
        is not None
    )
