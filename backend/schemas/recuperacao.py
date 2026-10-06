from pydantic import BaseModel, field_validator, model_validator

from core.validadores import normalizar_email


class SolicitarCodigoEntrada(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def email_valido(cls, valor: str) -> str:
        return normalizar_email(valor)


class SolicitarCodigoResposta(BaseModel):
    mensagem: str
    reenvio_em_segundos: int


class VerificarCodigoEntrada(BaseModel):
    email: str
    codigo: str

    @field_validator("email")
    @classmethod
    def email_valido(cls, valor: str) -> str:
        return normalizar_email(valor)

    @field_validator("codigo")
    @classmethod
    def codigo_preenchido(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("Informe o código recebido por e-mail.")
        return valor


class VerificarCodigoResposta(BaseModel):
    token_redefinicao: str
    expira_em_segundos: int


class RedefinirSenhaEntrada(BaseModel):
    token_redefinicao: str
    nova_senha: str
    confirmar_senha: str

    @field_validator("nova_senha")
    @classmethod
    def senha_minima(cls, valor: str) -> str:
        if len(valor) < 8:
            raise ValueError("A senha deve ter no mínimo 8 caracteres.")
        return valor

    @model_validator(mode="after")
    def senhas_conferem(self) -> "RedefinirSenhaEntrada":
        if self.nova_senha != self.confirmar_senha:
            raise ValueError("As senhas não conferem. Digite a mesma senha nos dois campos.")
        return self
