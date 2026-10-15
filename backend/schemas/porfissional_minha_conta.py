# CRIADO: JOAO MARCOS 

"""Entradas e saídas da área "minha conta" do profissional."""

from pydantic import BaseModel
import uuid

class EspecialidadeInput(BaseModel):
    """Especialidade a vincular, com conselho e valor da consulta."""

    id_especialidade: int
    numero_conselho: str 
    conselho: str 
    valor: float 

class AdicionaInfoProfissionalInput(BaseModel):
    """JSON do campo "dados" (form) de PUT /profissionais/alterar-info-profissional.

    Campos nulos ficam como estão; cada especialidade enviada cria um vínculo.
    """

    id_usuario: uuid.UUID
    info_profissional: str | None = None
    especialidade: list[EspecialidadeInput] | None = None


class EspecialidadeOutput(BaseModel):
    """Especialidade do profissional, com conselho e valor."""

    id_especialidade: int
    nome: str 
    numero_conselho: str 
    conselho: str 
    valor: float 

class BuscarInfoProfissionalOutput(BaseModel):
    """Resposta de GET /profissionais/buscar-info-profissional/{id_usuario}."""

    id_profissional: int
    info_profissional: str 
    especialidade: list[EspecialidadeOutput] 


class AlterarValorConsultaOutput(BaseModel): 
    """Resposta de PUT /profissionais/alterar-valor-consulta."""

    valor_consulta: float


class AlterarValorConsultaInput(BaseModel):
    """Corpo de PUT /profissionais/alterar-valor-consulta."""

    id_usuario: uuid.UUID
    id_especialidade: int 
    valor_consulta: float

class BuscarEspecialidadeOutput(BaseModel):
    """Item de GET /profissionais/lista-especialidade."""

    id_especialidade: int
    especialidade: str

class ExcluirEpecialidadeInput(BaseModel):
    """Corpo de DELETE /profissionais/excluir-especialidade."""

    id_usuario: uuid.UUID
    id_especialidade: int

