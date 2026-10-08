# routers/documento_validacao.py
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from dependencies.database import get_db
from schemas.documento_validacao import ValidacaoDocumentoOutput
from services.documento_validacao import validar_documento

router = APIRouter(prefix="/documentos", tags=["Documentos Clínicos"])


# Endpoint público para onde o QR-Code aponta. Confirma se a receita ou o
# atestado foi mesmo emitido pela plataforma. Não exige autenticação.
@router.get("/validar/{codigo_verificacao}", response_model=ValidacaoDocumentoOutput)
def validar(codigo_verificacao: str, response: Response, db: Session = Depends(get_db)):
    resultado = validar_documento(db=db, codigo_verificacao=codigo_verificacao)

    if resultado is None:
        response.status_code = 404
        return ValidacaoDocumentoOutput(valido=False)

    return resultado
