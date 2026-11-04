"""Abertura de manifestação na Ouvidoria (com anexos opcionais).

As regras espelham as da tela (OuvidoriaView.vue): assunto de 5 a 100
caracteres, descrição de 20 a 1500, até 5 anexos PDF/PNG/JPEG de até 10 MB e
aceite obrigatório do termo da LGPD. O tipo do anexo é conferido pelo conteúdo
do arquivo, não só pela extensão.
"""

import os
import re
import secrets
import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.excecoes import ErroNegocio
from core.tempo import agora_utc
from models.models import Usuario
from models.ouvidoria import AnexoOuvidoria, ManifestacaoOuvidoria

SOLICITANTES = {"paciente", "profissional"}
TIPOS = {"reclamacao", "teleconsulta", "sugestao", "elogio", "duvida"}

ASSUNTO_MIN, ASSUNTO_MAX = 5, 100
DESCRICAO_MIN, DESCRICAO_MAX = 20, 1500
CODIGO_MAX = 20
ANEXOS_MAX = 5
ANEXO_TAMANHO_MAX = 10 * 1024 * 1024  # 10 MB

# extensão -> (content-type, assinatura do início do arquivo)
FORMATOS = {
    "pdf": ("application/pdf", b"%PDF-"),
    "png": ("image/png", b"\x89PNG\r\n\x1a\n"),
    "jpg": ("image/jpeg", b"\xff\xd8\xff"),
    "jpeg": ("image/jpeg", b"\xff\xd8\xff"),
}

_CODIGO_VALIDO = re.compile(r"^[A-Z0-9-]+$")
_ALFABETO_PROTOCOLO = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # sem 0/O e 1/I


def pasta_uploads() -> Path:
    """Pasta onde os anexos são gravados (OUVIDORIA_PASTA_UPLOADS, padrão uploads/ouvidoria)."""
    return Path(os.getenv("OUVIDORIA_PASTA_UPLOADS", "uploads/ouvidoria"))


@dataclass(frozen=True)
class AnexoRecebido:
    """Arquivo já lido da requisição."""

    nome: str
    conteudo: bytes


@dataclass(frozen=True)
class NovaManifestacao:
    """Dados do formulário da Ouvidoria, ainda sem validar."""

    solicitante: str
    tipo: str
    assunto: str
    descricao: str
    aceite_lgpd: bool
    codigo_consulta: str | None = None


