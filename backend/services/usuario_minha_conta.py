# CRIADO: JOAO MARCOS 

from sqlalchemy.orm import Session

from repositories.usuario_minha_conta import (
    buscar_usuario_por_id as repositories_buscar_usuario_por_id,
    buscar_endereco_por_usuario as repositories_buscar_endereco_por_usuario,
    buscar_consultas_por_paciente as repositories_buscar_consultas_por_paciente,
    excluir_dados_consulta as repositories_excluir_dados_consulta,
    excluir_consultas_por_paciente as repositories_excluir_consultas_por_paciente,
    excluir_endereco_por_usuario as repositories_excluir_endereco_por_usuario
)

# Busca o usuário, verifica se está ativo e retorna o paciente associado
def verificar_paciente_usuario(id_usuario, db: Session):

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

    usuario = repositories_buscar_usuario_por_id(dados.id, db)

    if not usuario:
        raise ValueError("Usuário não encontrado")

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


# Exclui o paciente e os dados relacionados a ele
def excluir_paciente(id_usuario, db: Session):
    try:
        paciente = verificar_paciente_usuario(id_usuario=id_usuario, db=db)

        consultas = repositories_buscar_consultas_por_paciente(id_paciente=paciente.id_paciente, db=db)

        for consulta in consultas:
            repositories_excluir_dados_consulta(id_consulta= consulta.id_consulta, db=db)

        repositories_excluir_consultas_por_paciente(id_paciente=paciente.id_paciente, db=db)

        repositories_excluir_endereco_por_usuario(id_usuario=id_usuario,  db=db)

        db.delete(paciente)

        usuario = repositories_buscar_usuario_por_id(id_usuario=id_usuario,  db=db)

        if usuario is None:
            raise ValueError("Usuário não encontrado")

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
    try:
        usuario = repositories_buscar_usuario_por_id(id_usuario=id_usuario, db=db)

        if usuario is None:
            raise ValueError("Usuário não encontrado")

        usuario.status = False

        db.commit()

        return 

    except ValueError:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise