"""Rotas de autenticação: login em duas etapas, conta logada e logout."""

from typing import Annotated

from fastapi import APIRouter, Body

from dependencies.autenticacao import ServicoAutenticacaoDep, ServicoSessaoDep, SessaoAtual, UsuarioAtual
from schemas.auth import (
    ConfirmarLoginEntrada,
    DesafioLoginResposta,
    LoginEntrada,
    TokenResposta,
    UsuarioPublico,
    montar_usuario_publico,
)
from schemas.comum import MensagemResposta

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/login",
    response_model=DesafioLoginResposta,
    summary="Entrar, etapa 1: senha",
    description=(
        "Confere o e-mail ou CPF e a senha e envia um código de confirmação para o e-mail "
        "da conta. Não devolve token: use o `id_desafio` e o código em `/auth/login/confirmar`."
    ),
    responses={
        401: {"model": MensagemResposta},
        403: {"model": MensagemResposta},
        422: {"model": MensagemResposta},
        429: {"model": MensagemResposta},
        503: {"model": MensagemResposta},
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
) -> DesafioLoginResposta:
    """Etapa 1 do login: confere a senha e envia o código de confirmação por e-mail.

    Responde 401 com credencial errada, 403 com conta banida ou inativa, 422 com
    identificador inválido, 429 com a conta bloqueada por tentativas e 503 se o
    e-mail não sair.
    """
    desafio = servico.iniciar_login(dados.identificador, dados.senha)
    minutos = max(1, desafio.expira_em_segundos // 60)
    unidade = "minuto" if minutos == 1 else "minutos"
    return DesafioLoginResposta(
        mensagem=(
            f"Enviamos um código de confirmação para {desafio.email_mascarado}. "
            f"Ele vale por {minutos} {unidade} e só pode ser usado uma vez."
        ),
        id_desafio=desafio.id_desafio,
        email_mascarado=desafio.email_mascarado,
        expira_em_segundos=desafio.expira_em_segundos,
    )


@router.post(
    "/login/confirmar",
    response_model=TokenResposta,
    summary="Entrar, etapa 2: código do e-mail",
    description="Confere o código recebido por e-mail. Se estiver certo, abre a sessão e devolve o token.",
    responses={
        401: {"model": MensagemResposta},
        403: {"model": MensagemResposta},
        422: {"model": MensagemResposta},
        429: {"model": MensagemResposta},
    },
)
def confirmar_login(
    servico: ServicoAutenticacaoDep,
    dados: Annotated[
        ConfirmarLoginEntrada,
        Body(
            openapi_examples={
                "codigo": {
                    "summary": "Código recebido por e-mail",
                    "value": {
                        "id_desafio": "00000000-0000-0000-0000-000000000000",
                        "codigo": "123456",
                    },
                }
            }
        ),
    ],
) -> TokenResposta:
    """Etapa 2 do login: confere o código e, se estiver certo, abre a sessão.

    Responde 401 com código inválido, expirado ou incorreto, 403 com conta banida
    ou inativa e 429 com a conta bloqueada por tentativas.
    """
    resultado = servico.confirmar_login(dados.id_desafio, dados.codigo)
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
    """Devolve os dados públicos da conta logada. Sem token válido, responde 401."""
    return montar_usuario_publico(usuario)


@router.post(
    "/sair",
    status_code=204,
    summary="Encerrar a sessão atual",
    responses={401: {"model": MensagemResposta}},
)
def sair(sessao: SessaoAtual, servico: ServicoSessaoDep) -> None:
    """Encerra a sessão do token atual (logout). Sem token válido, responde 401."""
    servico.encerrar(sessao)
