import uuid

from pydantic import BaseModel, Field, field_validator

from core.perfil import perfil_de
from core.validadores import normalizar_cpf, normalizar_email
from models.models import Usuario


class LoginEntrada(BaseModel):
    identificador: str = Field(min_length=1)
    senha: str

    @field_validator("senha")
    @classmethod
    def senha_minima(cls, valor: str) -> str:
        if len(valor) < 8:
            raise ValueError("A senha deve ter no mínimo 8 caracteres.")
        return valor

    @field_validator("identificador")
    @classmethod
    def identificador_preenchido(cls, valor: str) -> str:
        texto = valor.strip()
        if not texto:
            raise ValueError("Informe o e-mail ou o CPF para entrar.")
        if "@" in texto:
            return normalizar_email(texto)
        return normalizar_cpf(texto)


class UsuarioPublico(BaseModel):
    id: uuid.UUID
    nome: str
    cpf: str
    email: str
    telefone: str
    status: bool
    perfil: str
    id_paciente: int | None = None
    id_profissional: int | None = None
    id_administrador: int | None = None


class TokenResposta(BaseModel):
    access_token: str
    token_type: str
    usuario: UsuarioPublico


def montar_usuario_publico(usuario: Usuario) -> UsuarioPublico:
    return UsuarioPublico(
        id=usuario.id,
        nome=usuario.nome,
        cpf=usuario.cpf,
        email=usuario.email,
        telefone=usuario.telefone,
        status=bool(usuario.status),
        perfil=perfil_de(usuario).value,
        id_paciente=usuario.paciente.id_paciente if usuario.paciente is not None else None,
        id_profissional=usuario.profissional.id_profissional if usuario.profissional is not None else None,
        id_administrador=(
            usuario.administrador.id_administrador if usuario.administrador is not None else None
        ),
    )
