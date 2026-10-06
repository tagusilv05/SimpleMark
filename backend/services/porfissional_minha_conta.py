# CRIADO: JOAO MARCOS 

from sqlalchemy.orm import Session
from datetime import datetime
from pathlib import Path

from repositories.porfissional_minha_conta import (
    buscar_especialidade_por_id as repositories_buscar_especialidade_por_id,
    criar_conselho as repositories_criar_conselho,
    criar_profissional_especialidade as repositories_criar_profissional_especialidade,
    buscar_especialidades_do_profissional as repositoreis_buscar_especialidades_do_profissional,
    excluir_horarios_por_especialidade as repositoreis_excluir_horarios_por_especialidade,
    excluir_especialidades_por_profissional as repositoreis_excluir_especialidades_por_profissional,
    buscar_profissional_especialidade as repositories_buscar_profissional_especialidade,
    excluir_conselho as repositories_excluir_conselho
)

from repositories.usuario_minha_conta import (
    buscar_usuario_por_id as repositories_buscar_usuario_por_id,
    excluir_endereco_por_usuario as repositories_excluir_endereco_por_usuario
)

# Busca o usuário, verifica se está ativo e retorna o profissional associado
def verificar_profissional_usuario(id_usuario, db: Session):

    usuario = repositories_buscar_usuario_por_id(id_usuario=id_usuario, db=db)

    if usuario is None:
        raise ValueError("Usuário não encontrado")

    if not usuario.status:
        raise ValueError("Usuário está inativo")

    profissional = usuario.profissional

    if profissional is None:
        raise ValueError("Profissional não encontrado")

    return profissional

from pathlib import Path
from datetime import datetime


# Atualiza a imagem do profissional no diretório de uploads
async def atualizar_imagem_profissional(imagem):

    pasta = Path("uploads/profissionais")
    pasta.mkdir(parents=True, exist_ok=True)

    extensao = Path(imagem.filename).suffix

    nome_arquivo = (
        f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        f"{extensao}"
    )

    caminho = pasta / nome_arquivo

    conteudo = await imagem.read()

    with open(caminho, "wb") as arquivo:
        arquivo.write(conteudo)

    return str(caminho)

# Altera as informações do profissional, incluindo imagem e especialidades, e confirma as alterações no banco de dados.
async def altera_info_profissional(dados, imagem, db: Session):

    try:

        profissional = verificar_profissional_usuario(id_usuario=dados.id_usuario, db=db)

        if dados.info_profissional is not None:
            profissional.info_profissional = dados.info_profissional

        if imagem is not None:

            caminho_imagem = await atualizar_imagem_profissional(imagem)

            profissional.path_imagem = caminho_imagem

        if dados.especialidade:

            for item in dados.especialidade:

                especialidade = repositories_buscar_especialidade_por_id(item.id_especialidade, db)

                if especialidade is None:
                    raise ValueError("Especialidade não encontrada")

                conselho = repositories_criar_conselho(
                    numero_conselho=item.numero_conselho,
                    orgao_conselho=item.conselho,
                    db=db
                )

                repositories_criar_profissional_especialidade(
                    id_profissional=profissional.id_profissional,
                    id_especialidade=especialidade.id_especialidade,
                    id_conselho=conselho.id_conselho,
                    valor_consulta=item.valor,
                    db=db
                )

        db.commit()
        db.refresh(profissional)

        return profissional

    except ValueError:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise

# Busca as informações do profissional e suas especialidades vinculadas
def buscar_info_profissional(id_usuario, db: Session):

    profissional = verificar_profissional_usuario(id_usuario=id_usuario, db=db)

    especialidades = repositoreis_buscar_especialidades_do_profissional(profissional.id_profissional, db)

    lista_especialidades = []

    for item in especialidades:

        conselho = item.conselho

        lista_especialidades.append({
            "id_especialidade": item.especialidade.id_especialidade,
            "nome": item.especialidade.especialidade,
            "numero_conselho": (
                conselho.numero_conselho
                if conselho is not None
                else ""
            ),
            "conselho": (
                conselho.orgao_conselho
                if conselho is not None
                else ""
            ),
            "valor": item.valor_consulta
        })

    return {
        "id_profissional": profissional.id_profissional,
        "info_profissional": profissional.info_profissional,
        "especialidade": lista_especialidades
    }

