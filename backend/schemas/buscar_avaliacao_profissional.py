# CRIADO: JOAO MARCOS 

"""Entrada e saída da busca das avaliações de um profissional."""

from datetime import date
from pydantic import BaseModel
import uuid


class AvaliacaoConsultaInput(BaseModel):
    """Corpo de POST /avaliacao/buscar-avaliacoes: usuário ou profissional e
    a especialidade (opcional).
    """

    id_usuario: str | uuid.UUID
    id_especialidade: int | None = None


class AvaliarOutput(BaseModel):
    """Avaliação de uma consulta, com o nome do paciente."""

    nome_paciente: str
    data_consulta: date
    feedback: str | None = None
    avaliacao: int | None = None  # None quando o paciente só deixou comentário


class AvaliacaoConsultaOutput(BaseModel):
    """Resposta de POST /avaliacao/buscar-avaliacoes.

    sub_total conta as avaliações por nota, com as chaves "1" a "5".
    """

    avaliacao: list[AvaliarOutput] = []
    total: int = 0
    sub_total: dict[str, int] = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
