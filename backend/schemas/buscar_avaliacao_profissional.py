# CRIADO: JOAO MARCOS 

"""Entrada e saída da busca das avaliações de um profissional."""

from datetime import date
from pydantic import BaseModel
import uuid


class AvaliacaoConsultaInput(BaseModel):
    """Corpo de POST /avaliacao/buscar-avaliacoes: usuário do profissional e
    a especialidade.
    """

    id_usuario: uuid.UUID
    id_especialidade: int


class AvaliarOutput(BaseModel):
    """Avaliação de uma consulta, com o nome do paciente."""

    nome_paciente: str
    data_consulta: date
    feedback: str | None
    avaliacao: int


class AvaliacaoConsultaOutput(BaseModel):
    """Resposta de POST /avaliacao/buscar-avaliacoes.

    sub_total conta as avaliações por nota, com as chaves "1" a "5".
    """

    avaliacao: list[AvaliarOutput]
    total: int
    sub_total: dict[str, int]