"""Entradas e saídas do login em duas etapas e da conta autenticada."""

import uuid

from pydantic import BaseModel, Field, field_validator

from core.perfil import perfil_de
from core.seguranca import TAMANHO_CODIGO_LOGIN
from core.validadores import normalizar_cpf, normalizar_email
from models.models import Usuario


class LoginEntrada(BaseModel):
    """Corpo de POST /auth/login: e-mail ou CPF e a senha.

    Com "@" o identificador é tratado como e-mail; sem, como CPF. Os dois
    chegam normalizados. A senha precisa ter ao menos 8 caracteres.
    """

    identificador: str = Field(min_length=1)
    senha: str

    @field_validator("senha")
    @classmethod
    def senha_minima(cls, valor: str) -> str:
        """Recusa senha com menos de 8 caracteres."""
        if len(valor) < 8:
            raise ValueError("A senha deve ter no mínimo 8 caracteres.")
        return valor

    @field_validator("identificador")
    @classmethod
    def identificador_preenchido(cls, valor: str) -> str:
        """Exige o identificador e o normaliza como e-mail (com "@") ou CPF."""
        texto = valor.strip()
        if not texto:
            raise ValueError("Informe o e-mail ou o CPF para entrar.")
        if "@" in texto:
            return normalizar_email(texto)
        return normalizar_cpf(texto)


class ConfirmarLoginEntrada(BaseModel):
    """Corpo de POST /auth/login/confirmar: o desafio e o código do e-mail."""

    id_desafio: uuid.UUID
    codigo: str

    @field_validator("codigo")
    @classmethod
    def codigo_somente_numeros(cls, valor: str) -> str:
        """Aceita só o código com a quantidade exata de dígitos (ASCII)."""
        texto = valor.strip()
        if len(texto) != TAMANHO_CODIGO_LOGIN or not (texto.isascii() and texto.isdigit()):
            raise ValueError(f"O código de confirmação deve ter {TAMANHO_CODIGO_LOGIN} números.")
        return texto


class DesafioLoginResposta(BaseModel):
    """Resposta de POST /auth/login: o desafio a confirmar, sem token.

    O código foi enviado ao e-mail mascarado e vale por expira_em_segundos.
    """

    mensagem: str
    id_desafio: uuid.UUID
    email_mascarado: str
    expira_em_segundos: int


class UsuarioPublico(BaseModel):
    """Dados da conta que podem ir para o cliente (sem senha).

    Resposta de /auth/eu, do cadastro e da validação de profissional; também
    vem dentro do TokenResposta. Só o id do perfil da conta vem preenchido.
    """

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
    """Resposta de POST /auth/login/confirmar: token bearer e a conta."""

    access_token: str
    token_type: str
    usuario: UsuarioPublico


def montar_usuario_publico(usuario: Usuario) -> UsuarioPublico:
    """Monta o UsuarioPublico com o perfil e os ids de paciente, profissional
    e administrador que a conta tiver.
    """
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
