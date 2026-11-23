"""Consultas da tabela data_horario usadas na agenda do profissional."""

from models.models import DataHorario
from typing import Optional
from datetime import date, time

def listar(db, id_esp_prof: int, data_consulta: Optional[date] = None):
    
    """Horários do vínculo, opcionalmente só de uma data.

    Se id_esp_prof for None, não filtra por vínculo e devolve todos os horários.

    Args:
        db (Session): Sessão do banco de dados.
        id_esp_prof (int): Id do vínculo profissional-especialidade, ou None.
        data_consulta (Optional[date]): Data dos horários; None não filtra.

    Returns:
        list[DataHorario]: Horários encontrados.
    """
    
    
    query = db.query(DataHorario)
    if id_esp_prof is not None:
        query = query.filter(DataHorario.id_esp_prof == id_esp_prof)
    if data_consulta is not None:
        query = query.filter(DataHorario.data_consulta == data_consulta)
    return query.all()

def buscar_por_id(db, id_horario: int):
    """Horário pelo id, ou None se não existir.

    Args:
        db (Session): Sessão do banco de dados.
        id_horario (int): Id do horário.

    Returns:
        DataHorario | None: Horário encontrado, ou None.
    """
    return db.query(DataHorario).filter(
        DataHorario.id_horario == id_horario
    ).first()

def existe_horario(db, id_esp_prof: int, data_consulta: date, hora_inicio: time):
    """Indica se o vínculo já tem horário nessa data e hora de início.

    Args:
        db (Session): Sessão do banco de dados.
        id_esp_prof (int): Id do vínculo profissional-especialidade.
        data_consulta (date): Data do horário.
        hora_inicio (time): Hora de início do horário.

    Returns:
        bool: True se já existe horário nessa data e hora.
    """
    return db.query(DataHorario).filter(
        DataHorario.id_esp_prof == id_esp_prof,
        DataHorario.data_consulta == data_consulta,
        DataHorario.hora_inicio == hora_inicio
    ).first() is not None

def criar(db, horario: DataHorario):
    """Inclui o horário na sessão, sem flush nem commit.

    Args:
        db (Session): Sessão do banco de dados.
        horario (DataHorario): Horário a incluir.

    Returns:
        DataHorario: O mesmo horário recebido.
    """
    db.add(horario)
    return horario

def atualizar_por_id(db, id_horario: int, novo_inicio: time, novo_fim: time):
    """Altera início e fim do horário na sessão, sem commit.

    Devolve None se o horário não existir.

    Args:
        db (Session): Sessão do banco de dados.
        id_horario (int): Id do horário.
        novo_inicio (time): Nova hora de início.
        novo_fim (time): Nova hora de fim.

    Returns:
        DataHorario | None: Horário alterado, ou None se não existir.
    """
    """Atualiza o horário pelo id, ou None se não existir."""
    horario = buscar_por_id(db, id_horario)
    if horario:
        horario.hora_inicio = novo_inicio
        horario.hora_fim = novo_fim
    return horario

def deletar(db, horario: DataHorario):
    """Marca o horário para exclusão na sessão, sem commit.

    Args:
        db (Session): Sessão do banco de dados.
        horario (DataHorario): Horário a excluir.
    """
    db.delete(horario)