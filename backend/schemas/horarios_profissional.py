from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, time

class ItemHorarioItem(BaseModel):
    hora_inicio: time
    hora_fim: time

class HorariosEmLoteCreate(BaseModel):
    id_esp_prof: int
    datas: List[date]
    lista_horarios: List[ItemHorarioItem]
    
class HorariosUpdate(BaseModel):
    hora_inicio: time
    hora_fim: time

class HorarioOut(BaseModel):
    id_horario: int
    id_esp_prof: int
    data_consulta: date
    hora_inicio: time
    hora_fim: time
    ocupado: bool

    model_config = {"from_attributes": True}  # <-- CORREÇÃO: sintaxe Pydantic v2