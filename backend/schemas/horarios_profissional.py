"""Entradas e saídas da agenda do profissional (/profissional/horarios)."""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, time

class ItemHorarioItem(BaseModel):
    """Janela de horário, repetida em cada data do lote."""

    hora_inicio: time
    hora_fim: time

class HorariosEmLoteCreate(BaseModel):
    """Corpo de POST /profissional/horarios.

    Cria cada horário de lista_horarios em cada uma das datas, para o vínculo
    profissional-especialidade.
    """

    id_esp_prof: int
    datas: List[date]
    lista_horarios: List[ItemHorarioItem]
    
class HorariosUpdate(BaseModel):
    """Corpo de PUT /profissional/horarios/{id_horario}."""

    hora_inicio: time
    hora_fim: time

class HorarioOut(BaseModel):
    """Horário da agenda, na resposta de GET /profissional/horarios."""

    id_horario: int
    id_esp_prof: int
    data_consulta: date
    hora_inicio: time
    hora_fim: time
    ocupado: bool

    model_config = {"from_attributes": True}  # <-- CORREÇÃO: sintaxe Pydantic v2