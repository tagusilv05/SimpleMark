from typing import Annotated

from fastapi import APIRouter, Body

from dependencies.autenticacao import ServicoAutenticacaoDep, ServicoSessaoDep, SessaoAtual, UsuarioAtual
from schemas.auth import LoginEntrada, TokenResposta, UsuarioPublico, montar_usuario_publico
from schemas.comum import MensagemResposta

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/login",
    response_model=TokenResposta,
    summary="Entrar",
    responses={
        401: {"model": MensagemResposta},
        403: {"model": MensagemResposta},
        422: {"model": MensagemResposta},
        429: {"model": MensagemResposta},
    },
)
def login(
    servico: ServicoAutenticacaoDep,
    dados: Annotated[
        LoginEntrada,
        Body(
            openapi_examples={
                "paciente": {
                    "summary": "Paciente",
                    "value": {
                        "identificador": "nordestino1971+paciente@gmail.com",
                        "senha": "Senha123",
                    },
                },
                "administrador": {
                    "summary": "Administradora Helena",
                    "value": {
                        "identificador": "nordestino1971@gmail.com",
                        "senha": "Senha123",
                    },
                },
            }
        ),
    ],
) -> TokenResposta:
    resultado = servico.autenticar(dados.identificador, dados.senha)
    return TokenResposta(
        access_token=resultado.token,
        token_type="bearer",
        usuario=montar_usuario_publico(resultado.usuario),
    )


@router.get(
    "/eu",
    response_model=UsuarioPublico,
    summary="Conta autenticada",
    responses={401: {"model": MensagemResposta}},
)
def eu(usuario: UsuarioAtual) -> UsuarioPublico:
    return montar_usuario_publico(usuario)


@router.post(
    "/sair",
    status_code=204,
    summary="Encerrar a sessão atual",
    responses={401: {"model": MensagemResposta}},
)
def sair(sessao: SessaoAtual, servico: ServicoSessaoDep) -> None:
    servico.encerrar(sessao)
