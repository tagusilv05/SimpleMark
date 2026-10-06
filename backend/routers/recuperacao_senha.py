from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Body

from core.parametros import recuperacao_codigo_minutos, recuperacao_reenvio_segundos
from dependencies.autenticacao import EnviadorEmailDep, ServicoRecuperacaoDep
from schemas.comum import MensagemResposta
from schemas.recuperacao import (
    RedefinirSenhaEntrada,
    SolicitarCodigoEntrada,
    SolicitarCodigoResposta,
    VerificarCodigoEntrada,
    VerificarCodigoResposta,
)

router = APIRouter(prefix="/auth/recuperacao", tags=["Recuperação de senha"])


@router.post(
    "/solicitar",
    response_model=SolicitarCodigoResposta,
    summary="Pedir o código por e-mail",
    description=(
        "Envia um código de 6 caracteres (letras e números) para o e-mail da conta. "
        "A resposta é sempre a mesma, exista conta ou não, para não revelar quem está cadastrado. "
        "Para pedir outro código é preciso esperar o intervalo de reenvio. "
        "O código novo substitui o anterior."
    ),
    responses={422: {"model": MensagemResposta}},
)
def solicitar_codigo(
    servico: ServicoRecuperacaoDep,
    enviador: EnviadorEmailDep,
    tarefas: BackgroundTasks,
    dados: Annotated[
        SolicitarCodigoEntrada,
        Body(openapi_examples={"paciente": {"summary": "Paciente", "value": {"email": "nordestino1971+paciente@gmail.com"}}}),
    ],
) -> SolicitarCodigoResposta:
    envio = servico.solicitar(dados.email)
    if envio is not None:
        # O e-mail sai depois da resposta: o tempo de espera não revela se a conta existe.
        tarefas.add_task(enviador, envio.destinatario, envio.assunto, envio.texto)
    minutos = recuperacao_codigo_minutos()
    return SolicitarCodigoResposta(
        mensagem=(
            "Se o e-mail estiver cadastrado, enviamos um código de 6 caracteres. "
            f"Ele vale por {minutos} {'minuto' if minutos == 1 else 'minutos'}."
        ),
        reenvio_em_segundos=recuperacao_reenvio_segundos(),
    )


@router.post(
    "/verificar",
    response_model=VerificarCodigoResposta,
    summary="Conferir o código",
    description=(
        "Confere o código recebido por e-mail. Se estiver certo, devolve o token que libera "
        "a troca da senha. Depois de 5 códigos errados, o código é invalidado e é preciso pedir outro."
    ),
    responses={400: {"model": MensagemResposta}, 422: {"model": MensagemResposta}},
)
def verificar_codigo(
    servico: ServicoRecuperacaoDep,
    dados: Annotated[
        VerificarCodigoEntrada,
        Body(
            openapi_examples={
                "paciente": {
                    "summary": "Paciente",
                    "value": {"email": "nordestino1971+paciente@gmail.com", "codigo": "AB3K9Z"},
                }
            }
        ),
    ],
) -> VerificarCodigoResposta:
    resultado = servico.verificar(dados.email, dados.codigo)
    return VerificarCodigoResposta(
        token_redefinicao=resultado.token,
        expira_em_segundos=resultado.expira_em_segundos,
    )


@router.post(
    "/redefinir",
    response_model=MensagemResposta,
    summary="Definir a nova senha",
    description=(
        "Troca a senha usando o token da etapa anterior. O token vale uma única vez. "
        "Ao concluir, o bloqueio de login é zerado e todas as sessões da conta são encerradas."
    ),
    responses={400: {"model": MensagemResposta}, 422: {"model": MensagemResposta}},
)
def redefinir_senha(
    servico: ServicoRecuperacaoDep,
    dados: Annotated[
        RedefinirSenhaEntrada,
        Body(
            openapi_examples={
                "paciente": {
                    "summary": "Paciente",
                    "value": {
                        "token_redefinicao": "cole-aqui-o-token-da-etapa-anterior",
                        "nova_senha": "NovaSenha123",
                        "confirmar_senha": "NovaSenha123",
                    },
                }
            }
        ),
    ],
) -> MensagemResposta:
    servico.redefinir(dados.token_redefinicao, dados.nova_senha)
    return MensagemResposta(mensagem="Senha redefinida com sucesso. Entre com a nova senha.")
