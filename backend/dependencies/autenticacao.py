"""Dependências do login. As rotas do grupo continuam usando só get_db."""

import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from core.excecoes import ErroNegocio
from core.perfil import PerfilUsuario, perfil_de
from core.seguranca import TokenInvalido, ler_token_acesso
from dependencies.database import get_db
from models.acesso import SessaoLogin
from models.models import Paciente, Usuario
from repositories.usuario import RepositorioUsuario
from services.AvaliacaoService.avaliacao import ServicoAvaliacao
from repositories.administracao import RepositorioAdministracao
from services.AdministracaoService.administracao import ServicoAdministracao
from services.CadastroService.cadastro import ServicoCadastro
from services.CadastroService.validacao_profissional import ServicoValidacaoProfissional
from services.LoginService.autenticacao import ServicoAutenticacao
from services.SessaoService.sessao import ServicoSessao

esquema_bearer = HTTPBearer(auto_error=False)

DbSession = Annotated[Session, Depends(get_db)]


def get_servico_cadastro(db: DbSession) -> ServicoCadastro:
    """Fornece o serviço de cadastro ligado à sessão do banco."""
    return ServicoCadastro(db)


def get_servico_autenticacao(db: DbSession) -> ServicoAutenticacao:
    """Fornece o serviço de autenticação ligado à sessão do banco."""
    return ServicoAutenticacao(db)


def get_servico_sessao(db: DbSession) -> ServicoSessao:
    """Fornece o serviço de sessão de login ligado à sessão do banco."""
    return ServicoSessao(db)


def get_servico_validacao(db: DbSession) -> ServicoValidacaoProfissional:
    """Fornece o serviço de validação de profissional ligado à sessão do banco."""
    return ServicoValidacaoProfissional(db)


def get_servico_avaliacao(db: DbSession) -> ServicoAvaliacao:
    """Fornece o serviço de avaliação ligado à sessão do banco."""
    return ServicoAvaliacao(db)

def get_servico_administracao(db: DbSession) -> ServicoAdministracao:
    """Fornece o serviço de administração ligado à sessão do banco."""
    return ServicoAdministracao(db)


def sessao_atual(
    db: DbSession,
    credenciais: Annotated[HTTPAuthorizationCredentials | None, Depends(esquema_bearer)],
) -> SessaoLogin:
    """Lê o token Bearer e devolve a sessão de login válida, renovando a atividade.

    Responde 401 sem token, com token inválido ou com sessão encerrada/expirada.
    """
    if credenciais is None or credenciais.scheme.lower() != "bearer":
        raise ErroNegocio("Informe o token de acesso para continuar.", 401)
    try:
        dados = ler_token_acesso(credenciais.credentials)
        id_usuario = uuid.UUID(str(dados["sub"]))
        id_sessao = uuid.UUID(str(dados["sid"]))
    except (TokenInvalido, KeyError, TypeError, ValueError, AttributeError) as exc:
        raise ErroNegocio("Token inválido. Entre novamente.", 401) from exc
    return ServicoSessao(db).validar_e_renovar(id_sessao, id_usuario)


def usuario_atual(db: DbSession, sessao: Annotated[SessaoLogin, Depends(sessao_atual)]) -> Usuario:
    """Devolve o usuário dono da sessão atual.

    Responde 401 se o usuário não existir ou estiver inativo, e 403 se estiver banido.
    """
    usuario = RepositorioUsuario(db).buscar_por_id(sessao.id_usuario)
    if usuario is None:
        raise ErroNegocio("Token inválido. Entre novamente.", 401)
    if not usuario.status:
        raise ErroNegocio("Esta conta não está ativa. Entre em contato com o administrador.", 401)
    if RepositorioAdministracao(db).esta_banido(usuario.id):
        raise ErroNegocio("Esta conta foi banida pelo administrador.", 403)
    return usuario


def administrador_atual(usuario: Annotated[Usuario, Depends(usuario_atual)]) -> Usuario:
    """Exige que o usuário logado seja administrador; caso contrário, responde 403."""
    if perfil_de(usuario) != PerfilUsuario.ADMINISTRADOR:
        raise ErroNegocio(
            "Somente o administrador pode validar o cadastro do profissional de saúde.",
            403,
        )
    return usuario


def paciente_atual(usuario: Annotated[Usuario, Depends(usuario_atual)]) -> Paciente:
    """Exige que o usuário logado seja paciente e devolve o registro de paciente.

    Caso contrário, responde 403.
    """
    if perfil_de(usuario) != PerfilUsuario.PACIENTE:
        raise ErroNegocio("Somente o paciente pode avaliar uma consulta.", 403)
    return usuario.paciente


ServicoCadastroDep = Annotated[ServicoCadastro, Depends(get_servico_cadastro)]
ServicoAutenticacaoDep = Annotated[ServicoAutenticacao, Depends(get_servico_autenticacao)]
ServicoValidacaoDep = Annotated[ServicoValidacaoProfissional, Depends(get_servico_validacao)]
ServicoAdministracaoDep = Annotated[ServicoAdministracao, Depends(get_servico_administracao)]
ServicoSessaoDep = Annotated[ServicoSessao, Depends(get_servico_sessao)]
SessaoAtual = Annotated[SessaoLogin, Depends(sessao_atual)]
UsuarioAtual = Annotated[Usuario, Depends(usuario_atual)]
AdministradorAtual = Annotated[Usuario, Depends(administrador_atual)]
ServicoAvaliacaoDep = Annotated[ServicoAvaliacao, Depends(get_servico_avaliacao)]
PacienteAtual = Annotated[Paciente, Depends(paciente_atual)]