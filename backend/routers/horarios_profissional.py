from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from dependencies.database import get_db
from schemas.horarios_profissional import HorariosEmLoteCreate, HorarioOut, HorariosUpdate
from services import horarios_profissionais
from datetime import date

router = APIRouter(
    prefix="/profissional/horarios",
    tags=["Horarios Profissionais"]
)

@router.get("", response_model=List[HorarioOut])  # <-- CORREcaO: serializa objetos SQLAlchemy
def listar_horarios(
    id_esp_prof: int,
    data: date = Query(..., description="Data no formato YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """
    Lista os horarios de um profissional para uma data especifica.
    
    Args:
        id_esp_prof (int): ID do vinculo entre profissional e especialidade
        data (date): Data para filtrar os horarios no formato YYYY-MM-DD
        db: Sessao do banco de dados
    
    Returns:
        List[HorarioOut]: Lista de horarios encontrados
    """
    horarios = horarios_profissionais.listar_horarios(
        db=db,
        id_esp_prof=id_esp_prof,
        data=data
    )
    return horarios

@router.post("", status_code=status.HTTP_201_CREATED)
def cadastrar_horarios_em_lote(
    payload: HorariosEmLoteCreate,
    db: Session = Depends(get_db)
):
    """
    Cadastra horarios para um profissional.
    
    Args:
        payload (HorariosEmLoteCreate): Dados contendo o ID do vinculo entre profissional e especialidade,
                                         as datas e os horarios a serem cadastrados.
        db: Sessao do banco de dados
    
    Returns:
        dict: Mensagem de sucesso ou erro
    """
    try:
        horarios_profissionais.criar_horarios_em_lote(db=db, dados_lote=payload)
        return {"status": "success", "message": "Horarios salvos com sucesso!"}
    except LookupError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao salvar horarios: {str(e)}"
        )

@router.delete("/{id_horario}", status_code=status.HTTP_200_OK)
def deletar_horario(id_horario: int, db: Session = Depends(get_db)):
    
    """
    Deleta um horario especifico de um profissional.
    
    Args:
        id_horario (int): ID do horario a ser deletado
        db: Sessao do banco de dados
        
    Returns:
        dict: Mensagem de sucesso ou erro
    """
    
    resultado = horarios_profissionais.deletar_horario(db, id_horario)
    if not resultado:
        raise HTTPException(status_code=404, detail="Horario nao encontrado")
    return resultado

@router.put("/{id_horario}", status_code=status.HTTP_200_OK)
def atualizar_horario(id_horario: int, payload: HorariosUpdate, db: Session = Depends(get_db)):
    
    """
    Atualiza um horario especifico de um profissional.
    
    Args:
        id_horario (int): ID do horario a ser atualizado
        payload (HorariosUpdate): Dados para atualizacao do horario
        db: Sessao do banco de dados
    
    Returns:
        dict: Mensagem de sucesso ou erro
    """
    
    
    resultado = horarios_profissionais.atualizar_horario(db, id_horario=id_horario, dados_atualizacao=payload)
    if not resultado:
        raise HTTPException(status_code=404, detail="Horario nao encontrado")
    return resultado