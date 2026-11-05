"""Consultas e gravações da tabela pagamento."""

from datetime import datetime

from sqlalchemy.orm import Session, joinedload

from models.models import Consulta, Paciente, Pagamento, Usuario


def buscar_consulta_por_id(id_consulta: int, db: Session):
    """Consulta pelo id, com paciente, usuário, endereço e pagamento; ou None."""
    return (
        db.query(Consulta)
        .options(
            joinedload(Consulta.paciente).joinedload(Paciente.usuario).joinedload(Usuario.endereco),
            joinedload(Consulta.pagamento),
        )
        .filter(Consulta.id_consulta == id_consulta)
        .first()
    )


def buscar_pagamento_por_consulta(id_consulta: int, db: Session):
    """Pagamento da consulta, ou None se ainda não houver."""
    return (
        db.query(Pagamento)
        .filter(Pagamento.id_consulta == id_consulta)
        .first()
    )


def criar_pagamento(
    id_consulta: int,
    status: str,
    db: Session,
    metodo: str | None = None,
    id_transacao: str | None = None,
):
    """Cria o pagamento com data e hora atuais e faz commit."""
    agora = datetime.now()
    pagamento = Pagamento(
        id_consulta=id_consulta,
        status=status,
        metodo=metodo,
        id_transacao=id_transacao,
        data=agora.date(),
        hora=agora.time().replace(microsecond=0),
    )
    db.add(pagamento)
    db.commit()
    db.refresh(pagamento)
    return pagamento


def atualizar_pagamento(
    pagamento: Pagamento,
    db: Session,
    status: str | None = None,
    metodo: str | None = None,
    id_transacao: str | None = None,
):
    """Atualiza status, método e/ou transação (só o que vier preenchido).

    Data e hora passam a ser as do momento da mudança. Faz commit.
    """
    if status is not None:
        pagamento.status = status
    if metodo is not None:
        pagamento.metodo = metodo
    if id_transacao is not None:
        pagamento.id_transacao = id_transacao
    agora = datetime.now()
    pagamento.data = agora.date()
    pagamento.hora = agora.time().replace(microsecond=0)
    db.commit()
    db.refresh(pagamento)
    return pagamento


def atualizar_status_pagamento(pagamento: Pagamento, status: str, db: Session):
    """Troca o status, atualiza data e hora para agora e faz commit."""
    return atualizar_pagamento(pagamento, db, status=status)
