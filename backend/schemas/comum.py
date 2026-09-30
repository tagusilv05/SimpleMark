from pydantic import BaseModel


class MensagemResposta(BaseModel):
    mensagem: str
