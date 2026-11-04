"""Rotas de recuperação de senha: pedir o código por e-mail e redefinir."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies.database import get_db
from schemas.comum import MensagemResposta
from schemas.recuperacao_senha import (
    DesafioRecuperacaoResposta,
    EsqueciSenhaEntrada,
    RedefinirSenhaEntrada,
)
from services.RecuperacaoService.recuperacao_senha import ServicoRecuperacaoSenha, validade_minutos

router = APIRouter(prefix="/auth/senha", tags=["Recuperação de senha"])


def get_servico_recuperacao(db: Annotated[Session, Depends(get_db)]) -> ServicoRecuperacaoSenha:
    """Fornece o serviço de recuperação de senha ligado à sessão do banco."""
    return ServicoRecuperacaoSenha(db)


ServicoRecuperacaoDep = Annotated[ServicoRecuperacaoSenha, Depends(get_servico_recuperacao)]


@router.post(
    "/esqueci",
    response_model=DesafioRecuperacaoResposta,
    summary="Esqueci a senha, etapa 1: e-mail",
    description=(
        "Recebe o e-mail da conta e envia um código de recuperação para ele. A resposta é "
        "a mesma exista a conta ou não. Use o `id_desafio` e o código em `/auth/senha/redefinir`."
    ),
    responses={
        422: {"model": MensagemResposta},
        503: {"model": MensagemResposta},
    },
)
def esqueci_senha(
    servico: ServicoRecuperacaoDep,
    dados: EsqueciSenhaEntrada,
) -> DesafioRecuperacaoResposta:
    """Etapa 1: envia o código de recuperação por e-mail.

    Responde 422 com e-mail inválido e 503 se o e-mail não sair.
    """
    desafio = servico.solicitar(dados.email)
    minutos = max(1, desafio.expira_em_segundos // 60)
    unidade = "minuto" if minutos == 1 else "minutos"
    return DesafioRecuperacaoResposta(
        mensagem=(
            f"Se existir uma conta com este e-mail, enviamos um código de recuperação para "
            f"{desafio.email_mascarado}. Ele vale por {minutos} {unidade} e só pode ser usado "
            "uma vez."
        ),
        id_desafio=desafio.id_desafio,
        email_mascarado=desafio.email_mascarado,
        expira_em_segundos=desafio.expira_em_segundos,
    )


@router.post(
    "/redefinir",
    response_model=MensagemResposta,
    summary="Esqueci a senha, etapa 2: código e nova senha",
    description=(
        "Confere o código recebido por e-mail e grava a nova senha. Encerra as sessões "
        "abertas da conta."
    ),
    responses={
        400: {"model": MensagemResposta},
        403: {"model": MensagemResposta},
        422: {"model": MensagemResposta},
        429: {"model": MensagemResposta},
    },
)
def redefinir_senha(
    servico: ServicoRecuperacaoDep,
    dados: RedefinirSenhaEntrada,
) -> MensagemResposta:
    """Etapa 2: confere o código e troca a senha.

    Responde 400 com código inválido, expirado ou incorreto (ou senha igual à
    atual), 403 com conta banida, 422 com dados inválidos e 429 com a conta
    bloqueada por tentativas.
    """
    servico.redefinir(dados.id_desafio, dados.codigo, dados.nova_senha)
    return MensagemResposta(mensagem="Senha redefinida com sucesso. Entre com a nova senha.")