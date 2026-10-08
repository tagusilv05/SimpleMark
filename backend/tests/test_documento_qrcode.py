# Testes do endpoint POST /api/v1/documentos/{documento_id}/qrcode
import base64

from models.models import DocumentoClinico
from services import documento_qrcode as servico

PNG_MAGICO = b"\x89PNG\r\n\x1a\n"


def _rota(id_documento: int) -> str:
    return f"/api/v1/documentos/{id_documento}/qrcode"


def test_gera_qrcode_com_sucesso(client, criar_documento, autenticar, db):
    documento = criar_documento(dono=1)
    autenticar(1)

    resposta = client.post(_rota(documento.id_documento))

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["documento_id"] == documento.id_documento
    assert corpo["codigo_verificacao"]
    assert corpo["url_validacao"] == (
        f"https://simplemark.test/api/v1/documentos/validar/{corpo['codigo_verificacao']}"
    )

    # O base64 precisa ser um PNG de verdade.
    imagem = base64.b64decode(corpo["qr_code_base64"], validate=True)
    assert imagem.startswith(PNG_MAGICO)

    # E tudo tem que estar gravado no banco.
    db.expire_all()
    gravado = db.get(DocumentoClinico, documento.id_documento)
    assert gravado.codigo_verificacao == corpo["codigo_verificacao"]
    assert gravado.qr_code == corpo["qr_code_base64"]
    assert gravado.data_emissao is not None


def test_codigo_nao_e_sequencial(client, criar_documento, autenticar):
    documento = criar_documento(dono=1)
    autenticar(1)

    corpo = client.post(_rota(documento.id_documento)).json()

    assert len(corpo["codigo_verificacao"]) >= 32
    assert corpo["codigo_verificacao"] != str(documento.id_documento)


def test_idempotente_devolve_o_qrcode_existente(client, criar_documento, autenticar):
    documento = criar_documento(dono=1)
    autenticar(1)

    primeira = client.post(_rota(documento.id_documento))
    segunda = client.post(_rota(documento.id_documento))

    assert primeira.status_code == 201
    assert segunda.status_code == 200
    assert segunda.json() == primeira.json()


def test_documento_inexistente_responde_404(client, cenario, autenticar):
    autenticar(1)

    resposta = client.post(_rota(99999))

    assert resposta.status_code == 404


def test_outro_profissional_responde_403(client, criar_documento, autenticar, db):
    documento = criar_documento(dono=1)
    autenticar(2)

    resposta = client.post(_rota(documento.id_documento))

    assert resposta.status_code == 403
    db.expire_all()
    assert db.get(DocumentoClinico, documento.id_documento).codigo_verificacao is None


def test_sem_autenticacao_responde_401(client, criar_documento):
    documento = criar_documento(dono=1)

    resposta = client.post(_rota(documento.id_documento))

    assert resposta.status_code == 401


def test_codigos_sao_unicos_entre_documentos(client, criar_documento, autenticar):
    primeiro = criar_documento(dono=1)
    segundo = criar_documento(dono=1)
    autenticar(1)

    codigo_primeiro = client.post(_rota(primeiro.id_documento)).json()["codigo_verificacao"]
    codigo_segundo = client.post(_rota(segundo.id_documento)).json()["codigo_verificacao"]

    assert codigo_primeiro != codigo_segundo


def test_colisao_de_codigo_tenta_de_novo(client, criar_documento, autenticar, db, monkeypatch):
    ocupado = criar_documento(dono=1)
    autenticar(1)
    codigo_ocupado = client.post(_rota(ocupado.id_documento)).json()["codigo_verificacao"]

    novo = criar_documento(dono=1)
    codigos = iter([codigo_ocupado, "codigo-livre-apos-colisao"])
    monkeypatch.setattr(servico.secrets, "token_urlsafe", lambda _tamanho: next(codigos))

    resposta = client.post(_rota(novo.id_documento))

    assert resposta.status_code == 201
    assert resposta.json()["codigo_verificacao"] == "codigo-livre-apos-colisao"
    db.expire_all()
    assert db.get(DocumentoClinico, ocupado.id_documento).codigo_verificacao == codigo_ocupado


def test_colisao_persistente_nao_grava_codigo_repetido(
    client, criar_documento, autenticar, db, monkeypatch
):
    ocupado = criar_documento(dono=1)
    autenticar(1)
    codigo_ocupado = client.post(_rota(ocupado.id_documento)).json()["codigo_verificacao"]

    novo = criar_documento(dono=1)
    monkeypatch.setattr(servico.secrets, "token_urlsafe", lambda _tamanho: codigo_ocupado)

    resposta = client.post(_rota(novo.id_documento))

    assert resposta.status_code == 500
    db.expire_all()
    assert db.get(DocumentoClinico, novo.id_documento).codigo_verificacao is None
