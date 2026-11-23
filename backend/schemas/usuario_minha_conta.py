# CRIADO: JOAO MARCOS

"""Entradas e saídas da área "minha conta" do usuário (/usuario).

Os ids enviados no corpo precisam ser os da conta logada (as rotas exigem login).
"""

from datetime import date
from typing import Literal
import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.validadores import normalizar_cep, normalizar_email, normalizar_telefone


class AltereInfoPessoalInput(BaseModel):
    """Corpo de PUT /usuario/altera-info-pessoal. Campos nulos ficam como estão."""

    model_config = ConfigDict(str_strip_whitespace=True)

    id: uuid.UUID
    nome: str | None = Field(default=None, min_length=3, max_length=150)
    email: str | None = None
    telefone: str | None = None

    @field_validator("email")
    @classmethod
    def email_valido(cls, valor: str | None) -> str | None:
        """Normaliza e valida o e-mail.

        Args:
            valor (str | None): E-mail informado, ou ``None``.

        Returns:
            str | None: E-mail normalizado, ou ``None`` se não informado.
        """
        return None if valor is None else normalizar_email(valor)

    @field_validator("telefone")
    @classmethod
    def telefone_valido(cls, valor: str | None) -> str | None:
        """Normaliza e valida o telefone.

        Args:
            valor (str | None): Telefone informado, ou ``None``.

        Returns:
            str | None: Somente os dígitos do telefone, ou ``None`` se não informado.
        """
        return None if valor is None else normalizar_telefone(valor)


class AltereInfoPessoalOutput(BaseModel):
    """Resposta de PUT /usuario/altera-info-pessoal."""

    nome: str
    email: str
    telefone: str


class AltereEnderecoInput(BaseModel):
    """Corpo de PUT /usuario/altera-endereco. Campos nulos ficam como estão.

    O número é texto (aceita "S/N", "120-A").
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    id_usuario: uuid.UUID
    cep: str | None = None
    cidade: str | None = Field(default=None, min_length=2, max_length=100)
    logradouro: str | None = Field(default=None, min_length=2, max_length=150)
    numero: str | None = Field(default=None, min_length=1, max_length=20)
    bairro: str | None = Field(default=None, min_length=2, max_length=100)
    complemento: str | None = Field(default=None, max_length=150)

    @field_validator("numero", mode="before")
    @classmethod
    def numero_texto(cls, valor):
        """Aceita número enviado como inteiro.

        Args:
            valor: Número informado (texto, inteiro ou ``None``).

        Returns:
            str | None: Número convertido em texto, ou ``None`` se não informado.
        """
        return None if valor is None else str(valor)

    @field_validator("cep")
    @classmethod
    def cep_valido(cls, valor: str | None) -> str | None:
        """Normaliza e valida o CEP.

        Args:
            valor (str | None): CEP informado, ou ``None``.

        Returns:
            str | None: CEP no formato ``00000-000``, ou ``None`` se não informado.
        """
        return None if valor is None else normalizar_cep(valor)


class AltereEnderecoOutput(BaseModel):
    """Resposta de PUT /usuario/altera-endereco."""

    cep: str
    cidade: str
    logradouro: str
    numero: str
    bairro: str
    complemento: str | None = None


class BuscarInfoEnderecoOutput(BaseModel):
    """Resposta de GET /usuario/buscar-info-endereco/{id_usuario}."""

    cep: str
    cidade: str
    logradouro: str
    numero: str
    bairro: str
    complemento: str | None = None


class BuscarInfoUsuarioOutput(BaseModel):
    """Resposta de GET /usuario/buscar-info-usuario/{id_usuario}."""

    nome: str
    cpf: str
    orgao_emissor: str
    data_nascimento: date
    genero: str
    telefone: str
    email: str
    status: bool = True


class ExcluirUsuarioInput(BaseModel):
    """Corpo de DELETE /usuario/excluir-usuario: o tipo define o que é excluído."""

    id: uuid.UUID
    tipo: Literal["paciente", "profissional"]


class AlterarSenhaInput(BaseModel):
    """Corpo de PUT /usuario/alterar-senha: senha atual e a nova."""

    senha_atual: str = Field(min_length=1, max_length=128)
    nova_senha: str = Field(max_length=128)

    @field_validator("nova_senha")
    @classmethod
    def senha_minima(cls, valor: str) -> str:
        """Mesma regra do cadastro: no mínimo 8 caracteres.

        Args:
            valor (str): Nova senha informada.

        Returns:
            str: A nova senha, sem alteração.

        Raises:
            ValueError: Quando a nova senha tem menos de 8 caracteres.
        """
        if len(valor) < 8:
            raise ValueError("A nova senha deve ter no mínimo 8 caracteres.")
        return valor
