from models.models import DataHorario
from typing import Optional
from datetime import date, time

def listar(db, id_esp_prof: int, data_consulta: Optional[date] = None):
    
    """
    
    """
    
    
    query = db.query(DataHorario)
    if id_esp_prof is not None:
        query = query.filter(DataHorario.id_esp_prof == id_esp_prof)
    if data_consulta is not None:
        query = query.filter(DataHorario.data_consulta == data_consulta)
    return query.all()

def buscar_por_id(db, id_horario: int):
    return db.query(DataHorario).filter(
        DataHorario.id_horario == id_horario
    ).first()

def existe_horario(db, id_esp_prof: int, data_consulta: date, hora_inicio: time):
    return db.query(DataHorario).filter(
        DataHorario.id_esp_prof == id_esp_prof,
        DataHorario.data_consulta == data_consulta,
        DataHorario.hora_inicio == hora_inicio
    ).first() is not None

def criar(db, horario: DataHorario):
    db.add(horario)
    return horario

def atualizar_por_id(db, id_horario: int, novo_inicio: time, novo_fim: time):
    horario = buscar_por_id(db, id_horario)
    if horario:
        horario.hora_inicio = novo_inicio
        horario.hora_fim = novo_fim
    return horario

def deletar(db, horario: DataHorario):
    db.delete(horario)