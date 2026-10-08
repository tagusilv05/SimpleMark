# routers/documento_emissao.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies.autenticacao import UsuarioAtual
from dependencies.database import get_db
from schemas.documento_emissao import (
    DocumentoEmitidoOutput,
    DocumentoResumoOutput,
    EmitirAtestadoInput,
    EmitirReceitaInput,
)
from services.documento_emissao import (
    ConsultaNaoEncontrada,
    ConsultaNaoPermiteEmissao,
    DocumentoNaoEncontrado,
    ProfissionalNaoResponsavel,
    buscar_documento_emitido,
    emitir_atestado,
    emitir_receita,
    listar_documentos,
)
from services.documento_qrcode import FalhaGeracaoCodigo

router = APIRouter(tags=["Documentos Clínicos"])


def _tratar(acao):
    """Converte os erros do service nos status da API."""
    try:
        return acao()

    except (ConsultaNaoEncontrada, DocumentoNaoEncontrado) as erro:
        raise HTTPException(status_code=404, detail=str(erro))

    except ProfissionalNaoResponsavel as erro:
        raise HTTPException(status_code=403, detail=str(erro))

    except ConsultaNaoPermiteEmissao as erro:
        raise HTTPException(status_code=400, detail=str(erro))

    except FalhaGeracaoCodigo as erro:
        raise HTTPException(status_code=500, detail=str(erro))


# Endpoint responsável por emitir uma receita médica vinculada a uma consulta.
# O paciente vem da consulta, não do corpo da requisição.
@router.post("/receitas", response_model=DocumentoEmitidoOutput, status_code=201)
def emitir_receita_medica(
    dados: EmitirReceitaInput,
    usuario: UsuarioAtual,
    db: Session = Depends(get_db),
):
    return _tratar(lambda: emitir_receita(db=db, dados=dados, usuario=usuario))


# Endpoint responsável por emitir um atestado médico vinculado a uma consulta.
@router.post("/atestados", response_model=DocumentoEmitidoOutput, status_code=201)
def emitir_atestado_medico(
    dados: EmitirAtestadoInput,
    usuario: UsuarioAtual,
    db: Session = Depends(get_db),
):
    return _tratar(lambda: emitir_atestado(db=db, dados=dados, usuario=usuario))


# Endpoint responsável por listar os documentos clínicos emitidos numa consulta.
@router.get("/consultas/{id_consulta}/documentos", response_model=list[DocumentoResumoOutput])
def documentos_da_consulta(
    id_consulta: int,
    usuario: UsuarioAtual,
    db: Session = Depends(get_db),
):
    return _tratar(lambda: listar_documentos(db=db, id_consulta=id_consulta, usuario=usuario))


# Endpoint responsável por retornar um documento clínico já emitido, por inteiro.
@router.get("/documentos/{documento_id}", response_model=DocumentoEmitidoOutput)
def documento_emitido(
    documento_id: int,
    usuario: UsuarioAtual,
    db: Session = Depends(get_db),
):
    return _tratar(lambda: buscar_documento_emitido(db=db, id_documento=documento_id, usuario=usuario))
