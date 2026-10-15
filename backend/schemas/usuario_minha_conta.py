# CRIADO: JOAO MARCOS 

"""Entradas e saídas da área "minha conta" do usuário (/usuario)."""

from pydantic import BaseModel
from datetime import date
from typing import Literal
import uuid

class AltereInfoPessoalInput(BaseModel):
    """Corpo de PUT /usuario/altera-info-pessoal. Campos nulos ficam como estão."""

    id: uuid.UUID
    nome: str | None = None
    email: str | None = None
    telefone: str | None = None

class AltereInfoPessoalOutput(BaseModel):
    """Resposta de PUT /usuario/altera-info-pessoal."""

    nome: str
    email: str
    telefone: str

class AltereEnderecoInput(BaseModel):
    """Corpo de PUT /usuario/altera-endereco. Campos nulos ficam como estão."""

    id_usuario: uuid.UUID
    cep: str | None = None
    cidade: str | None = None
    logradouro: str | None = None
    numero: int | None = None
    bairro: str | None = None
    complemento: str | None = None

class AltereEnderecoOutput(BaseModel):
    """Resposta de PUT /usuario/altera-endereco."""

    cep: str
    cidade: str
    logradouro: str
    numero: str
    bairro: str
    complemento: str 

class BuscarInfoEnderecoOutput(BaseModel):
    """Resposta de GET /usuario/buscar-info-endereco/{id_usuario}."""

    cep: str  
    cidade: str  
    logradouro: str 
    numero: int  
    bairro: str  
    complemento: str 

class BuscarInfoUsuarioOutput(BaseModel):
    """Resposta de GET /usuario/buscar-info-usuario/{id_usuario}."""

    nome: str
    cpf: str
    orgao_emissor: str
    data_nascimento: date
    genero: str
    telefone: str
    email: str

class ExcluirUsuarioInput(BaseModel):
    """Corpo de DELETE /usuario/excluir-usuario: o tipo define o que é excluído."""

    id: uuid.UUID
    tipo: Literal["paciente", "profissional"]


