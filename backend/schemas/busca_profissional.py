# Schemas da busca de profissionais por especialidade, data, horário e valor.
from datetime import date, time
from enum import Enum

from pydantic import BaseModel


class OrdenacaoBusca(str, Enum):
    """Critério de ordenação da lista devolvida pela busca."""

    NOME = "nome"
    VALOR = "valor"
    AVALIACAO = "avaliacao"


class FiltroBuscaProfissional(BaseModel):
    """Filtros da busca. Todos são opcionais e se combinam entre si.

    O router monta este objeto a partir dos parâmetros da query string; a
    validação cruzada (intervalos invertidos) fica no service.
    """

    id_especialidade: int | None = None
    especialidade: str | None = None
    data_inicio: date | None = None
    data_fim: date | None = None
    hora_inicio: time | None = None
    hora_fim: time | None = None
    valor_min: float | None = None
    valor_max: float | None = None
    ordenar_por: OrdenacaoBusca = OrdenacaoBusca.NOME


class HorarioDisponivelOutput(BaseModel):
    """Janela livre da agenda do profissional, pronta para o agendamento."""

    id_horario: int
    data_consulta: date
    hora_inicio: time
    hora_fim: time


class ProfissionalBuscaOutput(BaseModel):
    """Um profissional numa especialidade, com o preço e a agenda que sobrou.

    A busca devolve o vínculo (id_esp_prof), não o profissional puro: o valor da
    consulta, a avaliação e a agenda mudam de uma especialidade para a outra.
    """

    id_esp_prof: int
    id_profissional: int
    nome: str
    especialidade: str
    valor_consulta: float
    avaliacao: float | None = None
    conselho: str | None = None
    info_profissional: str | None = None
    path_imagem: str | None = None
    horarios_disponiveis: list[HorarioDisponivelOutput]
