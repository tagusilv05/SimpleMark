"""Dependências do login. As rotas do grupo continuam usando só get_db."""

import uuid
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from core.envio_email import enviar_email
from core.excecoes import ErroNegocio
from core.perfil import PerfilUsuario, perfil_de
from core.seguranca import TokenInvalido, ler_token_acesso
from dependencies.database import get_db
from models.acesso import SessaoLogin
from models.models import Usuario
from repositories.usuario import RepositorioUsuario
from services.CadastroService.cadastro import ServicoCadastro
from services.CadastroService.validacao_profissional import ServicoValidacaoProfissional
from services.LoginService.autenticacao import ServicoAutenticacao
from services.RecuperacaoService.recuperacao import ServicoRecuperacaoSenha
from services.SessaoService.sessao import ServicoSessao

esquema_bearer = HTTPBearer(auto_error=False)

DbSession = Annotated[Session, Depends(get_db)]


def get_servico_cadastro(db: DbSession) -> ServicoCadastro:
    return ServicoCadastro(db)


def get_servico_autenticacao(db: DbSession) -> ServicoAutenticacao:
    return ServicoAutenticacao(db)


def get_servico_sessao(db: DbSession) -> ServicoSessao:
    return ServicoSessao(db)


def get_servico_recuperacao(db: DbSession) -> ServicoRecuperacaoSenha:
    return ServicoRecuperacaoSenha(db)


def get_enviador_email() -> Callable[[str, str, str], None]:
    """Função que envia o e-mail. Os testes trocam por uma que só guarda a mensagem."""
    return enviar_email


def get_servico_validacao(db: DbSession) -> ServicoValidacaoProfissional:
    return ServicoValidacaoProfissional(db)


def sessao_atual(
    db: DbSession,
    credenciais: Annotated[HTTPAuthorizationCredentials | None, Depends(esquema_bearer)],
) -> SessaoLogin:
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
    usuario = RepositorioUsuario(db).buscar_por_id(sessao.id_usuario)
    if usuario is None:
        raise ErroNegocio("Token inválido. Entre novamente.", 401)
    if not usuario.status:
        raise ErroNegocio("Esta conta não está ativa. Entre em contato com o administrador.", 401)
    return usuario


def administrador_atual(usuario: Annotated[Usuario, Depends(usuario_atual)]) -> Usuario:
    if perfil_de(usuario) != PerfilUsuario.ADMINISTRADOR:
        raise ErroNegocio(
            "Somente o administrador pode validar o cadastro do profissional de saúde.",
            403,
        )
    return usuario


ServicoCadastroDep = Annotated[ServicoCadastro, Depends(get_servico_cadastro)]
ServicoAutenticacaoDep = Annotated[ServicoAutenticacao, Depends(get_servico_autenticacao)]
ServicoValidacaoDep = Annotated[ServicoValidacaoProfissional, Depends(get_servico_validacao)]
ServicoSessaoDep = Annotated[ServicoSessao, Depends(get_servico_sessao)]
ServicoRecuperacaoDep = Annotated[ServicoRecuperacaoSenha, Depends(get_servico_recuperacao)]
EnviadorEmailDep = Annotated[Callable[[str, str, str], None], Depends(get_enviador_email)]
SessaoAtual = Annotated[SessaoLogin, Depends(sessao_atual)]
UsuarioAtual = Annotated[Usuario, Depends(usuario_atual)]
AdministradorAtual = Annotated[Usuario, Depends(administrador_atual)]