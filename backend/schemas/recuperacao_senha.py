"""Entradas e saídas da recuperação de senha em duas etapas."""

import uuid

from pydantic import BaseModel, field_validator

from core.seguranca import TAMANHO_CODIGO_LOGIN
from core.validadores import normalizar_email


class EsqueciSenhaEntrada(BaseModel):
    """Corpo de POST /auth/senha/esqueci: o e-mail da conta."""

    email: str

    @field_validator("email")
    @classmethod
    def email_valido(cls, valor: str) -> str:
        """Normaliza o e-mail (minúsculas, sem espaços) e recusa formato inválido."""
        return normalizar_email(valor)


class RedefinirSenhaEntrada(BaseModel):
    """Corpo de POST /auth/senha/redefinir: o desafio, o código do e-mail e a nova senha."""

    id_desafio: uuid.UUID
    codigo: str
    nova_senha: str

    @field_validator("codigo")
    @classmethod
    def codigo_somente_numeros(cls, valor: str) -> str:
        """Aceita só o código com a quantidade exata de dígitos (ASCII)."""
        texto = valor.strip()
        if len(texto) != TAMANHO_CODIGO_LOGIN or not (texto.isascii() and texto.isdigit()):
            raise ValueError(f"O código de confirmação deve ter {TAMANHO_CODIGO_LOGIN} números.")
        return texto

    @field_validator("nova_senha")
    @classmethod
    def senha_minima(cls, valor: str) -> str:
        """Recusa senha com menos de 8 caracteres (mesma regra do cadastro)."""
        if len(valor) < 8:
            raise ValueError("A senha deve ter no mínimo 8 caracteres.")
        return valor


class DesafioRecuperacaoResposta(BaseModel):
    """Resposta de POST /auth/senha/esqueci: o desafio a confirmar.

    É igual exista a conta ou não. O código foi enviado ao e-mail mascarado e
    vale por expira_em_segundos.
    """

    mensagem: str
    id_desafio: uuid.UUID
    email_mascarado: str
    expira_em_segundos: int