"""Perfil da conta a partir das tabelas paciente, profissional e administrador."""

from enum import Enum

from core.excecoes import ErroNegocio
from models.models import Usuario


class PerfilUsuario(str, Enum):
    """Perfis de acesso possíveis de uma conta."""

    PACIENTE = "paciente"
    PROFISSIONAL = "profissional"
    ADMINISTRADOR = "administrador"


def perfil_de(usuario: Usuario) -> PerfilUsuario:
    """Descobre o perfil da conta pelo registro vinculado.

    A ordem de prioridade é administrador, profissional e paciente. Sem nenhum
    deles, levanta ErroNegocio com 403.
    """
    if usuario.administrador is not None:
        return PerfilUsuario.ADMINISTRADOR
    if usuario.profissional is not None:
        return PerfilUsuario.PROFISSIONAL
    if usuario.paciente is not None:
        return PerfilUsuario.PACIENTE
    raise ErroNegocio("Esta conta não possui um perfil de acesso.", 403)