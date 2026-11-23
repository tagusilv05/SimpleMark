# CRIADO: JOAO MARCOS
"""Rotas da conta do usuário (paciente e profissional): dados pessoais, endereço,
senha, inativação e exclusão.

Todas exigem login (401 sem token) e só agem sobre a própria conta: um id de
outro usuário responde 403.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.excecoes import ErroNegocio
from dependencies.autenticacao import UsuarioAtual
from dependencies.database import get_db
from models.models import Usuario
from repositories.usuario_minha_conta import (
    buscar_endereco_por_usuario as repositories_buscar_endereco_por_usuario,
)
from schemas.usuario_minha_conta import (
    AlterarSenhaInput,
    AltereEnderecoInput,
    AltereEnderecoOutput,
    AltereInfoPessoalInput,
    AltereInfoPessoalOutput,
    BuscarInfoEnderecoOutput,
    BuscarInfoUsuarioOutput,
    ExcluirUsuarioInput,
)
from services.porfissional_minha_conta import excluir_profissional as service_excluir_profissional
from services.usuario_minha_conta import (
    altera_endereco as service_altera_endereco,
    altera_info_pessoal as services_altera_info_pessoal,
    alterar_senha as service_alterar_senha,
    excluir_paciente as service_excluir_paciente,
    inativar_usuario as service_inativar_usuario,
)

router = APIRouter()


def exigir_propria_conta(usuario: Usuario, id_usuario) -> None:
    """Recusa (403) quando o id pedido não é o da conta logada.

    Args:
        usuario (Usuario): Usuário da conta logada.
        id_usuario (uuid.UUID | str): Id da conta que se quer acessar.

    Raises:
        ErroNegocio: Quando ``id_usuario`` não é o id da conta logada (403).
    """
    if str(usuario.id) != str(id_usuario):
        raise ErroNegocio("Você só pode acessar os dados da sua própria conta.", 403)


def _executar(acao, mensagem_erro: str, status_valor: int = 400):
    """Roda a ação traduzindo ValueError (status_valor) e erros inesperados (500).

    ErroNegocio passa direto, com o próprio status.

    Args:
        acao (Callable[[], Any]): Função sem argumentos a executar.
        mensagem_erro (str): Mensagem devolvida nos erros inesperados (500).
        status_valor (int): Status HTTP usado quando a ação levanta ``ValueError``.

    Returns:
        Any: O retorno de ``acao``.

    Raises:
        ErroNegocio: Repassado sem alteração quando levantado pela ação.
        HTTPException: Com ``status_valor`` para ``ValueError`` e 500 para outros erros.
    """
    try:
        return acao()
    except ErroNegocio:
        raise
    except ValueError as erro:
        raise HTTPException(status_code=status_valor, detail=str(erro))
    except Exception as erro:
        print(f"ERRO REAL: {erro}")
        raise HTTPException(status_code=500, detail=mensagem_erro)


@router.get("/buscar-info-usuario/{id_usuario}", response_model=BuscarInfoUsuarioOutput)
def buscar_info_usuario(id_usuario: uuid.UUID, usuario: UsuarioAtual):
    """Dados pessoais da conta logada (o id precisa ser o dela).

    Args:
        id_usuario (uuid.UUID): Id da conta; precisa ser o da conta logada.
        usuario (Usuario): Usuário logado, injetado pelo FastAPI.

    Returns:
        Usuario: A conta logada, serializada como ``BuscarInfoUsuarioOutput``.
    """
    exigir_propria_conta(usuario, id_usuario)
    return usuario


@router.get("/buscar-info-endereco/{id_usuario}", response_model=BuscarInfoEnderecoOutput)
def buscar_info_endereco(id_usuario: uuid.UUID, usuario: UsuarioAtual, db: Session = Depends(get_db)):
    """Endereço da conta logada. Responde 404 se ela não tiver endereço.

    Args:
        id_usuario (uuid.UUID): Id da conta; precisa ser o da conta logada.
        usuario (Usuario): Usuário logado, injetado pelo FastAPI.
        db (Session): Sessão do banco de dados, injetada pelo FastAPI.

    Returns:
        object: Endereço da conta, serializado como ``BuscarInfoEnderecoOutput``.

    Raises:
        ErroNegocio: Quando a conta não tem endereço cadastrado (404).
    """
    exigir_propria_conta(usuario, id_usuario)
    endereco = repositories_buscar_endereco_por_usuario(id_usuario=usuario.id, db=db)
    if endereco is None:
        raise ErroNegocio("Endereço não cadastrado.", 404)
    return endereco


@router.put("/altera-info-pessoal", response_model=AltereInfoPessoalOutput)
def altera_info_pessoal(dados: AltereInfoPessoalInput, usuario: UsuarioAtual, db: Session = Depends(get_db)):
    """Altera nome, e-mail e telefone (só os campos enviados) e devolve os dados atualizados.

    Responde 409 se o e-mail já for de outra conta e 422 com dado inválido.

    Args:
        dados (AltereInfoPessoalInput): Id da conta e os campos a alterar.
        usuario (Usuario): Usuário logado, injetado pelo FastAPI.
        db (Session): Sessão do banco de dados, injetada pelo FastAPI.

    Returns:
        AltereInfoPessoalOutput: Dados pessoais atualizados.
    """
    exigir_propria_conta(usuario, dados.id)
    return _executar(
        lambda: services_altera_info_pessoal(dados=dados, db=db),
        "Erro interno ao alterar as informações do usuário",
    )


@router.put("/altera-endereco", response_model=AltereEnderecoOutput)
def altera_endereco(dados: AltereEnderecoInput, usuario: UsuarioAtual, db: Session = Depends(get_db)):
    """Altera o endereço (só os campos enviados) e devolve o endereço atualizado.

    Args:
        dados (AltereEnderecoInput): Id da conta e os campos do endereço a alterar.
        usuario (Usuario): Usuário logado, injetado pelo FastAPI.
        db (Session): Sessão do banco de dados, injetada pelo FastAPI.

    Returns:
        AltereEnderecoOutput: Endereço atualizado.
    """
    exigir_propria_conta(usuario, dados.id_usuario)
    return _executar(
        lambda: service_altera_endereco(dados=dados, db=db),
        "Erro interno ao alterar o endereço do usuário",
    )


@router.put("/alterar-senha")
def alterar_senha(dados: AlterarSenhaInput, usuario: UsuarioAtual, db: Session = Depends(get_db)):
    """Troca a senha da conta logada. Responde 400 se a senha atual estiver incorreta.

    Args:
        dados (AlterarSenhaInput): Senha atual e nova senha.
        usuario (Usuario): Usuário logado, injetado pelo FastAPI.
        db (Session): Sessão do banco de dados, injetada pelo FastAPI.

    Returns:
        dict: Mensagem de sucesso.
    """
    _executar(
        lambda: service_alterar_senha(usuario.id, dados.senha_atual, dados.nova_senha, db),
        "Erro interno ao alterar a senha",
    )
    return {"mensagem": "Senha alterada com sucesso"}


@router.delete("/excluir-usuario")
def deletar_usuario(dados: ExcluirUsuarioInput, usuario: UsuarioAtual, db: Session = Depends(get_db)):
    """Exclui a conta logada (paciente ou profissional) e os dados ligados a ela.

    Responde 409 se houver consulta agendada por vir e 404 se a conta não for do
    tipo informado.

    Args:
        dados (ExcluirUsuarioInput): Id da conta e tipo (paciente ou profissional).
        usuario (Usuario): Usuário logado, injetado pelo FastAPI.
        db (Session): Sessão do banco de dados, injetada pelo FastAPI.

    Returns:
        dict: Mensagem de sucesso.
    """
    exigir_propria_conta(usuario, dados.id)
    if dados.tipo == "paciente":
        acao = lambda: service_excluir_paciente(id_usuario=dados.id, db=db)  # noqa: E731
    else:
        acao = lambda: service_excluir_profissional(id_usuario=dados.id, db=db)  # noqa: E731
    _executar(acao, "Erro interno ao excluir o usuário", status_valor=404)
    return {"mensagem": "Usuário excluído com sucesso"}


@router.patch("/inativar-usuario")
def inativar_usuario(id_usuario: uuid.UUID, usuario: UsuarioAtual, db: Session = Depends(get_db)):
    """Inativa a conta logada (id_usuario na query string) e encerra as sessões dela.

    Args:
        id_usuario (uuid.UUID): Id da conta; precisa ser o da conta logada.
        usuario (Usuario): Usuário logado, injetado pelo FastAPI.
        db (Session): Sessão do banco de dados, injetada pelo FastAPI.

    Returns:
        dict: Mensagem de sucesso.
    """
    exigir_propria_conta(usuario, id_usuario)
    _executar(
        lambda: service_inativar_usuario(id_usuario=id_usuario, db=db),
        "Erro interno ao inativar usuário",
        status_valor=404,
    )
    return {"mensagem": "Usuário inativado com sucesso"}