class ServicoOuvidoria:
    """Valida e grava manifestações da Ouvidoria."""

    def __init__(self, db: Session) -> None:
        """Guarda a sessão do banco."""
        self.db = db

    def abrir(
        self,
        dados: NovaManifestacao,
        anexos: list[AnexoRecebido],
        usuario: Usuario | None = None,
    ) -> ManifestacaoOuvidoria:
        """Valida os dados, grava a manifestação e os anexos e devolve o registro.

        Responde 422 com dados inválidos. Se o banco falhar, apaga os arquivos já gravados.
        """
        limpos = self._validar(dados)
        formatos = [self._validar_anexo(anexo) for anexo in self._validar_lista_anexos(anexos)]

        manifestacao = ManifestacaoOuvidoria(
            id=uuid.uuid4(),
            protocolo=self._gerar_protocolo(),
            solicitante=limpos.solicitante,
            tipo=limpos.tipo,
            codigo_consulta=limpos.codigo_consulta,
            assunto=limpos.assunto,
            descricao=limpos.descricao,
            aceite_lgpd=True,
            status="aberta",
            id_usuario=usuario.id if usuario is not None else None,
            criada_em=agora_utc(),
        )

        pasta = pasta_uploads() / str(manifestacao.id)
        try:
            if anexos:
                pasta.mkdir(parents=True, exist_ok=True)
            for anexo, (extensao, tipo_conteudo) in zip(anexos, formatos):
                caminho = pasta / f"{uuid.uuid4().hex}.{extensao}"
                caminho.write_bytes(anexo.conteudo)
                manifestacao.anexos.append(
                    AnexoOuvidoria(
                        nome_original=Path(anexo.nome).name[:255],
                        caminho=str(caminho),
                        tipo_conteudo=tipo_conteudo,
                        tamanho_bytes=len(anexo.conteudo),
                    )
                )
            self.db.add(manifestacao)
            self.db.commit()
        except Exception:
            self.db.rollback()
            shutil.rmtree(pasta, ignore_errors=True)
            raise
        self.db.refresh(manifestacao)
        return manifestacao

    # ---------- validação ----------

    def _validar(self, dados: NovaManifestacao) -> NovaManifestacao:
        """Normaliza os campos e levanta ErroNegocio 422 na primeira regra quebrada."""
        solicitante = (dados.solicitante or "").strip().lower()
        if solicitante not in SOLICITANTES:
            raise ErroNegocio("Informe se você é paciente ou profissional de saúde.", 422)

        tipo = (dados.tipo or "").strip().lower()
        if tipo not in TIPOS:
            raise ErroNegocio("Escolha um tipo de manifestação válido.", 422)

        codigo = (dados.codigo_consulta or "").strip().upper() or None
        if codigo is not None and (len(codigo) > CODIGO_MAX or not _CODIGO_VALIDO.match(codigo)):
            raise ErroNegocio(
                f"O código da consulta aceita só letras, números e hífen (até {CODIGO_MAX}).", 422
            )

        assunto = re.sub(r"\s+", " ", dados.assunto or "").strip()
        if not ASSUNTO_MIN <= len(assunto) <= ASSUNTO_MAX:
            raise ErroNegocio(
                f"O assunto deve ter entre {ASSUNTO_MIN} e {ASSUNTO_MAX} caracteres.", 422
            )

        descricao = (dados.descricao or "").strip()
        if not DESCRICAO_MIN <= len(descricao) <= DESCRICAO_MAX:
            raise ErroNegocio(
                f"A descrição deve ter entre {DESCRICAO_MIN} e {DESCRICAO_MAX} caracteres.", 422
            )

        if not dados.aceite_lgpd:
            raise ErroNegocio("É necessário aceitar o termo para enviar a manifestação.", 422)

        return NovaManifestacao(
            solicitante=solicitante,
            tipo=tipo,
            assunto=assunto,
            descricao=descricao,
            aceite_lgpd=True,
            codigo_consulta=codigo,
        )

    @staticmethod
    def _validar_lista_anexos(anexos: list[AnexoRecebido]) -> list[AnexoRecebido]:
        """Limita a quantidade de anexos."""
        if len(anexos) > ANEXOS_MAX:
            raise ErroNegocio(f"Envie no máximo {ANEXOS_MAX} arquivos.", 422)
        return anexos

    @staticmethod
    def _validar_anexo(anexo: AnexoRecebido) -> tuple[str, str]:
        """Confere extensão, tamanho e conteúdo; devolve (extensão, content-type)."""
        nome = Path(anexo.nome or "").name
        extensao = nome.rsplit(".", 1)[-1].lower() if "." in nome else ""
        if extensao not in FORMATOS:
            raise ErroNegocio(f'"{nome}": formato não aceito (use PDF, PNG, JPG ou JPEG).', 422)
        if not anexo.conteudo:
            raise ErroNegocio(f'"{nome}": o arquivo está vazio.', 422)
        if len(anexo.conteudo) > ANEXO_TAMANHO_MAX:
            raise ErroNegocio(f'"{nome}": maior que 10 MB.', 422)
        tipo_conteudo, assinatura = FORMATOS[extensao]
        if not anexo.conteudo.startswith(assinatura):
            raise ErroNegocio(f'"{nome}": o conteúdo não corresponde a um arquivo {extensao.upper()}.', 422)
        return ("jpg" if extensao == "jpeg" else extensao), tipo_conteudo

    # ---------- protocolo ----------

    def _gerar_protocolo(self) -> str:
        """Gera um protocolo inédito no formato OUV-AAAAMMDD-XXXXXX."""
        data = agora_utc().strftime("%Y%m%d")
        for _ in range(10):
            sufixo = "".join(secrets.choice(_ALFABETO_PROTOCOLO) for _ in range(6))
            protocolo = f"OUV-{data}-{sufixo}"
            existe = self.db.scalar(
                select(ManifestacaoOuvidoria.id).where(ManifestacaoOuvidoria.protocolo == protocolo)
            )
            if existe is None:
                return protocolo
        raise ErroNegocio("Não foi possível gerar o protocolo agora. Tente novamente.", 503)
