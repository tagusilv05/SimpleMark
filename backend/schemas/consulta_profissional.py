# schemas/consulta.py
"""Saídas da lista de consultas do profissional."""

from datetime import date, time
from pydantic import BaseModel

class PacienteConsultaOut(BaseModel):
    """Dados de contato do paciente da consulta."""

    id_paciente: int
    nome: str
    telefone: str
    email: str
    data_nascimento: date
    genero: str

class ConsultaProfissionalOut(BaseModel):
    """Item de GET /consultas_profissionais/{id_profissional}/consultas."""

    id_consulta: int
    data: date
    hora: time
    tipo: str
    status: str
    especialidade: str
    paciente: PacienteConsultaOut