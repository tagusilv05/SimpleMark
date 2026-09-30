"""Perfil da conta a partir das tabelas paciente, profissional e administrador."""

from enum import Enum

from core.excecoes import ErroNegocio
from models.models import Usuario


class PerfilUsuario(str, Enum):
    PACIENTE = "paciente"
    PROFISSIONAL = "profissional"
    ADMINISTRADOR = "administrador"


def perfil_de(usuario: Usuario) -> PerfilUsuario:
    if usuario.administrador is not None:
        return PerfilUsuario.ADMINISTRADOR
    if usuario.profissional is not None:
        return PerfilUsuario.PROFISSIONAL
    if usuario.paciente is not None:
        return PerfilUsuario.PACIENTE
    raise ErroNegocio("Esta conta não possui um perfil de acesso.", 403)