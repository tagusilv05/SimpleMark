# routers/documento_qrcode.py
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from dependencies.autenticacao import UsuarioAtual
from dependencies.database import get_db
from schemas.documento_qrcode import QrCodeDocumentoOutput
from services.documento_qrcode import (
    DocumentoNaoEncontrado,
    FalhaGeracaoCodigo,
    ProfissionalNaoResponsavel,
    gerar_qrcode_documento,
    montar_url_validacao,
)

router = APIRouter(prefix="/documentos", tags=["Documentos Clínicos"])


# Endpoint responsável por gerar o identificador único e o QR-Code de uma
# receita ou atestado. Responde 201 quando gera agora e 200 quando já existia.
@router.post("/{documento_id}/qrcode", response_model=QrCodeDocumentoOutput, status_code=201)
def gerar_qrcode(
    documento_id: int,
    usuario: UsuarioAtual,
    response: Response,
    db: Session = Depends(get_db),
):
    try:
        documento, criado = gerar_qrcode_documento(
            db=db, id_documento=documento_id, usuario=usuario
        )

    except DocumentoNaoEncontrado as erro:
        raise HTTPException(status_code=404, detail=str(erro))

    except ProfissionalNaoResponsavel as erro:
        raise HTTPException(status_code=403, detail=str(erro))

    except FalhaGeracaoCodigo as erro:
        raise HTTPException(status_code=500, detail=str(erro))

    if not criado:
        response.status_code = 200

    return QrCodeDocumentoOutput(
        documento_id=documento.id_documento,
        codigo_verificacao=documento.codigo_verificacao,
        url_validacao=montar_url_validacao(documento.codigo_verificacao),
        qr_code_base64=documento.qr_code,
    )
