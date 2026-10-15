"""Rotas do administrador: validação de profissionais, banimentos e log de ações.

Todas exigem login de administrador: sem token responde 401 e, com outro
perfil, 403.
"""

from typing import Annotated

from fastapi import APIRouter, Body

from dependencies.autenticacao import AdministradorAtual, ServicoAdministracaoDep, ServicoValidacaoDep
from schemas.administracao import BanirEntrada, IdsUsuariosResposta, LogAcaoResposta
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
    administracao: ServicoAdministracaoDep,
    _admin: AdministradorAtual,
) -> list[ProfissionalPendenteResposta]:
    """Lista os profissionais que aguardam validação, sem os banidos.

    Somente administrador.
    """
    pendentes = administracao.sem_banidos(servico.listar_pendentes())
    return [ProfissionalPendenteResposta.de_profissional(item) for item in pendentes]


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
    administracao: ServicoAdministracaoDep,
    admin: AdministradorAtual,
) -> UsuarioPublico:
    """Ativa a conta do profissional e registra a ação no log.

    Somente administrador. Responde 404 se o profissional não existir e 409 se ele
    já estiver validado ou banido.
    """
    administracao.recusar_validacao_se_banido(id_profissional)
    usuario = servico.validar(id_profissional)
    administracao.registrar_validacao(admin, id_profissional, usuario.id)
    return montar_usuario_publico(usuario)


@router.get(
    "/usuarios/ids",
    response_model=IdsUsuariosResposta,
    summary="Buscar IDs de profissionais e pacientes",
    responses={401: {"model": MensagemResposta}, 403: {"model": MensagemResposta}},
)
def listar_ids_usuarios(
    administracao: ServicoAdministracaoDep,
    _admin: AdministradorAtual,
) -> IdsUsuariosResposta:
    """Lista os IDs de profissionais e pacientes, sem os banidos.

    Somente administrador.
    """
    return administracao.listar_ids_usuarios()


@router.post(
    "/profissionais/{id_profissional}/banir",
    response_model=MensagemResposta,
    summary="Banir profissional",
    responses={
        401: {"model": MensagemResposta},
        403: {"model": MensagemResposta},
        404: {"model": MensagemResposta},
        409: {"model": MensagemResposta},
    },
)
def banir_profissional(
    id_profissional: int,
    administracao: ServicoAdministracaoDep,
    admin: AdministradorAtual,
    dados: Annotated[BanirEntrada, Body()] = BanirEntrada(),
) -> MensagemResposta:
    """Bane o profissional, encerra as sessões dele e registra no log.

    Somente administrador; o motivo é opcional. Responde 404 se o profissional não
    existir, 403 se a conta for de administrador e 409 se já estiver banida.
    """
    administracao.banir_profissional(id_profissional, admin, dados.motivo)
    return MensagemResposta(mensagem="O profissional foi banido.")


@router.post(
    "/pacientes/{id_paciente}/banir",
    response_model=MensagemResposta,
    summary="Banir paciente",
    responses={
        401: {"model": MensagemResposta},
        403: {"model": MensagemResposta},
        404: {"model": MensagemResposta},
        409: {"model": MensagemResposta},
    },
)
def banir_paciente(
    id_paciente: int,
    administracao: ServicoAdministracaoDep,
    admin: AdministradorAtual,
    dados: Annotated[BanirEntrada, Body()] = BanirEntrada(),
) -> MensagemResposta:
    """Bane o paciente, encerra as sessões dele e registra no log.

    Somente administrador; o motivo é opcional. Responde 404 se o paciente não
    existir, 403 se a conta for de administrador e 409 se já estiver banida.
    """
    administracao.banir_paciente(id_paciente, admin, dados.motivo)
    return MensagemResposta(mensagem="O paciente foi banido.")


@router.get(
    "/logs",
    response_model=list[LogAcaoResposta],
    summary="Mostrar os logs das ações do administrador",
    responses={401: {"model": MensagemResposta}, 403: {"model": MensagemResposta}},
)
def listar_logs(
    administracao: ServicoAdministracaoDep,
    _admin: AdministradorAtual,
) -> list[LogAcaoResposta]:
    """Lista as ações registradas pelos administradores. Somente administrador."""
    return administracao.listar_logs()