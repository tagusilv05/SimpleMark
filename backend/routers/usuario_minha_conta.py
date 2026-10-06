# CRIADO: JOAO MARCOS 

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
import uuid

from dependencies.database import get_db

from services.usuario_minha_conta import (
    altera_info_pessoal as services_altera_info_pessoal,
    altera_endereco as service_altera_endereco,
    excluir_paciente as service_excluir_paciente,
    inativar_usuario as service_inativar_usuario
)

from schemas.usuario_minha_conta import (
    AltereInfoPessoalOutput,
    AltereInfoPessoalInput,
    AltereEnderecoInput,
    AltereEnderecoOutput,
    BuscarInfoEnderecoOutput,
    BuscarInfoUsuarioOutput,
    ExcluirUsuarioInput
)

from services.porfissional_minha_conta import excluir_profissional as service_excluir_profissional

from repositories.usuario_minha_conta import(
    buscar_endereco_por_usuario as repositories_buscar_endereco_por_usuario,
    buscar_usuario_por_id as repositories_buscar_usuario_por_id
)

router = APIRouter()

# Endpoint responsável por altera as informações pessoais do usuário e retorna os dados atualizados.
@router.put("/altera-info-pessoal", response_model=AltereInfoPessoalOutput)
async def altera_info_pessoal(dados: AltereInfoPessoalInput, db: Session = Depends(get_db)):
    try:
        info_usuario = services_altera_info_pessoal(dados=dados, db=db)
        return info_usuario

    except ValueError as erro:
        print(f"VALUE ERROR: {erro}")
        raise HTTPException(status_code=400, detail=str(erro))
    except Exception as erro:
        print(f"ERRO REAL: {erro}")
        raise HTTPException(status_code=500, detail="Erro interno ao alterar as informação do usuario")

# Endpoint responsável por altera o endereço do usuário e retorna os dados atualizados.
@router.put("/altera-endereco", response_model=AltereEnderecoOutput)
async def altera_endereco(dados: AltereEnderecoInput, db: Session = Depends(get_db)):
    try:
        endereco = service_altera_endereco(dados=dados, db=db)
        return endereco

    except ValueError as erro:
        print(f"VALUE ERROR: {erro}")
        raise HTTPException(status_code=400, detail=str(erro))
    except Exception as erro:
        print(f"ERRO REAL: {erro}")
        raise HTTPException(status_code=500, detail="Erro interno ao alterar o endereço do usuario")

# Endpoint responsável por buscar as informações de endereço do usuário
@router.get("/buscar-info-endereco/{id_usuario}", response_model=BuscarInfoEnderecoOutput)
async def buscar_info_endereco(id_usuario: uuid.UUID, db: Session = Depends(get_db)):
    try:
        endereco = repositories_buscar_endereco_por_usuario(id_usuario=id_usuario, db=db)
        return endereco

    except ValueError as erro:
        print(f"VALUE ERROR: {erro}")
        raise HTTPException(status_code=400, detail=str(erro))
    except Exception as erro:
        print(f"ERRO REAL: {erro}")
        raise HTTPException(status_code=500, detail="Erro interno buscar endereco do usuario")

# Endpoint responsável por buscar as informações do usuário
@router.get("/buscar-info-usuario/{id_usuario}", response_model=BuscarInfoUsuarioOutput)
async def buscar_info_usuario(id_usuario: uuid.UUID, db: Session = Depends(get_db)):
    try:
        info_usuario = repositories_buscar_usuario_por_id(id_usuario=id_usuario, db=db)
        return info_usuario

    except ValueError as erro:
        print(f"VALUE ERROR: {erro}")
        raise HTTPException(status_code=400, detail=str(erro))
    
    except Exception as erro:
        print(f"ERRO REAL: {erro}")
        raise HTTPException(status_code=500, detail="Erro interno buscar informação do usuario")

# Endpoint responsável por excluir um usuário de acordo com o seu tipo
@router.delete("/excluir-usuario")
async def deletar_usuario(dados: ExcluirUsuarioInput, db: Session = Depends(get_db)):
    try:
        if dados.tipo == "paciente":
            service_excluir_paciente(id_usuario=dados.id, db=db)

        elif dados.tipo == "profissional":
            service_excluir_profissional(id_usuario=dados.id, db=db)

        return {"mensagem": "Usuário excluído com sucesso"}

    except ValueError as erro:
        print(f"VALUE ERROR: {erro}")
        raise HTTPException(status_code=404, detail=str(erro))

    except Exception as erro:
        print(f"ERRO REAL: {erro}")
        raise HTTPException(status_code=500, detail="Erro interno ao excluir o usuário")

# Endpoint responsável por inativa o usuário alterando seu status para False
@router.patch("/inativar-usuario")
async def inativar_usuario(id_usuario: uuid.UUID, db: Session = Depends(get_db)):
    try:
        service_inativar_usuario(id_usuario=id_usuario, db=db)
        return {"mensagem": "Usuário inativado com sucesso"}
    
    except ValueError as erro:
        print(f"VALUE ERROR: {erro}")
        raise HTTPException(status_code=404, detail=str(erro))

    except Exception as erro:
        print(f"ERRO REAL: {erro}")
        raise HTTPException(status_code=500, detail="Erro interno ao inativar usuário")



