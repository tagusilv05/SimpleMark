# Arquivo criado por Gustavo e Victor
"""Dependências do login e da autenticação.

A rota de autenticação recebe UsuarioAtual. O token identifica a conta
de paciente, profissional de saúde ou administrador.
"""

import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import ErroNegocio
from app.core.perfil import PerfilUsuario, perfil_de
from app.core.security import TokenInvalido, ler_token_acesso
from app.models.sessao import Sessao
from app.models.usuario import Usuario
from app.repositories.usuario import RepositorioUsuario
from app.services.autenticacao import ServicoAutenticacao
from app.services.cadastro import ServicoCadastro
from app.services.sessao import ServicoSessao
from app.services.validacao_profissional import ServicoValidacaoProfissional

# Esquema de autenticação Bearer - Serve para proteger as rotas da API que exigem login, garantindo que apenas usuários autenticados possam acessar.
# auto_error=False: Se o token não for fornecido, a função não levanta uma exceção e retorna None.
esquema_bearer = HTTPBearer(auto_error=False)

# Criei uma sessão para automatizar a conexão com o banco de dados e garantir que ela seja fechada corretamente a cada requisição, sem precisr abrir e fechar o banco manualmente.
DbSession = Annotated[Session, Depends(get_db)]

# Função para cadastrar novos usuários na API. Utilizamos o ServicoCadastro para realizar o cadastro.
def get_servico_cadastro(db: DbSession) -> ServicoCadastro:
    """Monta o service de cadastro com a sessão desta requisição.

    Passo a passo:
    1. O FastAPI chama get_db e injeta a sessão.
    2. Esta função devolve o service já apontando para essa sessão.
    """
    return ServicoCadastro(db)


def get_servico_autenticacao(db: DbSession) -> ServicoAutenticacao:
    """Monta o service de login com a sessão desta requisição.

    Passo a passo:
    1. O FastAPI abre a sessão do banco.
    2. Devolve o service que confere e-mail ou CPF e senha.
    """
    return ServicoAutenticacao(db)


def get_servico_sessao(db: DbSession) -> ServicoSessao:
    """Monta o service de sessão com a sessão do banco desta requisição."""
    return ServicoSessao(db)


def sessao_atual(
    db: DbSession,
    credenciais: Annotated[HTTPAuthorizationCredentials | None, Depends(esquema_bearer)],
) -> Sessao:
    """Lê o token e devolve a sessão de login, já conferida e renovada.

    Passo a passo:
    1. Sem o cabeçalho Authorization, responde 401.
    2. Confere a assinatura do JWT e lê o id do usuário (sub) e o da sessão (sid).
    3. Token sem sid, como os emitidos antes da sessão existir, é recusado com 401.
    4. O ServicoSessao confere se a sessão é desta conta, não foi encerrada e não
       passou 24h parada. Se vale, registra o uso e renova o prazo.
    """
    if credenciais is None or credenciais.scheme.lower() != "bearer":
        raise ErroNegocio("Informe o token de acesso para continuar.", 401)
    try:
        dados = ler_token_acesso(credenciais.credentials)
        id_usuario = int(dados["sub"])
        id_sessao = uuid.UUID(dados["sid"])
    except (TokenInvalido, KeyError, TypeError, ValueError, AttributeError) as exc:
        raise ErroNegocio("Token inválido. Entre novamente.", 401) from exc
    return ServicoSessao(db).validar_e_renovar(id_sessao, id_usuario)


SessaoAtual = Annotated[Sessao, Depends(sessao_atual)]


def usuario_atual(db: DbSession, sessao: SessaoAtual) -> Usuario:
    """Devolve a conta dona da sessão.

    Passo a passo:
    1. SessaoAtual já conferiu o token e a validade da sessão.
    2. Busca a conta da sessão. Se ela não existir mais, responde 401.
    3. Conta desativada perde o acesso na hora, mesmo com sessão válida (401).
    4. Devolve o usuário, com o perfil paciente, profissional ou administrador.
    """
    usuario = RepositorioUsuario(db).buscar_por_id(sessao.id_usuario)
    if usuario is None:
        raise ErroNegocio("Token inválido. Entre novamente.", 401)
    if not usuario.status:
        raise ErroNegocio("Esta conta não está ativa. Entre em contato com o administrador.", 401)
    return usuario


UsuarioAtual = Annotated[Usuario, Depends(usuario_atual)]


def get_servico_validacao(db: DbSession) -> ServicoValidacaoProfissional:
    """Monta o service que lista e valida o profissional de saúde.

    Passo a passo:
    1. O FastAPI abre a sessão do banco.
    2. Devolve o service usado pelas rotas do administrador.
    """
    return ServicoValidacaoProfissional(db)


def administrador_atual(usuario: UsuarioAtual) -> Usuario:
    """Exige que o token seja de um administrador ativo.

    Passo a passo:
    1. UsuarioAtual já conferiu o token.
    2. Se o perfil não for administrador, responde 403.
    3. Devolve a conta para a rota de validação.
    """
    if perfil_de(usuario) != PerfilUsuario.ADMINISTRADOR:
        raise ErroNegocio("Somente o administrador pode validar o cadastro do profissional de saúde.", 403)
    return usuario


ServicoCadastroDep = Annotated[ServicoCadastro, Depends(get_servico_cadastro)]
ServicoAutenticacaoDep = Annotated[ServicoAutenticacao, Depends(get_servico_autenticacao)]
ServicoValidacaoDep = Annotated[ServicoValidacaoProfissional, Depends(get_servico_validacao)]
ServicoSessaoDep = Annotated[ServicoSessao, Depends(get_servico_sessao)]
AdministradorAtual = Annotated[Usuario, Depends(administrador_atual)]
