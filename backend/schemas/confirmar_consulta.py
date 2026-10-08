# CRIADO: JOAO MARCOS 

from datetime import date, time
from typing import Literal
import uuid
from pydantic import BaseModel


class ConfirmarConsultaInput(BaseModel):

    id_usuario_paciente: uuid.UUID
    id_usuario_profissional: uuid.UUID
    id_especialidade: int
    data: date
    hora: time
    tipo: Literal["consulta", "retorno"]
    status: Literal["agendado", "realizado", "cancelado"]
    valor: float