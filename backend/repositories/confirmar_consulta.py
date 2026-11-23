# CRIADO: JOAO MARCOS 

"""Gravação da consulta confirmada pelo paciente."""

from sqlalchemy.orm import Session

from models.models import Consulta

# Adiciona uma nova consulta ao banco de dados e retorna a consulta cadastrada.
def adicionar_consulta(dados, id_paciente, id_esp_prof, db: Session):
    """Cria a consulta com os dados recebidos, faz commit e a devolve recarregada.

    Args:
        dados: Dados da consulta, com ``data``, ``hora``, ``tipo``, ``status`` e
            ``valor``.
        id_paciente (int): Id do paciente.
        id_esp_prof (int): Id do vínculo profissional-especialidade.
        db (Session): Sessão do banco de dados.

    Returns:
        Consulta: Consulta criada, recarregada do banco.
    """

    consulta = Consulta(
        id_paciente=id_paciente,
        id_esp_prof=id_esp_prof,
        data=dados.data,
        hora=dados.hora,
        tipo=dados.tipo,
        status=dados.status,
        valor=dados.valor
    )

    db.add(consulta)
    db.commit()
    db.refresh(consulta)

    return consulta