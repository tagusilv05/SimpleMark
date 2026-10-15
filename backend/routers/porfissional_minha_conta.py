# CRIADO: JOAO MARCOS 
"""Rotas da conta do profissional: informações, imagem, especialidades e valor."""

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
import json
import uuid

from dependencies.database import get_db

from services.porfissional_minha_conta import (
    altera_info_profissional as service_altera_info_profissional,
    buscar_info_profissional as service_buscar_info_profissional,
    alterar_valor_consulta as service_alterar_valor_consulta,
    salvar_imagem_profissional as service_salvar_imagem_profissional,
    buscar_imagem_profissional as service_buscar_imagem_profissional,
    excluir_especialidade_profissional as service_excluir_especialidade_profissional
)

from repositories.porfissional_minha_conta import listar_especialidades as repositories_listar_especialidades

from schemas.porfissional_minha_conta import (
    AdicionaInfoProfissionalInput,
    BuscarInfoProfissionalOutput,
    AlterarValorConsultaInput,
    AlterarValorConsultaOutput,
    ExcluirEpecialidadeInput,
    BuscarEspecialidadeOutput
)

router = APIRouter()

# Endpoint responsável por receber e alterar as informações e a imagem do profissional
@router.put("/alterar-info-profissional")
async def alterar_info_profissional(dados: str | None = Form(None), imagem: UploadFile | None = File(None), db: Session = Depends(get_db)):
    """Altera a descrição, a imagem e as especialidades do profissional.

    Recebe multipart: `dados` (JSON em texto, com o id_usuario) e a `imagem`
    opcional. Cada especialidade enviada é vinculada com conselho e valor. Rota sem
    autenticação. Responde 400 se o usuário não for profissional ativo, se o JSON
    for inválido ou se a especialidade não existir; outros erros, 500.
    """
    try:
        dados_obj = None

        if dados is not None: 
            dados_obj = AdicionaInfoProfissionalInput(**json.loads(dados))

        await service_altera_info_profissional(dados=dados_obj, imagem=imagem, db=db)

        return {"mensagem": "Informações do profissional alteradas com sucesso"}

    except ValueError as erro:
        print(f"VALUE ERROR: {erro}")
        raise HTTPException(status_code=400, detail=str(erro))

    except Exception as erro:
        print(f"ERRO REAL: {erro}")
        raise HTTPException(status_code=500, detail="Erro interno ao alterar as informações")


# Endpoint responsável por retornar as informações de um profissional relacionado a especialidade
@router.get("/buscar-info-profissional/{id_usuario}", response_model=BuscarInfoProfissionalOutput)
async def buscar_info_profissional(id_usuario: uuid.UUID, db: Session = Depends(get_db)):
    """Devolve a descrição do profissional e suas especialidades, conselho e valor.

    Rota sem autenticação. Responde 404 se o usuário não for profissional ativo.
    """
    try:
        resultado = service_buscar_info_profissional(id_usuario=id_usuario, db=db)
        return resultado

    except ValueError as erro:
        print(f"VALUE ERROR: {erro}")
        raise HTTPException(status_code=404, detail=str(erro))

    except Exception as erro:
        print(f"ERRO REAL: {erro}")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar as informações")


# Endpoint responsável por alterar o valor da consulta do profissional
@router.put("/alterar-valor-consulta", response_model=AlterarValorConsultaOutput)
async def alterar_valor_consulta(dados:AlterarValorConsultaInput, db: Session = Depends(get_db)):
    """Altera o valor da consulta do profissional numa especialidade.

    Rota sem autenticação. Responde 404 se o usuário não for profissional ativo, se
    não tiver a especialidade ou se o valor for negativo.
    """
    try:
        resultado = service_alterar_valor_consulta(dados=dados, db=db)
        return resultado

    except ValueError as erro:
        print(f"VALUE ERROR: {erro}")
        raise HTTPException(status_code=404, detail=str(erro))

    except Exception as erro:
        print(f"ERRO REAL: {erro}")
        raise HTTPException(status_code=500, detail="Erro interno ao alterar valor da consulta")


# Endpoint responsável por salvar a imagem do profissional
@router.post("/salvar-imagem-profissional")
async def salvar_imagem_profissional(id_usuario: uuid.UUID = Form(...), imagem: UploadFile = File(...), db: Session = Depends(get_db)):
    """Salva a imagem do profissional em uploads/profissionais e grava o caminho.

    Rota sem autenticação. Responde 404 se o usuário não for profissional ativo.
    """
    try:
        await service_salvar_imagem_profissional(id_usuario=id_usuario, imagem=imagem, db=db)

        return {"mensagem": "Imagem enviada com sucesso"}

    except ValueError as erro:
        print(f"VALUE ERROR: {erro}")
        raise HTTPException(status_code=404, detail=str(erro))

    except Exception as erro:
        print(f"ERRO REAL: {erro}")
        raise HTTPException(status_code=500, detail="Erro interno ao salvar a imagem")


# Endpoint responsável por buscar e retornar a imagem do profissional
@router.get("/buscar-imagem-profissional/{id_usuario}")
async def buscar_imagem_profissional(id_usuario: uuid.UUID, db: Session = Depends(get_db)):
    """Devolve o arquivo da imagem do profissional.

    Rota sem autenticação. Responde 404 se o usuário não for profissional ativo, se
    não tiver imagem ou se o arquivo não existir.
    """
    try:
        caminho = service_buscar_imagem_profissional(id_usuario=id_usuario, db=db)

        return FileResponse(
            path=caminho,
            filename=caminho.name
        )

    except ValueError as erro:
        print(f"VALUE ERROR: {erro}")
        raise HTTPException(status_code=404, detail=str(erro))

    except Exception as erro:
        print(f"ERRO REAL: {erro}")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar a imagem")


# Endpoint responsável por listar todas as especialidades cadastradas
@router.get("/lista-especialidade", response_model=list[BuscarEspecialidadeOutput])
async def lista_especialidade(db: Session = Depends(get_db)):
    """Lista todas as especialidades cadastradas. Rota pública."""
    try:
        especialidades = repositories_listar_especialidades(db)
        return especialidades

    except Exception as erro:
        print(f"ERRO REAL: {erro}")
        raise HTTPException(status_code=500, detail="Erro interno ao listar as especialidades")


# Endpoint responsável por excluir uma especialidade do profissional
@router.delete("/excluir-especialidade")
def excluir_especialidade(dados: ExcluirEpecialidadeInput, db: Session = Depends(get_db)):
    """Remove a especialidade do profissional, com os horários e o conselho dela.

    Rota sem autenticação. Responde 404 se o usuário não for profissional ativo ou
    não tiver a especialidade.
    """
    try:
        service_excluir_especialidade_profissional(id_usuario=dados.id_usuario, id_especialidade=dados.id_especialidade, db=db)

        return {"mensagem": "Especialidade removida do profissional com sucesso"}

    except ValueError as erro:
        print(f"VALUE ERROR: {erro}")
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as erro:
        print(f"ERRO REAL: {erro}")
        raise HTTPException(status_code=500,detail="Erro ao remover especialidade do profissional")


