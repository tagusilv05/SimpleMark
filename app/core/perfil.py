# Arquivo criado por Victor
from enum import Enum

from app.core.exceptions import ErroNegocio
from app.models.usuario import Usuario


class PerfilUsuario(str, Enum):
    """Perfis previstos no relatório: paciente, profissional de saúde e administrador."""

    PACIENTE = "paciente"
    PROFISSIONAL = "profissional"
    ADMINISTRADOR = "administrador"


def perfil_de(usuario: Usuario) -> PerfilUsuario:
    """Descobre o perfil pela tabela filha, como no modelo entidade-relacionamento.

    Passo a passo:
    1. Se existir linha em administrador, o perfil é administrador.
    2. Senão, se existir linha em profissional, o perfil é profissional.
    3. Senão, se existir linha em paciente, o perfil é paciente.
    4. Sem nenhuma dessas linhas, a conta está inconsistente e a função recusa o acesso.
    A ordem importa: administrador é conferido primeiro.
    """
    if usuario.administrador is not None:
        return PerfilUsuario.ADMINISTRADOR
    if usuario.profissional is not None:
        return PerfilUsuario.PROFISSIONAL
    if usuario.paciente is not None:
        return PerfilUsuario.PACIENTE
    raise ErroNegocio(
        "A conta não possui um perfil válido. Entre em contato com o suporte da Simple Mark.",
        403,
    )
