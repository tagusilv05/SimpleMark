from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator


class MedicamentoInput(BaseModel):
    medicamento: str = Field(min_length=1, max_length=200)
    dosagem: str = Field(min_length=1, max_length=100)
    posologia: str = Field(min_length=1, max_length=300)
    quantidade: str = Field(min_length=1, max_length=50)
    duracao_dias: int | None = Field(default=None, gt=0, le=365)

    @field_validator("medicamento", "dosagem", "posologia", "quantidade")
    @classmethod
    def sem_espaco_sobrando(cls, valor: str) -> str:
        texto = valor.strip()
        if not texto:
            raise ValueError("Preencha todos os campos do medicamento.")
        return texto


class EmitirReceitaInput(BaseModel):
    id_consulta: int
    medicamentos: list[MedicamentoInput] = Field(min_length=1)
    validade_dias: int = Field(default=30, gt=0, le=365)
    observacoes: str | None = None


class EmitirAtestadoInput(BaseModel):
    id_consulta: int
    dias_afastamento: int = Field(gt=0, le=365)
    data_inicio: date
    cid: str | None = Field(default=None, max_length=10)
    finalidade: str | None = Field(default=None, max_length=200)
    observacoes: str | None = None


class MedicamentoOutput(BaseModel):
    medicamento: str
    dosagem: str
    posologia: str
    quantidade: str
    duracao_dias: int | None = None


class PacienteDocumentoOutput(BaseModel):
    id_paciente: int
    nome: str
    cpf: str
    data_nascimento: date


class DocumentoEmitidoOutput(BaseModel):
    """Documento recém-emitido, já com o QR-Code pronto para impressão."""

    documento_id: int
    tipo: str
    id_consulta: int
    paciente: PacienteDocumentoOutput
    profissional: str
    especialidade: str
    conselho: str | None = None
    data_emissao: datetime
    observacoes: str | None = None

    # presentes só na receita
    validade_dias: int | None = None
    medicamentos: list[MedicamentoOutput] | None = None

    # presentes só no atestado
    dias_afastamento: int | None = None
    data_inicio: date | None = None
    cid: str | None = None
    finalidade: str | None = None

    codigo_verificacao: str
    url_validacao: str
    qr_code_base64: str


class DocumentoResumoOutput(BaseModel):
    """Item da listagem dos documentos de uma consulta."""

    documento_id: int
    tipo: str
    data_emissao: datetime | None = None
    codigo_verificacao: str | None = None
