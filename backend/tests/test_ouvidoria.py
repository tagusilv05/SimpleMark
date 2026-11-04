# Testes da Ouvidoria: POST /api/v1/ouvidoria/manifestacoes (multipart).
#
# Os anexos vão para uma pasta temporária (OUVIDORIA_PASTA_UPLOADS).
"""Testes da abertura de manifestação na Ouvidoria."""
import uuid
from datetime import date
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select

from dependencies.database import get_db
from dependencies.erros import registrar_erros
from models.models import Paciente, Usuario
from models.ouvidoria import AnexoOuvidoria, ManifestacaoOuvidoria
from routers.ouvidoria import router as ouvidoria_router, usuario_opcional

URL = "/api/v1/ouvidoria/manifestacoes"
PDF = b"%PDF-1.4\n%conteudo de teste\n"
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32


@pytest.fixture
def pasta(tmp_path, monkeypatch):
    """Pasta temporária para os anexos."""
    destino = tmp_path / "ouvidoria"
    monkeypatch.setenv("OUVIDORIA_PASTA_UPLOADS", str(destino))
    return destino


@pytest.fixture
def aplicacao(db, pasta):
    """App só com o router da Ouvidoria."""
    app = FastAPI()
    registrar_erros(app)
    app.include_router(ouvidoria_router, prefix="/api/v1")
    app.dependency_overrides[get_db] = lambda: db
    return app


@pytest.fixture
def cliente(aplicacao):
    """Cliente HTTP de teste."""
    return TestClient(aplicacao)


def _dados(**extra):
    """Campos válidos do formulário, com sobrescritas."""
    base = {
        "solicitante": "paciente",
        "tipo": "teleconsulta",
        "codigo_consulta": "sm-8942-sp",
        "assunto": "Falha  no link da videochamada",
        "descricao": "O link da chamada não abriu no horário marcado da consulta.",
        "aceite_lgpd": "true",
    }
    base.update(extra)
    return {k: v for k, v in base.items() if v is not None}


def test_abre_manifestacao_sem_anexo(cliente, db):
    """Grava a manifestação normalizada e devolve o protocolo."""
    resposta = cliente.post(URL, data=_dados())

    assert resposta.status_code == 201, resposta.text
    corpo = resposta.json()
    assert corpo["protocolo"].startswith("OUV-")
    assert corpo["status"] == "aberta"
    assert corpo["quantidade_anexos"] == 0
    assert corpo["protocolo"] in corpo["mensagem"]

    registro = db.scalar(select(ManifestacaoOuvidoria))
    assert registro.protocolo == corpo["protocolo"]
    assert registro.codigo_consulta == "SM-8942-SP"
    assert registro.assunto == "Falha no link da videochamada"
    assert registro.id_usuario is None
    assert registro.aceite_lgpd is True


def test_abre_manifestacao_com_anexos(cliente, db, pasta):
    """Grava os anexos no disco e na tabela."""
    arquivos = [
        ("anexos", ("laudo.pdf", PDF, "application/pdf")),
        ("anexos", ("tela.PNG", PNG, "image/png")),
    ]
    resposta = cliente.post(URL, data=_dados(), files=arquivos)

    assert resposta.status_code == 201, resposta.text
    assert resposta.json()["quantidade_anexos"] == 2
    anexos = db.scalars(select(AnexoOuvidoria).order_by(AnexoOuvidoria.id)).all()
    assert [a.nome_original for a in anexos] == ["laudo.pdf", "tela.PNG"]
    assert [a.tipo_conteudo for a in anexos] == ["application/pdf", "image/png"]
    assert Path(anexos[0].caminho).read_bytes() == PDF
    assert Path(anexos[0].caminho).parent.parent == pasta


@pytest.mark.parametrize(
    ("campo", "valor", "trecho"),
    [
        ("solicitante", "visitante", "paciente ou profissional"),
        ("tipo", "denuncia", "tipo de manifestação"),
        ("assunto", "abc", "assunto"),
        ("descricao", "curta demais", "descrição"),
        ("aceite_lgpd", "false", "aceitar o termo"),
        ("codigo_consulta", "SM 89/42", "código da consulta"),
    ],
)
def test_recusa_dados_invalidos(cliente, db, campo, valor, trecho):
    """Responde 422 com mensagem em português e não grava nada."""
    resposta = cliente.post(URL, data=_dados(**{campo: valor}))

    assert resposta.status_code == 422
    assert trecho in resposta.json()["mensagem"]
    assert db.scalar(select(ManifestacaoOuvidoria)) is None


def test_recusa_sem_aceite(cliente):
    """Sem o campo de aceite, também recusa."""
    resposta = cliente.post(URL, data=_dados(aceite_lgpd=None))
    assert resposta.status_code == 422


@pytest.mark.parametrize(
    ("nome", "conteudo", "trecho"),
    [
        ("planilha.xlsx", b"PK\x03\x04", "formato não aceito"),
        ("falso.pdf", b"isto nao e pdf", "não corresponde"),
        ("vazio.png", b"", "vazio"),
        ("grande.pdf", b"%PDF-" + b"0" * (10 * 1024 * 1024), "maior que 10 MB"),
    ],
)
def test_recusa_anexo_invalido(cliente, db, pasta, nome, conteudo, trecho):
    """Anexo com formato, conteúdo ou tamanho errado responde 422 e não grava nada."""
    resposta = cliente.post(URL, data=_dados(), files=[("anexos", (nome, conteudo, "application/octet-stream"))])

    assert resposta.status_code == 422
    assert trecho in resposta.json()["mensagem"]
    assert db.scalar(select(ManifestacaoOuvidoria)) is None
    assert not pasta.exists() or not any(pasta.iterdir())


def test_recusa_mais_de_cinco_anexos(cliente):
    """Limite de 5 arquivos."""
    arquivos = [("anexos", (f"a{i}.pdf", PDF, "application/pdf")) for i in range(6)]
    resposta = cliente.post(URL, data=_dados(), files=arquivos)

    assert resposta.status_code == 422
    assert "no máximo 5" in resposta.json()["mensagem"]


def test_vincula_usuario_logado(aplicacao, db):
    """Com usuário logado, a manifestação fica ligada à conta."""
    usuario = Usuario(
        id=uuid.uuid4(),
        nome="Ana Ouvidoria",
        cpf="529.982.247-25",
        orgao_emissor="SSP-PI",
        data_nascimento=date(1990, 5, 1),
        genero="feminino",
        telefone="86999990003",
        email="ana.ouvidoria@email.com",
        status=True,
    )
    db.add(usuario)
    db.flush()
    db.add(Paciente(id_usuario=usuario.id))
    db.commit()
    aplicacao.dependency_overrides[usuario_opcional] = lambda: usuario

    resposta = TestClient(aplicacao).post(URL, data=_dados())

    assert resposta.status_code == 201
    assert db.scalar(select(ManifestacaoOuvidoria)).id_usuario == usuario.id


def test_token_invalido_nao_bloqueia(cliente, db):
    """Token inválido não impede o envio: a manifestação fica anônima."""
    resposta = cliente.post(URL, data=_dados(), headers={"Authorization": "Bearer token-falso"})

    assert resposta.status_code == 201
    assert db.scalar(select(ManifestacaoOuvidoria)).id_usuario is None
