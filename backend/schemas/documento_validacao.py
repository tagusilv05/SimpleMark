from datetime import date, datetime

from pydantic import BaseModel


class ValidacaoDocumentoOutput(BaseModel):
    """Resposta da validação pública.

    Só carrega o que comprova a autenticidade do documento. Nada de observações
    clínicas nem de identificação do paciente (RNF17).
    """

    valido: bool
    documento_id: int | None = None
    tipo: str | None = None
    data_emissao: datetime | None = None
    profissional: str | None = None
    especialidade: str | None = None
    conselho: str | None = None
    data_consulta: date | None = None
