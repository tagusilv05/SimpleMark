# Testes do endpoint público GET /api/v1/documentos/validar/{codigo_verificacao}
from models.models import DocumentoClinico


def _rota_qrcode(id_documento: int) -> str:
    return f"/api/v1/documentos/{id_documento}/qrcode"


def _rota_validar(codigo: str) -> str:
    return f"/api/v1/documentos/validar/{codigo}"


def _gerar(client, criar_documento, autenticar, dono: int = 1, tipo: bool = True):
    documento = criar_documento(dono=dono, tipo=tipo)
    autenticar(dono)
    return documento, client.post(_rota_qrcode(documento.id_documento)).json()


def test_codigo_valido_confirma_o_documento(client, criar_documento, autenticar):
    documento, qrcode = _gerar(client, criar_documento, autenticar)

    resposta = client.get(_rota_validar(qrcode["codigo_verificacao"]))

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["valido"] is True
    assert corpo["documento_id"] == documento.id_documento
    assert corpo["tipo"] == "RECEITA"
    assert corpo["profissional"] == "Profissional 1"
    assert corpo["especialidade"] == "Cardiologia"
    assert corpo["conselho"] == "CRM-PI 12345"
    assert corpo["data_emissao"] is not None
    assert corpo["data_consulta"] == "2026-01-20"


def test_atestado_e_identificado_pelo_tipo(client, criar_documento, autenticar):
    _documento, qrcode = _gerar(client, criar_documento, autenticar, tipo=False)

    corpo = client.get(_rota_validar(qrcode["codigo_verificacao"])).json()

    assert corpo["tipo"] == "ATESTADO"


def test_codigo_inexistente_responde_404(client, cenario):
    resposta = client.get(_rota_validar("codigo-que-nunca-existiu"))

    assert resposta.status_code == 404
    assert resposta.json()["valido"] is False
    assert resposta.json()["documento_id"] is None


def test_documento_sem_qrcode_nao_e_validavel(client, criar_documento):
    criar_documento(dono=1)

    resposta = client.get(_rota_validar("qualquer-coisa"))

    assert resposta.status_code == 404
    assert resposta.json()["valido"] is False


def test_validacao_e_publica_nao_exige_token(client, criar_documento, autenticar, app):
    from dependencies.autenticacao import usuario_atual

    _documento, qrcode = _gerar(client, criar_documento, autenticar)
    app.dependency_overrides.pop(usuario_atual, None)  # derruba o login

    resposta = client.get(_rota_validar(qrcode["codigo_verificacao"]))

    assert resposta.status_code == 200


def test_nao_expoe_dado_clinico_nem_paciente(client, criar_documento, autenticar, db):
    documento, qrcode = _gerar(client, criar_documento, autenticar)
    db.expire_all()
    observacoes = db.get(DocumentoClinico, documento.id_documento).observacoes

    corpo = client.get(_rota_validar(qrcode["codigo_verificacao"])).json()

    texto = str(corpo).lower()
    assert observacoes.lower() not in texto
    assert "observacoes" not in corpo
    assert "paciente" not in texto
    assert "000.000.0001" not in texto


def test_a_url_gravada_no_qrcode_realmente_responde(client, criar_documento, autenticar):
    """Segue o caminho exato que o QR-Code carrega e exige que ele responda 200."""
    documento, qrcode = _gerar(client, criar_documento, autenticar)

    caminho = qrcode["url_validacao"].split("https://simplemark.test", 1)[1]
    assert caminho == f"/api/v1/documentos/validar/{qrcode['codigo_verificacao']}"

    resposta = client.get(caminho)

    assert resposta.status_code == 200
    assert resposta.json()["documento_id"] == documento.id_documento