# Altera o valor da consulta de uma especialidade do profissional
def alterar_valor_consulta(dados, db: Session):
    try:

        profissional = verificar_profissional_usuario(id_usuario=dados.id_usuario, db=db)
        print(profissional)
        profissional_especialidade = repositories_buscar_profissional_especialidade(profissional.id_profissional, dados.id_especialidade, db)
        print(profissional_especialidade)
        if profissional_especialidade is None:
            raise ValueError("Porfissional não tem essa Especialiade")

        if dados.valor_consulta < 0:
            raise ValueError("O valor da consulta não pode ser negativo")

        profissional_especialidade.valor_consulta = dados.valor_consulta

        db.commit()
        db.refresh(profissional_especialidade)

        return profissional_especialidade

    except ValueError:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise


# Salva a imagem do profissional e adiciona o caminho no banco
async def salvar_imagem_profissional(id_usuario, imagem, db: Session):
    try:
        profissional = verificar_profissional_usuario(id_usuario=id_usuario, db=db)

        pasta = Path("uploads/profissionais")
        pasta.mkdir(parents=True, exist_ok=True)

        extensao = Path(imagem.filename).suffix

        nome_arquivo = (
            f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
            f"{extensao}"
        )

        caminho = pasta / nome_arquivo

        conteudo = await imagem.read()

        with open(caminho, "wb") as arquivo:
            arquivo.write(conteudo)

        profissional.path_imagem = str(caminho)

        db.commit()
        db.refresh(profissional)

        return str(caminho)

    except ValueError:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise

# Busca o caminho da imagem do profissional
def buscar_imagem_profissional(id_usuario, db: Session):

    profissional = verificar_profissional_usuario(id_usuario=id_usuario, db=db)

    if not profissional.path_imagem:
        raise ValueError("Profissional não possui imagem")

    caminho = Path(profissional.path_imagem)

    if not caminho.exists():
        raise ValueError("Imagem não encontrada")

    return caminho

# Exclui a imagem do profissional 
async def deletar_imagem_profissional(nome_arquivo):

    caminho = Path("uploads/profissionais") / nome_arquivo

    if not caminho.exists():
        return 

    caminho.unlink()

    return 

# Exclui o profissional e todos os dados relacionados a ele
def excluir_profissional(id_usuario, db: Session):
    try:
        
        profissional = verificar_profissional_usuario(id_usuario=id_usuario, db=db)

        path_imagem_profissional = profissional.path_imagem

        if profissional is None:
            raise ValueError("Profissional não encontrado")

        especialidades = repositoreis_buscar_especialidades_do_profissional(id_profissional=profissional.id_profissional, db=db)

        for esp_prof in especialidades:

            repositoreis_excluir_horarios_por_especialidade(id_esp_prof=esp_prof.id_esp_prof, db=db)

            id_conselho = esp_prof.id_conselho

            db.delete(esp_prof)
            db.flush()

            if id_conselho is not None:
                repositories_excluir_conselho(id_conselho=id_conselho, db=db)

        repositoreis_excluir_especialidades_por_profissional(id_profissional=profissional.id_profissional, db=db)

        repositories_excluir_endereco_por_usuario(id_usuario=id_usuario, db=db)

        db.delete(profissional)

        usuario = repositories_buscar_usuario_por_id(id_usuario=id_usuario, db=db)

        if usuario is None:
            raise ValueError("Usuário não encontrado")

        db.delete(usuario)

        db.commit()

        if path_imagem_profissional:
            deletar_imagem_profissional(path_imagem_profissional)

    except ValueError:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise


# Exclui uma especialidade do profissional
def excluir_especialidade_profissional(id_usuario, id_especialidade: int, db: Session):
    try:

        profissional = verificar_profissional_usuario(id_usuario=id_usuario, db=db)

        profissional_especialidade = repositories_buscar_profissional_especialidade(profissional.id_profissional, id_especialidade, db)

        if profissional_especialidade is None:
            raise ValueError("Especialidade não encontrada para este profissional")

        repositoreis_excluir_horarios_por_especialidade(id_esp_prof=profissional_especialidade.id_esp_prof, db=db)

        id_conselho = profissional_especialidade.id_conselho

        db.delete(profissional_especialidade)

        db.flush()

        if id_conselho is not None:
            repositories_excluir_conselho(id_conselho=id_conselho, db=db)

        db.commit()

    except ValueError:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise

