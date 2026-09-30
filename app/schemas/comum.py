# Arquivo criado por Victor
from pydantic import BaseModel, ConfigDict, Field


# Classe para representar o esquema base dos JSON da API.
class Esquema(BaseModel):
    """Base dos JSON da API. Campo desconhecido é recusado, em vez de ignorado.

    Passo a passo:
    1. extra=forbid faz o Pydantic rejeitar chave que o schema não declara.
    2. O handler de erro traduz isso para a frase de campo que não faz parte da requisição.
    """
    model_config = ConfigDict(extra="forbid")

# Classe para representar a resposta de mensagem.
class MensagemResposta(Esquema):
    # representação do campo mensagem.
    mensagem: str = Field(description="Explicação do resultado e, quando couber, o que fazer em seguida.")
