# Validação pública de uma receita ou atestado a partir do código do QR-Code.
#
# Rota aberta de propósito: quem confere o documento é a farmácia, o RH ou o
# próprio paciente, que não têm conta na plataforma. A proteção não vem de login,
# vem do código: secrets.token_urlsafe(24) são 192 bits, inviável de adivinhar.
#
# RNF17: a resposta não devolve observações clínicas nem identifica o paciente,
# e este módulo não registra o código em log.
from sqlalchemy.orm import Session

from core.documento import descrever_tipo
from models.models import DocumentoClinico
from repositories.documento_validacao import buscar_documento_por_codigo
from schemas.documento_validacao import ValidacaoDocumentoOutput


def _descrever_conselho(conselho) -> str | None:
    if conselho is None:
        return None
    return f"{conselho.orgao_conselho} {conselho.numero_conselho}"


def _para_schema(documento: DocumentoClinico) -> ValidacaoDocumentoOutput:
    esp_prof = documento.consulta.profissional_especialidade
    return ValidacaoDocumentoOutput(
        valido=True,
        documento_id=documento.id_documento,
        tipo=descrever_tipo(documento.tipo),
        data_emissao=documento.data_emissao,
        profissional=esp_prof.profissional.usuario.nome,
        especialidade=esp_prof.especialidade.especialidade,
        conselho=_descrever_conselho(esp_prof.conselho),
        data_consulta=documento.consulta.data,
    )


def validar_documento(db: Session, codigo_verificacao: str) -> ValidacaoDocumentoOutput | None:
    """Devolve os dados do documento autêntico, ou None se o código não existir.

    O router converte o None em 404. Código inexistente, expirado ou adulterado
    caem todos no mesmo caso: não existe documento com aquele código.
    """
    documento = buscar_documento_por_codigo(db, codigo_verificacao)
    if documento is None:
        return None
    return _para_schema(documento)
