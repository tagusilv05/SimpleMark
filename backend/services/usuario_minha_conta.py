"""Tela "Minha conta" do paciente: dados pessoais, endereço e exclusão."""

# CRIADO: JOAO MARCOS 

from sqlalchemy.orm import Session

from core.excecoes import ErroNegocio
from core.seguranca import gerar_hash_senha, verificar_senha
from core.tempo import agora_local, agora_utc
from repositories.administracao import RepositorioAdministracao
from repositories.credencial import RepositorioCredencial
from repositories.usuario import RepositorioUsuario
from repositories.usuario_minha_conta import (
    consulta_ainda_vai_acontecer as repositories_consulta_ainda_vai_acontecer,
    desvincular_logs_do_usuario as repositories_desvincular_logs_do_usuario,
    buscar_usuario_por_id as repositories_buscar_usuario_por_id,
    buscar_endereco_por_usuario as repositories_buscar_endereco_por_usuario,
    buscar_consultas_por_paciente as repositories_buscar_consultas_por_paciente,
    excluir_dados_consulta as repositories_excluir_dados_consulta,
    excluir_consultas_por_paciente as repositories_excluir_consultas_por_paciente,
    excluir_endereco_por_usuario as repositories_excluir_endereco_por_usuario
)

# Busca o usuário, verifica se está ativo e retorna o paciente associado
def verificar_paciente_usuario(id_usuario, db: Session):
    """Paciente ligado ao usuário.

    Levanta ValueError se o usuário não existir, estiver inativo ou não for
    paciente.
    """

    usuario = repositories_buscar_usuario_por_id(id_usuario=id_usuario,db=db)

    if usuario is None:
        raise ValueError("Usuário não encontrado")

    if not usuario.status:
        raise ValueError("Usuário está inativo")

    paciente = usuario.paciente

    if paciente is None:
        raise ValueError("Paciente não encontrado")

    return paciente


# Altera as informações pessoais do usuário
def altera_info_pessoal(dados, db: Session):
    """Atualiza nome, e-mail e telefone que vierem preenchidos.

    Levanta ValueError se o usuário não existir ou se o commit falhar.
    """

    usuario = repositories_buscar_usuario_por_id(dados.id, db)

    if not usuario:
        raise ValueError("Usuário não encontrado")

    if dados.email is not None and dados.email != usuario.email:
        dono = RepositorioUsuario(db).buscar_por_email(dados.email)
        if dono is not None and dono.id != usuario.id:
            raise ErroNegocio("Este e-mail já está em uso por outra conta.", 409)

    if dados.nome is not None:
        usuario.nome = dados.nome

    if dados.email is not None:
        usuario.email = dados.email

    if dados.telefone is not None:
        usuario.telefone = dados.telefone

    try:
        db.commit()
        db.refresh(usuario)

    except Exception:
        db.rollback()
        raise ValueError("Não foi possível alterar as informações pessoais")

    return usuario

# Altera as informações de endereço do usuário
def altera_endereco(dados, db: Session):
    """Atualiza os campos do endereço que vierem preenchidos.

    Levanta ValueError se o endereço não existir ou se o commit falhar.
    """

    endereco = repositories_buscar_endereco_por_usuario(dados.id_usuario, db)

    if not endereco:
        raise ValueError("Endereço não encontrado")

    if dados.cep is not None:
        endereco.cep = dados.cep

    if dados.cidade is not None:
        endereco.cidade = dados.cidade

    if dados.logradouro is not None:
        endereco.logradouro = dados.logradouro

    if dados.numero is not None:
        endereco.numero = dados.numero

    if dados.bairro is not None:
        endereco.bairro = dados.bairro

    if dados.complemento is not None:
        endereco.complemento = dados.complemento

    try:
        db.commit()
        db.refresh(endereco)

    except Exception:
        db.rollback()
        raise ValueError("Não foi possível alterar o endereço")

    return endereco


def recusar_se_tem_consulta_futura(consultas) -> None:
    """Impede excluir a conta com consulta agendada que ainda vai acontecer (409)."""
    agora = agora_local()
    if any(repositories_consulta_ainda_vai_acontecer(consulta, agora) for consulta in consultas):
        raise ErroNegocio(
            "Você tem consultas agendadas. Cancele-as antes de excluir a conta.",
            409,
        )


# Exclui o paciente e os dados relacionados a ele
def excluir_paciente(id_usuario, db: Session):
    """Exclui o paciente, suas consultas e dados ligados, o endereço e o usuário.

    Levanta ValueError se o usuário não for paciente ativo e ErroNegocio 409 se
    houver consulta agendada por vir. Em erro faz rollback.
    """
    try:
        paciente = verificar_paciente_usuario(id_usuario=id_usuario, db=db)

        consultas = repositories_buscar_consultas_por_paciente(id_paciente=paciente.id_paciente, db=db)
        recusar_se_tem_consulta_futura(consultas)

        for consulta in consultas:
            repositories_excluir_dados_consulta(id_consulta= consulta.id_consulta, db=db)

        repositories_excluir_consultas_por_paciente(id_paciente=paciente.id_paciente, db=db)

        repositories_excluir_endereco_por_usuario(id_usuario=id_usuario,  db=db)

        db.delete(paciente)

        usuario = repositories_buscar_usuario_por_id(id_usuario=id_usuario,  db=db)

        if usuario is None:
            raise ValueError("Usuário não encontrado")

        repositories_desvincular_logs_do_usuario(id_usuario=id_usuario, db=db)
        db.delete(usuario)

        db.commit()

    except ValueError:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise

# Inativar o usuário no banco de dados.
def inativar_usuario(id_usuario, db: Session):
    """Marca o usuário como inativo e encerra as sessões abertas; ValueError se ele não existir."""
    try:
        usuario = repositories_buscar_usuario_por_id(id_usuario=id_usuario, db=db)

        if usuario is None:
            raise ValueError("Usuário não encontrado")

        usuario.status = False
        RepositorioAdministracao(db).encerrar_sessoes(usuario.id, agora_utc())

        db.commit()

        return 

    except ValueError:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise


def alterar_senha(id_usuario, senha_atual: str, nova_senha: str, db: Session) -> None:
    """Troca a senha depois de conferir a atual.

    Responde 400 se a senha atual estiver errada ou se a nova for igual à atual.
    A sessão em uso continua valendo.
    """
    credencial = RepositorioCredencial(db).buscar_para_atualizar(id_usuario)
    if credencial is None:
        raise ErroNegocio("Esta conta não tem senha cadastrada.", 400)

    confere, _ = verificar_senha(senha_atual, credencial.senha_hash)
    if not confere:
        db.rollback()
        raise ErroNegocio("A senha atual está incorreta.", 400)
    if senha_atual == nova_senha:
        db.rollback()
        raise ErroNegocio("A nova senha deve ser diferente da atual.", 400)

    credencial.senha_hash = gerar_hash_senha(nova_senha)
    db.commit()
