"""Entradas e saídas da Ouvidoria."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class ManifestacaoCriadaResposta(BaseModel):
    """Resposta de POST /ouvidoria/manifestacoes: o protocolo da manifestação aberta."""

    mensagem: str
    id: uuid.UUID
    protocolo: str
    status: str
    criada_em: datetime
    quantidade_anexos: int
