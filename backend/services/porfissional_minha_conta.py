"""Tela "Minha conta" do profissional: dados, especialidades, imagem e exclusão."""

# CRIADO: JOAO MARCOS 

import uuid
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from core.excecoes import ErroNegocio
from core.tempo import agora_local
from models.models import Consulta, Profissional

from repositories.porfissional_minha_conta import (
    buscar_especialidade_por_id as repositories_buscar_especialidade_por_id,
    criar_conselho as repositories_criar_conselho,
    criar_profissional_especialidade as repositories_criar_profissional_especialidade,
    buscar_especialidades_do_profissional as repositoreis_buscar_especialidades_do_profissional,
    excluir_horarios_por_especialidade as repositoreis_excluir_horarios_por_especialidade,
    excluir_especialidades_por_profissional as repositoreis_excluir_especialidades_por_profissional,
    buscar_profissional_especialidade as repositories_buscar_profissional_especialidade,
    excluir_conselho as repositories_excluir_conselho,
    conselho_em_uso as repositories_conselho_em_uso,
)

from repositories.usuario_minha_conta import (
    buscar_usuario_por_id as repositories_buscar_usuario_por_id,
    excluir_endereco_por_usuario as repositories_excluir_endereco_por_usuario,
    excluir_dados_consulta as repositories_excluir_dados_consulta,
    consulta_ainda_vai_acontecer as repositories_consulta_ainda_vai_acontecer,
    desvincular_logs_do_usuario as repositories_desvincular_logs_do_usuario,
)

# Imagens enviadas pelos profissionais
PASTA_IMAGENS = Path("uploads/profissionais")
EXTENSOES_IMAGEM = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
TAMANHO_MAX_IMAGEM = 5 * 1024 * 1024  # 5 MB


def _extensao_imagem(nome_arquivo: str | None) -> str:
    """Extensão da imagem enviada; recusa (400) o que não for imagem."""
    extensao = Path(nome_arquivo or "").suffix.lower()
    if extensao not in EXTENSOES_IMAGEM:
        raise ErroNegocio("Envie uma imagem JPG, PNG, WEBP ou GIF.", 400)
    return extensao


def _excluir_conselho_se_livre(id_conselho, db: Session, exceto_id_esp_prof=None) -> None:
    """Apaga o conselho só se nenhum outro vínculo o usar (sem commit)."""
    if id_conselho is not None and not repositories_conselho_em_uso(id_conselho, db, exceto_id_esp_prof):
        repositories_excluir_conselho(id_conselho=id_conselho, db=db)


def _consultas_do_vinculo(id_esp_prof, db: Session):
    """Consultas marcadas num vínculo profissional-especialidade."""
    return db.query(Consulta).filter(Consulta.id_esp_prof == id_esp_prof).all()

# Busca o usuário, verifica se está ativo e retorna o profissional associado
def verificar_profissional_usuario(id_usuario, db: Session):
    """Profissional ligado ao usuário ou ao id_profissional.

    Aceita UUID (ou string de UUID) do usuário, ou ID inteiro (ou string numérica) do profissional.
    """
    is_numeric = False
    if isinstance(id_usuario, int):
        is_numeric = True
    elif isinstance(id_usuario, str) and id_usuario.isdigit():
        is_numeric = True

    if is_numeric:
        profissional = db.query(Profissional).filter(Profissional.id_profissional == int(id_usuario)).first()
        if profissional is None:
            raise ValueError("Profissional não encontrado")
        usuario = profissional.usuario
    else:
        identificador = id_usuario
        try:
            if isinstance(identificador, str):
                identificador = uuid.UUID(identificador)
        except Exception:
            raise ValueError("Identificador inválido")

        usuario = repositories_buscar_usuario_por_id(id_usuario=identificador, db=db)
        if usuario is None:
            raise ValueError("Usuário não encontrado")
        profissional = usuario.profissional

    if usuario is None or not usuario.status:
        raise ValueError("Usuário está inativo")

    if profissional is None:
        raise ValueError("Profissional não encontrado")

    return profissional

