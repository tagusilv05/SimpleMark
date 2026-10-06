# CRIADO: JOAO MARCOS 

from pydantic import BaseModel
from datetime import date
from typing import Literal
import uuid

class AltereInfoPessoalInput(BaseModel):
    id: uuid.UUID
    nome: str | None = None
    email: str | None = None
    telefone: str | None = None

class AltereInfoPessoalOutput(BaseModel):
    nome: str
    email: str
    telefone: str

class AltereEnderecoInput(BaseModel):
    id_usuario: uuid.UUID
    cep: str | None = None
    cidade: str | None = None
    logradouro: str | None = None
    numero: int | None = None
    bairro: str | None = None
    complemento: str | None = None

class AltereEnderecoOutput(BaseModel):
    cep: str
    cidade: str
    logradouro: str
    numero: str
    bairro: str
    complemento: str 

class BuscarInfoEnderecoOutput(BaseModel):
    cep: str  
    cidade: str  
    logradouro: str 
    numero: int  
    bairro: str  
    complemento: str 

class BuscarInfoUsuarioOutput(BaseModel):
    nome: str
    cpf: str
    orgao_emissor: str
    data_nascimento: date
    genero: str
    telefone: str
    email: str

class ExcluirUsuarioInput(BaseModel):
    id: uuid.UUID
    tipo: Literal["paciente", "profissional"]


