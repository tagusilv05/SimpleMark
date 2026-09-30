# schemas/consulta.py
from datetime import date, time
from pydantic import BaseModel

class PacienteConsultaOut(BaseModel):
    id_paciente: int
    nome: str
    telefone: str
    email: str
    data_nascimento: date
    genero: str

class ConsultaProfissionalOut(BaseModel):
    id_consulta: int
    data: date
    hora: time
    tipo: str
    status: str
    especialidade: str
    paciente: PacienteConsultaOut