from fastapi import APIRouter

from dependencies.autenticacao import AdministradorAtual, ServicoValidacaoDep
from schemas.auth import UsuarioPublico, montar_usuario_publico
from schemas.cadastro import ProfissionalPendenteResposta
from schemas.comum import MensagemResposta

router = APIRouter(prefix="/administracao", tags=["Administração"])


@router.get(
    "/profissionais/pendentes",
    response_model=list[ProfissionalPendenteResposta],
    summary="Listar profissionais pendentes",
    responses={401: {"model": MensagemResposta}, 403: {"model": MensagemResposta}},
)
def listar_pendentes(
    servico: ServicoValidacaoDep,
    _admin: AdministradorAtual,
) -> list[ProfissionalPendenteResposta]:
    return [ProfissionalPendenteResposta.de_profissional(item) for item in servico.listar_pendentes()]


@router.post(
    "/profissionais/{id_profissional}/validar",
    response_model=UsuarioPublico,
    summary="Validar profissional",
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
    return montar_usuario_publico(servico.validar(id_profissional))
