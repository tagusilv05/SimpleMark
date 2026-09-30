# Arquivo criado por Victor e Gustavo
from typing import Annotated

from fastapi import APIRouter, Body

from app.api.deps import ServicoAutenticacaoDep, UsuarioAtual
from app.schemas.auth import LoginEntrada, TokenResposta, UsuarioPublico, montar_usuario_publico
from app.schemas.comum import MensagemResposta

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/login",
    response_model=TokenResposta,
    summary="Entrar",
    description=(
        "Entra como paciente, profissional de saúde ou administrador. "
        "O identificador pode ser o e-mail ou o CPF."
        "Após 5 tentativas de login com credenciais erradas, a conta fica bloqueada por 1 hora."
    ),
    responses={401: {"model": MensagemResposta}, 
               422: {"model": MensagemResposta},
               429: {"model": MensagemResposta, "description": "Conta bloqueada temporariamente devido a tentativas de login inválidas."}},
)
def login(
    servico: ServicoAutenticacaoDep,
    dados: Annotated[
        LoginEntrada,
        Body(
            openapi_examples={
                "paciente": {
                    "summary": "Paciente Maria",
                    "value": {
                        "identificador": "nordestino1971+paciente@gmail.com",
                        "senha": "Senha123",
                    },
                },
                "profissional": {
                    "summary": "Profissional de saúde Carlos",
                    "value": {
                        "identificador": "nordestino1971+profissional@gmail.com",
                        "senha": "Senha123",
                    },
                },
                "administrador": {
                    "summary": "Administradora Helena",
                    "description": "Administradores são inseridos direto no banco. Não há rota de cadastro.",
                    "value": {
                        "identificador": "nordestino1971@gmail.com",
                        "senha": "Senha123",
                    },
                },
            }
        ),
    ],
) -> TokenResposta:
    """Confere e-mail ou CPF e senha, e devolve o token.

    Passo a passo:
    1. O schema exige identificador e senha com no mínimo 8 caracteres.
    2. O service descobre se o identificador é e-mail ou CPF e confere a senha.
    3. Conta bloqueada por senhas erradas seguidas responde 429, com o tempo que falta.
    4. A resposta leva o token e os dados públicos, com o perfil da conta.
    """
    resultado = servico.autenticar(dados.identificador, dados.senha)
    return TokenResposta(
        access_token=resultado.token,
        token_type="bearer",
        usuario=montar_usuario_publico(resultado.usuario),
    )


@router.get(
    "/eu",
    response_model=UsuarioPublico,
    summary="Autenticar a conta",
    description=(
        "Confere o token e devolve a conta autenticada. "
        "Vale para paciente, profissional de saúde e administrador."
    ),
    responses={401: {"model": MensagemResposta}},
)
def eu(usuario: UsuarioAtual) -> UsuarioPublico:
    """Mostra quem está autenticado pelo token.

    Passo a passo:
    1. UsuarioAtual exige o token no cadeado Authorize.
    2. O token inválido responde 401 antes desta função.
    3. A resposta traz o perfil: paciente, profissional ou administrador.
    """
    return montar_usuario_publico(usuario)