# Atualiza a imagem do profissional no diretório de uploads
async def atualizar_imagem_profissional(imagem):
    """Salva a imagem enviada em uploads/profissionais e devolve o caminho."""

    extensao = _extensao_imagem(imagem.filename)
    conteudo = await imagem.read()
    if len(conteudo) > TAMANHO_MAX_IMAGEM:
        raise ErroNegocio("A imagem deve ter no máximo 5 MB.", 400)

    PASTA_IMAGENS.mkdir(parents=True, exist_ok=True)
    caminho = PASTA_IMAGENS / f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}{extensao}"

    with open(caminho, "wb") as arquivo:
        arquivo.write(conteudo)

    return str(caminho)

# Altera as informações do profissional, incluindo imagem e especialidades, e confirma as alterações no banco de dados.
async def altera_info_profissional(dados, imagem, db: Session):
    """Atualiza a descrição, a imagem e adiciona especialidades ao profissional.

    Cada especialidade nova cria um conselho e um vínculo com o valor da consulta.
    Levanta ValueError se uma especialidade não existir. Em erro faz rollback.
    """

    try:

        profissional = verificar_profissional_usuario(id_usuario=dados.id_usuario, db=db)

        if dados.info_profissional is not None:
            profissional.info_profissional = dados.info_profissional

        if imagem is not None and getattr(imagem, "filename", None):

            caminho_imagem = await atualizar_imagem_profissional(imagem)

            profissional.path_imagem = caminho_imagem

        if dados.especialidade:

            for item in dados.especialidade:

                especialidade = repositories_buscar_especialidade_por_id(item.id_especialidade, db)

                if especialidade is None:
                    raise ValueError("Especialidade não encontrada")

                if item.valor < 0:
                    raise ValueError("O valor da consulta não pode ser negativo")

                vinculo = repositories_buscar_profissional_especialidade(
                    profissional.id_profissional, especialidade.id_especialidade, db
                )

                if vinculo is None:
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
                    continue

                # Especialidade que o profissional já tem: atualiza em vez de duplicar
                vinculo.valor_consulta = item.valor
                atual = vinculo.conselho
                mudou_conselho = atual is None or (
                    atual.numero_conselho != item.numero_conselho or atual.orgao_conselho != item.conselho
                )
                if mudou_conselho:
                    # O conselho pode ser compartilhado com outras especialidades: cria um próprio
                    id_antigo = vinculo.id_conselho
                    novo = repositories_criar_conselho(
                        numero_conselho=item.numero_conselho,
                        orgao_conselho=item.conselho,
                        db=db
                    )
                    vinculo.id_conselho = novo.id_conselho
                    db.flush()
                    _excluir_conselho_se_livre(id_antigo, db)

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
    """Descrição do profissional e suas especialidades com conselho e valor."""

    profissional = verificar_profissional_usuario(id_usuario=id_usuario, db=db)

    especialidades = repositoreis_buscar_especialidades_do_profissional(profissional.id_profissional, db)

    lista_especialidades = []

    for item in especialidades:

        conselho = item.conselho

        lista_especialidades.append({
            "id_esp_prof": item.id_esp_prof,
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
        "id_usuario": profissional.id_usuario,
        "nome": profissional.usuario.nome if (profissional.usuario and profissional.usuario.nome) else "",
        "path_imagem": profissional.path_imagem,
        "info_profissional": profissional.info_profissional,
        "especialidade": lista_especialidades
    }

# Altera o valor da consulta de uma especialidade do profissional
def alterar_valor_consulta(dados, db: Session):
    """Altera o valor da consulta do profissional em uma especialidade.

    Levanta ValueError se o vínculo não existir ou se o valor for negativo.
    """
    try:

        profissional = verificar_profissional_usuario(id_usuario=dados.id_usuario, db=db)
        profissional_especialidade = repositories_buscar_profissional_especialidade(profissional.id_profissional, dados.id_especialidade, db)
        if profissional_especialidade is None:
            raise ValueError("O profissional não tem essa especialidade")

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
    """Salva a imagem enviada e grava o caminho no profissional.

    Devolve o caminho do arquivo. Em erro faz rollback e relança.
    """
    try:
        profissional = verificar_profissional_usuario(id_usuario=id_usuario, db=db)
        imagem_antiga = profissional.path_imagem

        caminho = Path(await atualizar_imagem_profissional(imagem))

        profissional.path_imagem = str(caminho)

        db.commit()
        db.refresh(profissional)

        if imagem_antiga and imagem_antiga != str(caminho):
            deletar_imagem_profissional(imagem_antiga)

        return str(caminho)

    except ValueError:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise

# Busca o caminho da imagem do profissional
def buscar_imagem_profissional(id_usuario, db: Session):
    """Caminho da imagem do profissional; ValueError se não houver arquivo."""

    profissional = verificar_profissional_usuario(id_usuario=id_usuario, db=db)

    if not profissional.path_imagem:
        raise ValueError("Profissional não possui imagem")

    caminho = Path(profissional.path_imagem)

    if not caminho.exists():
        raise ValueError("Imagem não encontrada")

    return caminho

# Exclui a imagem do profissional
def deletar_imagem_profissional(path_imagem):
    """Apaga o arquivo da imagem (caminho gravado em path_imagem), se existir.

    Só apaga arquivos dentro de uploads/profissionais.
    """
    caminho = Path(path_imagem)
    if caminho.parent.resolve() != PASTA_IMAGENS.resolve():
        caminho = PASTA_IMAGENS / caminho.name
    try:
        caminho.unlink(missing_ok=True)
    except OSError:
        pass

    return 

# Exclui o profissional e todos os dados relacionados a ele
def excluir_profissional(id_usuario, db: Session):
    """Exclui o profissional com vínculos, horários, conselhos, endereço e usuário.

    Levanta ValueError se o usuário não for profissional ativo. Em erro faz
    rollback e relança.
    """
    try:
        
        profissional = verificar_profissional_usuario(id_usuario=id_usuario, db=db)

        path_imagem_profissional = profissional.path_imagem

        especialidades = repositoreis_buscar_especialidades_do_profissional(id_profissional=profissional.id_profissional, db=db)

        consultas = [c for esp_prof in especialidades for c in _consultas_do_vinculo(esp_prof.id_esp_prof, db)]
        agora = agora_local()
        if any(repositories_consulta_ainda_vai_acontecer(c, agora) for c in consultas):
            raise ErroNegocio(
                "Você tem consultas agendadas. Cancele-as antes de excluir a conta.",
                409,
            )

        for consulta in consultas:
            repositories_excluir_dados_consulta(id_consulta=consulta.id_consulta, db=db)
            db.delete(consulta)
        db.flush()

        ids_conselhos = {esp_prof.id_conselho for esp_prof in especialidades if esp_prof.id_conselho is not None}

        for esp_prof in especialidades:
            repositoreis_excluir_horarios_por_especialidade(id_esp_prof=esp_prof.id_esp_prof, db=db)
            db.delete(esp_prof)
        db.flush()

        for id_conselho in ids_conselhos:
            _excluir_conselho_se_livre(id_conselho, db)

        repositoreis_excluir_especialidades_por_profissional(id_profissional=profissional.id_profissional, db=db)

        repositories_excluir_endereco_por_usuario(id_usuario=id_usuario, db=db)

        db.delete(profissional)

        usuario = repositories_buscar_usuario_por_id(id_usuario=id_usuario, db=db)

        if usuario is None:
            raise ValueError("Usuário não encontrado")

        repositories_desvincular_logs_do_usuario(id_usuario=usuario.id, db=db)
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
    """Remove uma especialidade do profissional com seus horários e conselho.

    Levanta ValueError se a especialidade não for do profissional.
    """
    try:

        profissional = verificar_profissional_usuario(id_usuario=id_usuario, db=db)

        profissional_especialidade = repositories_buscar_profissional_especialidade(profissional.id_profissional, id_especialidade, db)

        if profissional_especialidade is None:
            raise ValueError("Especialidade não encontrada para este profissional")

        if _consultas_do_vinculo(profissional_especialidade.id_esp_prof, db):
            # As consultas (e o histórico do paciente) dependem do vínculo
            raise ErroNegocio(
                "Esta especialidade já tem consultas marcadas e não pode ser removida.",
                409,
            )

        repositoreis_excluir_horarios_por_especialidade(id_esp_prof=profissional_especialidade.id_esp_prof, db=db)

        id_conselho = profissional_especialidade.id_conselho

        db.delete(profissional_especialidade)

        db.flush()

        _excluir_conselho_se_livre(id_conselho, db)

        db.commit()

    except ValueError:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise

