from datetime import datetime

from sqlalchemy.orm import Session, joinedload

from models.models import Consulta, Paciente, Pagamento, Usuario


def buscar_consulta_por_id(id_consulta: int, db: Session):
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
    return (
        db.query(Pagamento)
        .filter(Pagamento.id_consulta == id_consulta)
        .first()
    )


def criar_pagamento(id_consulta: int, status: str, db: Session):
    agora = datetime.now()
    pagamento = Pagamento(
        id_consulta=id_consulta,
        status=status,
        data=agora.date(),
        hora=agora.time().replace(microsecond=0),
    )
    db.add(pagamento)
    db.commit()
    db.refresh(pagamento)
    return pagamento


def atualizar_status_pagamento(pagamento: Pagamento, status: str, db: Session):
    agora = datetime.now()
    pagamento.status = status
    pagamento.data = agora.date()
    pagamento.hora = agora.time().replace(microsecond=0)
    db.commit()
    db.refresh(pagamento)
    return pagamento