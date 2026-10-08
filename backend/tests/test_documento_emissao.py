# Testes da emissão de receitas e atestados
import base64

from models.models import Atestado, DocumentoClinico, Receita, ReceitaMedicamento

PNG_MAGICO = b"\x89PNG\r\n\x1a\n"

RECEITA = {
    "id_consulta": None,
    "medicamentos": [
        {
            "medicamento": "Losartana Potássica",
            "dosagem": "50 mg",
            "posologia": "1 comprimido a cada 12 horas",
            "quantidade": "60 comprimidos",
            "duracao_dias": 30,
        },
        {
            "medicamento": "Dipirona",
            "dosagem": "500 mg",
            "posologia": "1 comprimido se dor",
            "quantidade": "20 comprimidos",
        },
    ],
    "validade_dias": 30,
    "observacoes": "Retornar em 30 dias.",
}

ATESTADO = {
    "id_consulta": None,
    "dias_afastamento": 3,
    "data_inicio": "2026-01-20",
    "cid": "j11",
    "finalidade": "Afastamento do trabalho",
}


def _corpo(modelo: dict, id_consulta: int) -> dict:
    return {**modelo, "id_consulta": id_consulta}


def _consulta(cenario, dono: int = 1) -> int:
    return cenario["consultas"][dono].id_consulta


def test_emite_receita_vinculada_a_consulta_e_ao_paciente(client, cenario, autenticar, db):
    autenticar(1)

    resposta = client.post("/api/v1/receitas", json=_corpo(RECEITA, _consulta(cenario)))

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["tipo"] == "RECEITA"
    assert corpo["id_consulta"] == _consulta(cenario)
    assert corpo["paciente"]["nome"] == "Paciente 1"
    assert corpo["paciente"]["cpf"] == "000.000.0001"
    assert corpo["profissional"] == "Profissional 1"
    assert corpo["conselho"] == "CRM-PI 12345"
    assert corpo["validade_dias"] == 30
    assert len(corpo["medicamentos"]) == 2
    assert corpo["medicamentos"][0]["medicamento"] == "Losartana Potássica"
    assert corpo["medicamentos"][1]["duracao_dias"] is None
    assert corpo["dias_afastamento"] is None  # campo de atestado não vaza

    # gravado nas tabelas especializadas
    documento = db.get(DocumentoClinico, corpo["documento_id"])
    assert db.get(Receita, documento.id_documento).validade_dias == 30
    itens = db.query(ReceitaMedicamento).filter_by(id_documento=documento.id_documento).all()
    assert len(itens) == 2


def test_receita_ja_sai_com_qrcode(client, cenario, autenticar):
    autenticar(1)

    corpo = client.post("/api/v1/receitas", json=_corpo(RECEITA, _consulta(cenario))).json()

    assert corpo["codigo_verificacao"]
    assert base64.b64decode(corpo["qr_code_base64"], validate=True).startswith(PNG_MAGICO)
    assert corpo["url_validacao"].endswith(f"/documentos/validar/{corpo['codigo_verificacao']}")


def test_receita_emitida_e_validavel_pelo_qrcode(client, cenario, autenticar):
    autenticar(1)
    corpo = client.post("/api/v1/receitas", json=_corpo(RECEITA, _consulta(cenario))).json()

    caminho = corpo["url_validacao"].split("https://simplemark.test", 1)[1]
    validacao = client.get(caminho)

    assert validacao.status_code == 200
    assert validacao.json()["valido"] is True
    assert validacao.json()["tipo"] == "RECEITA"


def test_emite_atestado(client, cenario, autenticar, db):
    autenticar(1)

    resposta = client.post("/api/v1/atestados", json=_corpo(ATESTADO, _consulta(cenario)))

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["tipo"] == "ATESTADO"
    assert corpo["dias_afastamento"] == 3
    assert corpo["data_inicio"] == "2026-01-20"
    assert corpo["cid"] == "J11"  # normalizado para maiúsculo
    assert corpo["medicamentos"] is None  # campo de receita não vaza

    assert db.get(Atestado, corpo["documento_id"]).dias_afastamento == 3


def test_atestado_e_validavel_e_identificado_como_atestado(client, cenario, autenticar):
    autenticar(1)
    corpo = client.post("/api/v1/atestados", json=_corpo(ATESTADO, _consulta(cenario))).json()

    caminho = corpo["url_validacao"].split("https://simplemark.test", 1)[1]

    assert client.get(caminho).json()["tipo"] == "ATESTADO"


