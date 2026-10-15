"""Schemas compartilhados entre as rotas."""

from pydantic import BaseModel


class MensagemResposta(BaseModel):
    """Mensagem simples, usada em respostas de sucesso e de erro."""

    mensagem: str
