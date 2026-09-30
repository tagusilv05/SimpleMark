# Arquivo criado por Victor
from app.models.administrador import Administrador
from app.models.endereco import Endereco
from app.models.especialidade import Especialidade
from app.models.info_conselho import InfoConselho
from app.models.paciente import Paciente
from app.models.profissional import Profissional
from app.models.profissional_especialidade import ProfissionalEspecialidade
from app.models.usuario import Usuario

__all__ = [
    "Administrador",
    "Endereco",
    "Especialidade",
    "InfoConselho",
    "Paciente",
    "Profissional",
    "ProfissionalEspecialidade",
    "Usuario",
]
