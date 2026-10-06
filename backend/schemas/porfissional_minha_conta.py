# CRIADO: JOAO MARCOS 

from pydantic import BaseModel
import uuid

class EspecialidadeInput(BaseModel):
    id_especialidade: int
    numero_conselho: str 
    conselho: str 
    valor: float 

class AdicionaInfoProfissionalInput(BaseModel):
    id_usuario: uuid.UUID
    info_profissional: str | None = None
    especialidade: list[EspecialidadeInput] | None = None


class EspecialidadeOutput(BaseModel):
    id_especialidade: int
    nome: str 
    numero_conselho: str 
    conselho: str 
    valor: float 

class BuscarInfoProfissionalOutput(BaseModel):
    id_profissional: int
    info_profissional: str 
    especialidade: list[EspecialidadeOutput] 


class AlterarValorConsultaOutput(BaseModel): 
    valor_consulta: float


class AlterarValorConsultaInput(BaseModel):
    id_usuario: uuid.UUID
    id_especialidade: int 
    valor_consulta: float

class BuscarEspecialidadeOutput(BaseModel):
    id_especialidade: int
    especialidade: str

class ExcluirEpecialidadeInput(BaseModel):
    id_usuario: uuid.UUID
    id_especialidade: int

