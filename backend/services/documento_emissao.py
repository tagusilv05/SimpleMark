# Emissão de receitas e atestados pelo profissional.
#
# O documento nasce vinculado à consulta, e é a consulta que diz quem é o
# paciente e quem é o profissional responsável — nenhum dos dois chega por
# parâmetro, para não haver como emitir documento no nome de outra pessoa.
#
# RN9: só o profissional da consulta emite o documento dela.
# RN10: o identificador único e o QR-Code saem prontos na emissão.
# RNF17: este módulo não registra em log medicamento, CID nem observação.
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from core.documento import TIPO_ATESTADO, TIPO_RECEITA, descrever_tipo
from models.models import Atestado, Consulta, DocumentoClinico, Receita, ReceitaMedicamento, Usuario
from repositories.documento_emissao import (
    buscar_consulta,
    buscar_documento,
    listar_documentos_da_consulta,
)
from schemas.documento_emissao import (
    DocumentoEmitidoOutput,
    DocumentoResumoOutput,
    EmitirAtestadoInput,
    EmitirReceitaInput,
    MedicamentoOutput,
    PacienteDocumentoOutput,
)
from services.documento_qrcode import aplicar_qrcode, montar_url_validacao

STATUS_IMPEDE_EMISSAO = {"cancelada"}


class ConsultaNaoEncontrada(Exception):
    """A consulta informada não existe. O router converte em 404."""


class DocumentoNaoEncontrado(Exception):
    """O documento informado não existe. O router converte em 404."""


class ProfissionalNaoResponsavel(Exception):
    """Quem pediu não é o profissional da consulta. O router converte em 403."""


class ConsultaNaoPermiteEmissao(Exception):
    """A consulta está em um estado que não comporta emissão. O router converte em 400."""


def _consulta_do_profissional(db: Session, id_consulta: int, usuario: Usuario) -> Consulta:
    """Carrega a consulta e confirma que ela é de quem está pedindo (RN9)."""
    profissional = usuario.profissional
    if profissional is None:
        raise ProfissionalNaoResponsavel(
            "Somente o profissional responsável pela consulta pode emitir o documento."
        )

    consulta = buscar_consulta(db, id_consulta)
    if consulta is None:
        raise ConsultaNaoEncontrada("Consulta não encontrada.")

    if consulta.profissional_especialidade.id_profissional != profissional.id_profissional:
        raise ProfissionalNaoResponsavel(
            "Somente o profissional responsável pela consulta pode emitir o documento."
        )

    return consulta


def _criar_documento(db: Session, consulta: Consulta, tipo: bool, observacoes: str | None):
    if consulta.status in STATUS_IMPEDE_EMISSAO:
        raise ConsultaNaoPermiteEmissao(
            "Não é possível emitir documentos para uma consulta cancelada."
        )

    documento = DocumentoClinico(
        id_consulta=consulta.id_consulta,
        tipo=tipo,
        observacoes=observacoes.strip() if observacoes else None,
        data_emissao=datetime.now(timezone.utc),
    )
    db.add(documento)
    db.flush()  # precisa do id_documento para as filhas
    return documento


def _descrever_conselho(esp_prof) -> str | None:
    if esp_prof.conselho is None:
        return None
    return f"{esp_prof.conselho.orgao_conselho} {esp_prof.conselho.numero_conselho}"


def _para_schema(documento: DocumentoClinico) -> DocumentoEmitidoOutput:
    consulta = documento.consulta
    esp_prof = consulta.profissional_especialidade
    paciente = consulta.paciente

    saida = DocumentoEmitidoOutput(
        documento_id=documento.id_documento,
        tipo=descrever_tipo(documento.tipo),
        id_consulta=consulta.id_consulta,
        paciente=PacienteDocumentoOutput(
            id_paciente=paciente.id_paciente,
            nome=paciente.usuario.nome,
            cpf=paciente.usuario.cpf,
            data_nascimento=paciente.usuario.data_nascimento,
        ),
        profissional=esp_prof.profissional.usuario.nome,
        especialidade=esp_prof.especialidade.especialidade,
        conselho=_descrever_conselho(esp_prof),
        data_emissao=documento.data_emissao,
        observacoes=documento.observacoes,
        codigo_verificacao=documento.codigo_verificacao,
        url_validacao=montar_url_validacao(documento.codigo_verificacao),
        qr_code_base64=documento.qr_code,
    )

    if documento.receita is not None:
        saida.validade_dias = documento.receita.validade_dias
        saida.medicamentos = [
            MedicamentoOutput(
                medicamento=item.medicamento,
                dosagem=item.dosagem,
                posologia=item.posologia,
                quantidade=item.quantidade,
                duracao_dias=item.duracao_dias,
            )
            for item in documento.receita.medicamentos
        ]

    if documento.atestado is not None:
        saida.dias_afastamento = documento.atestado.dias_afastamento
        saida.data_inicio = documento.atestado.data_inicio
        saida.cid = documento.atestado.cid
        saida.finalidade = documento.atestado.finalidade

    return saida


def emitir_receita(db: Session, dados: EmitirReceitaInput, usuario: Usuario) -> DocumentoEmitidoOutput:
    consulta = _consulta_do_profissional(db, dados.id_consulta, usuario)
    documento = _criar_documento(db, consulta, TIPO_RECEITA, dados.observacoes)

    db.add(Receita(id_documento=documento.id_documento, validade_dias=dados.validade_dias))
    for item in dados.medicamentos:
        db.add(
            ReceitaMedicamento(
                id_documento=documento.id_documento,
                medicamento=item.medicamento,
                dosagem=item.dosagem,
                posologia=item.posologia,
                quantidade=item.quantidade,
                duracao_dias=item.duracao_dias,
            )
        )

    aplicar_qrcode(db, documento)
    db.commit()
    db.refresh(documento)
    return _para_schema(documento)


def emitir_atestado(db: Session, dados: EmitirAtestadoInput, usuario: Usuario) -> DocumentoEmitidoOutput:
    consulta = _consulta_do_profissional(db, dados.id_consulta, usuario)
    documento = _criar_documento(db, consulta, TIPO_ATESTADO, dados.observacoes)

    db.add(
        Atestado(
            id_documento=documento.id_documento,
            dias_afastamento=dados.dias_afastamento,
            data_inicio=dados.data_inicio,
            cid=dados.cid.strip().upper() if dados.cid else None,
            finalidade=dados.finalidade.strip() if dados.finalidade else None,
        )
    )

    aplicar_qrcode(db, documento)
    db.commit()
    db.refresh(documento)
    return _para_schema(documento)


def buscar_documento_emitido(db: Session, id_documento: int, usuario: Usuario) -> DocumentoEmitidoOutput:
    documento = buscar_documento(db, id_documento)
    if documento is None:
        raise DocumentoNaoEncontrado("Documento clínico não encontrado.")

    # Reaproveita a checagem da RN9 sobre a consulta do documento.
    _consulta_do_profissional(db, documento.id_consulta, usuario)
    return _para_schema(documento)


def listar_documentos(db: Session, id_consulta: int, usuario: Usuario) -> list[DocumentoResumoOutput]:
    _consulta_do_profissional(db, id_consulta, usuario)
    return [
        DocumentoResumoOutput(
            documento_id=documento.id_documento,
            tipo=descrever_tipo(documento.tipo),
            data_emissao=documento.data_emissao,
            codigo_verificacao=documento.codigo_verificacao,
        )
        for documento in listar_documentos_da_consulta(db, id_consulta)
    ]
