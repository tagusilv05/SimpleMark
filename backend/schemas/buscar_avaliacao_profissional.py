# CRIADO: JOAO MARCOS 

from datetime import date
from pydantic import BaseModel
import uuid


class AvaliacaoConsultaInput(BaseModel):
    id_usuario: uuid.UUID
    id_especialidade: int


class AvaliarOutput(BaseModel):
    nome_paciente: str
    data_consulta: date
    feedback: str | None
    avaliacao: int


class AvaliacaoConsultaOutput(BaseModel):
    avaliacao: list[AvaliarOutput]
    total: int
    sub_total: dict[str, int]