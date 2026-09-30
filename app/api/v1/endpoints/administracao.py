# Arquivo criado por Victor
from fastapi import APIRouter

from app.api.deps import AdministradorAtual, ServicoValidacaoDep
from app.schemas.auth import UsuarioPublico, montar_usuario_publico
from app.schemas.cadastro import ProfissionalPendenteResposta
from app.schemas.comum import MensagemResposta

router = APIRouter(prefix="/administracao", tags=["Administração"])


@router.get(
    "/profissionais/pendentes",
    response_model=list[ProfissionalPendenteResposta],
    summary="Listar profissionais de saúde pendentes",
    description="Lista quem se cadastrou e ainda aguarda a validação do administrador.",
    responses={401: {"model": MensagemResposta}, 403: {"model": MensagemResposta}},
)
def listar_pendentes(
    servico: ServicoValidacaoDep,
    _admin: AdministradorAtual,
) -> list[ProfissionalPendenteResposta]:
    """Devolve os profissionais de saúde com conta ainda inativa.

    Passo a passo:
    1. AdministradorAtual exige o token de um administrador.
    2. O service busca status falso.
    3. A resposta traz o id usado na validação, mais nome, e-mail, CPF e conselho.
    """
    return [ProfissionalPendenteResposta.de_profissional(item) for item in servico.listar_pendentes()]


@router.post(
    "/profissionais/{id_profissional}/validar",
    response_model=UsuarioPublico,
    summary="Validar profissional de saúde",
    description="Libera o login do profissional de saúde depois da conferência do administrador.",
    responses={
        401: {"model": MensagemResposta},
        403: {"model": MensagemResposta},
        404: {"model": MensagemResposta},
        409: {"model": MensagemResposta},
    },
)
def validar_profissional(
    id_profissional: int,
    servico: ServicoValidacaoDep,
    _admin: AdministradorAtual,
) -> UsuarioPublico:
    """Ativa a conta do profissional de saúde.

    Passo a passo:
    1. AdministradorAtual exige o token de um administrador.
    2. O service procura o id e grava status verdadeiro.
    3. A resposta mostra a conta ativa, sem a senha.
    """
    return montar_usuario_publico(servico.validar(id_profissional))
