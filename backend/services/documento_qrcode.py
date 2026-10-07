# Geração do identificador único e do QR-Code de um documento clínico
# (receita ou atestado), no lado do profissional.
#
# RN10: cada documento tem um codigo_verificacao e um QR-Code únicos.
# RN9: só o profissional responsável pela consulta pode gerar o QR-Code.
# RNF17: nada de dado sensível de saúde em log. Este módulo não imprime
# observações, nome de paciente nem o próprio codigo_verificacao.
import base64
import io
import secrets
from datetime import datetime, timezone

import qrcode
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.parametros import base_url_validacao
from models.models import DocumentoClinico, Usuario
from repositories.documento_qrcode import (
    buscar_documento_para_atualizacao,
    buscar_profissional_da_consulta,
)

# secrets.token_urlsafe(24) gera 32 caracteres imprevisíveis. Nunca sequencial.
TAMANHO_CODIGO = 24
MAX_TENTATIVAS = 5


class DocumentoNaoEncontrado(Exception):
    """O documento informado não existe. O router converte em 404."""


class ProfissionalNaoResponsavel(Exception):
    """Quem pediu não é o profissional da consulta. O router converte em 403."""


class FalhaGeracaoCodigo(Exception):
    """Não foi possível obter um código livre. O router converte em 500."""


def montar_url_validacao(codigo_verificacao: str) -> str:
    """URL que o QR-Code carrega. O endpoint que a recebe é de outro módulo."""
    return f"{base_url_validacao().rstrip('/')}/documentos/validar/{codigo_verificacao}"


def _gerar_qrcode_base64(url: str) -> str:
    imagem = qrcode.make(url)
    buffer = io.BytesIO()
    imagem.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def aplicar_qrcode(db: Session, documento: DocumentoClinico) -> bool:
    """Grava codigo_verificacao e qr_code no documento, se ainda não tiver.

    Devolve True se gerou agora e False se já existia. Não faz commit: quem chama
    é dono da transação. Usado tanto pelo endpoint do QR-Code quanto pela emissão
    da receita e do atestado.
    """
    if documento.codigo_verificacao and documento.qr_code:
        return False

    for _ in range(MAX_TENTATIVAS):
        codigo = secrets.token_urlsafe(TAMANHO_CODIGO)
        try:
            # Savepoint: se o código colidir com o de outro documento, desfaz só
            # esta tentativa e mantém a trava da linha para a próxima.
            with db.begin_nested():
                documento.codigo_verificacao = codigo
                documento.qr_code = _gerar_qrcode_base64(montar_url_validacao(codigo))
                if documento.data_emissao is None:
                    documento.data_emissao = datetime.now(timezone.utc)
                db.flush()
        except IntegrityError:
            continue
        return True

    raise FalhaGeracaoCodigo(
        "Não foi possível gerar um identificador único para o documento. Tente novamente."
    )


def gerar_qrcode_documento(
    db: Session,
    id_documento: int,
    usuario: Usuario,
) -> tuple[DocumentoClinico, bool]:
    """Gera (ou devolve) o QR-Code do documento.

    O segundo item da tupla diz se o QR-Code foi criado agora (201) ou se já
    existia (200).
    """
    profissional = usuario.profissional
    if profissional is None:
        raise ProfissionalNaoResponsavel(
            "Somente o profissional responsável pela consulta pode gerar o QR-Code do documento."
        )

    documento = buscar_documento_para_atualizacao(db, id_documento)
    if documento is None:
        raise DocumentoNaoEncontrado("Documento clínico não encontrado.")

    id_profissional_consulta = buscar_profissional_da_consulta(db, documento.id_consulta)
    if id_profissional_consulta != profissional.id_profissional:
        raise ProfissionalNaoResponsavel(
            "Somente o profissional responsável pela consulta pode gerar o QR-Code do documento."
        )

    # Idempotência: se já tiver QR-Code, devolve o que está gravado.
    try:
        criado = aplicar_qrcode(db, documento)
    except FalhaGeracaoCodigo:
        db.rollback()
        raise

    db.commit()  # também libera a trava da linha
    return documento, criado
