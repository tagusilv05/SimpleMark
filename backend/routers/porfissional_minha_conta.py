# CRIADO: JOAO MARCOS 

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
    try:
        especialidades = repositories_listar_especialidades(db)
        return especialidades

    except Exception as erro:
        print(f"ERRO REAL: {erro}")
        raise HTTPException(status_code=500, detail="Erro interno ao listar as especialidades")


# Endpoint responsável por excluir uma especialidade do profissional
@router.delete("/excluir-especialidade")
def excluir_especialidade(dados: ExcluirEpecialidadeInput, db: Session = Depends(get_db)):
    try:
        service_excluir_especialidade_profissional(id_usuario=dados.id_usuario, id_especialidade=dados.id_especialidade, db=db)

        return {"mensagem": "Especialidade removida do profissional com sucesso"}

    except ValueError as erro:
        print(f"VALUE ERROR: {erro}")
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as erro:
        print(f"ERRO REAL: {erro}")
        raise HTTPException(status_code=500,detail="Erro ao remover especialidade do profissional")


