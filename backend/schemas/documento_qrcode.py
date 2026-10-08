from pydantic import BaseModel


class QrCodeDocumentoOutput(BaseModel):
    documento_id: int
    codigo_verificacao: str
    url_validacao: str
    qr_code_base64: str
