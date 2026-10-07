# schemas/avaliacao.py
from datetime import date, time
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class AvaliacaoCreate(BaseModel):
    id_consulta: int
    avaliacao: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = Field(None, max_length=1000)


class AvaliacaoResponse(BaseModel):
    id_consulta: int
    id_profissional: int
    avaliacao: int
    feedback: Optional[str]
    data: date
    hora: time

    model_config = ConfigDict(from_attributes=True)


class MediaProfissionalResponse(BaseModel):
    id_profissional: int
    media: Optional[float]
    total: int