from datetime import date, time

from pydantic import BaseModel, ConfigDict, StrictInt, field_validator, model_validator


class AvaliacaoEntrada(BaseModel):
    """Avaliação da consulta. A nota é opcional: sem nota, vale só o comentário."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    nota: StrictInt | None = None
    feedback: str | None = None

    @field_validator("nota")
    @classmethod
    def nota_valida(cls, valor: int | None) -> int | None:
        if valor is not None and not 1 <= valor <= 5:
            raise ValueError("A nota deve ser de 1 a 5 estrelas.")
        return valor

    @field_validator("feedback")
    @classmethod
    def feedback_valido(cls, valor: str | None) -> str | None:
        if valor is None or valor == "":
            return None
        if len(valor) > 1000:
            raise ValueError("O comentário deve ter no máximo 1000 caracteres.")
        return valor

    @model_validator(mode="after")
    def ao_menos_um_campo(self) -> "AvaliacaoEntrada":
        if self.nota is None and self.feedback is None:
            raise ValueError("Informe a nota em estrelas ou um comentário para avaliar.")
        return self


class AvaliacaoResposta(BaseModel):
    id_consulta: int
    nota: int | None
    feedback: str | None
    data: date
    hora: time


class ResumoAvaliacoesResposta(BaseModel):
    id_profissional: int
    media: float | None
    total_avaliacoes: int
    distribuicao: dict[int, int]


class ProfissionalMelhorAvaliadoResposta(BaseModel):
    posicao: int
    id_profissional: int
    nome: str
    especialidades: list[str]
    media: float
    total_avaliacoes: int
    pontuacao: float
