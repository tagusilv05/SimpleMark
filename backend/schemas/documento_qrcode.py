"""Saída da geração do QR-Code de um documento clínico."""

from pydantic import BaseModel


class QrCodeDocumentoOutput(BaseModel):
    """Resposta de POST /documentos/{documento_id}/qrcode: código, link de
    validação e a imagem do QR-Code em base64.
    """

    documento_id: int
    codigo_verificacao: str
    url_validacao: str
    qr_code_base64: str