def test_cid_e_finalidade_sao_opcionais(client, cenario, autenticar):
    autenticar(1)
    sem_cid = {k: v for k, v in ATESTADO.items() if k not in {"cid", "finalidade"}}

    corpo = client.post("/api/v1/atestados", json=_corpo(sem_cid, _consulta(cenario))).json()

    assert corpo["cid"] is None
    assert corpo["finalidade"] is None


def test_outro_profissional_nao_emite_na_consulta_alheia(client, cenario, autenticar, db):
    autenticar(2)

    resposta = client.post("/api/v1/receitas", json=_corpo(RECEITA, _consulta(cenario, dono=1)))

    assert resposta.status_code == 403
    assert db.query(DocumentoClinico).count() == 0


def test_consulta_inexistente_responde_404(client, cenario, autenticar):
    autenticar(1)

    resposta = client.post("/api/v1/receitas", json=_corpo(RECEITA, 99999))

    assert resposta.status_code == 404


def test_sem_autenticacao_responde_401(client, cenario):
    resposta = client.post("/api/v1/receitas", json=_corpo(RECEITA, _consulta(cenario)))

    assert resposta.status_code == 401


def test_consulta_cancelada_nao_permite_emissao(client, cenario, autenticar, db):
    consulta = cenario["consultas"][1]
    consulta.status = "cancelada"
    db.commit()
    autenticar(1)

    resposta = client.post("/api/v1/receitas", json=_corpo(RECEITA, consulta.id_consulta))

    assert resposta.status_code == 400
    assert db.query(DocumentoClinico).count() == 0


def test_receita_sem_medicamento_e_recusada(client, cenario, autenticar, db):
    autenticar(1)
    vazia = {**RECEITA, "medicamentos": []}

    resposta = client.post("/api/v1/receitas", json=_corpo(vazia, _consulta(cenario)))

    assert resposta.status_code == 422
    assert db.query(DocumentoClinico).count() == 0


def test_dias_de_afastamento_precisa_ser_positivo(client, cenario, autenticar):
    autenticar(1)
    invalido = {**ATESTADO, "dias_afastamento": 0}

    resposta = client.post("/api/v1/atestados", json=_corpo(invalido, _consulta(cenario)))

    assert resposta.status_code == 422


def test_documentos_da_consulta_lista_os_emitidos(client, cenario, autenticar):
    autenticar(1)
    id_consulta = _consulta(cenario)
    client.post("/api/v1/receitas", json=_corpo(RECEITA, id_consulta))
    client.post("/api/v1/atestados", json=_corpo(ATESTADO, id_consulta))

    resposta = client.get(f"/api/v1/consultas/{id_consulta}/documentos")

    assert resposta.status_code == 200
    tipos = [item["tipo"] for item in resposta.json()]
    assert tipos == ["RECEITA", "ATESTADO"]
    assert all(item["codigo_verificacao"] for item in resposta.json())


def test_listagem_nao_vaza_para_outro_profissional(client, cenario, autenticar):
    autenticar(1)
    id_consulta = _consulta(cenario)
    client.post("/api/v1/receitas", json=_corpo(RECEITA, id_consulta))
    autenticar(2)

    assert client.get(f"/api/v1/consultas/{id_consulta}/documentos").status_code == 403


def test_busca_documento_emitido_por_id(client, cenario, autenticar):
    autenticar(1)
    emitido = client.post("/api/v1/receitas", json=_corpo(RECEITA, _consulta(cenario))).json()

    resposta = client.get(f"/api/v1/documentos/{emitido['documento_id']}")

    assert resposta.status_code == 200
    assert resposta.json() == emitido


def test_documento_de_outro_profissional_responde_403(client, cenario, autenticar):
    autenticar(1)
    emitido = client.post("/api/v1/receitas", json=_corpo(RECEITA, _consulta(cenario))).json()
    autenticar(2)

    assert client.get(f"/api/v1/documentos/{emitido['documento_id']}").status_code == 403


def test_cada_documento_emitido_tem_codigo_proprio(client, cenario, autenticar):
    autenticar(1)
    id_consulta = _consulta(cenario)

    primeiro = client.post("/api/v1/receitas", json=_corpo(RECEITA, id_consulta)).json()
    segundo = client.post("/api/v1/atestados", json=_corpo(ATESTADO, id_consulta)).json()

    assert primeiro["codigo_verificacao"] != segundo["codigo_verificacao"]
