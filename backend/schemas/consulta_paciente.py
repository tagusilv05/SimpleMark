# schemas/consulta_paciente.py
from datetime import date, time
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel


class ProfissionalResumo(BaseModel):
    id_profissional: int
    nome: str
    path_imagem: Optional[str] = None
    especialidade: str


class AvaliacaoResumo(BaseModel):
    avaliacao: int
    feedback: Optional[str] = None


class ConsultaPacienteResponse(BaseModel):
    id_consulta: int
    data: date
    hora: time
    tipo: str
    status: str
    valor: Decimal
    profissional: ProfissionalResumo
    pagamento_status: Optional[str] = None
    avaliacao: Optional[AvaliacaoResumo] = None
    pode_avaliar: bool 


class ListaConsultasResponse(BaseModel):
    total: int
    itens: List[ConsultaPacienteResponse]