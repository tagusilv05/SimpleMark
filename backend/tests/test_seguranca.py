"""Testes de segurança da API (ver docs/seguranca.md).

Diferente dos outros testes, aqui a autenticação NÃO é trocada por um
``dependency_override``: cada usuário recebe uma sessão de verdade no banco e um
JWT assinado, então o caminho completo (cabeçalho -> token -> sessão -> usuário
-> perfil) é exercitado.

O app de teste é montado lendo os ``include_router`` do ``main.py``, para ter as
mesmas rotas e prefixos da API real sem rodar o ``create_all``/seed do import.

Os testes marcados com ``xfail(strict=True)`` documentam falhas que AINDA
existem (achados do relatório). Eles "falham como esperado" hoje; quando a falha
for corrigida, o pytest acusa XPASS e o marcador deve ser removido, para o teste
passar a proteger a correção.
"""

import importlib
import re
import uuid
from datetime import date, time, timedelta
from pathlib import Path

import jwt
import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from core.parametros import login_max_tentativas
from core.seguranca import gerar_hash_senha, gerar_token_acesso
from core.tempo import agora_utc
from dependencies import autenticacao
from dependencies.database import get_db
from dependencies.erros import registrar_erros
from models.acesso import Credencial, SessaoLogin
from models.models import (
    Administrador,
    Avaliacao,
    Consulta,
    DataHorario,
    DocumentoClinico,
    Paciente,
    Usuario,
)

MAIN = Path(__file__).resolve().parent.parent / "main.py"

DEPENDENCIAS_DE_LOGIN = {
    autenticacao.sessao_atual,
    autenticacao.usuario_atual,
    autenticacao.administrador_atual,
    autenticacao.paciente_atual,
}

# Rotas que DEVEM ser públicas, com o motivo. Uma rota pública nova que não
# esteja aqui faz o teste test_rotas_publicas_sao_so_as_esperadas falhar.
PUBLICAS_ESPERADAS = {
    ("POST", "/api/v1/cadastro/paciente"): "cadastro",
    ("POST", "/api/v1/cadastro/profissional"): "cadastro",
    ("POST", "/api/v1/auth/login"): "login (etapa 1)",
    ("POST", "/api/v1/auth/login/confirmar"): "login (etapa 2)",
    ("POST", "/api/v1/auth/senha/esqueci"): "recuperação de senha",
    ("POST", "/api/v1/auth/senha/redefinir"): "recuperação de senha",
    ("POST", "/api/v1/ouvidoria/manifestacoes"): "ouvidoria aceita anônimos",
    ("GET", "/api/v1/profissionais/busca"): "busca pública de profissionais",
    ("GET", "/api/v1/documentos/validar/{codigo_verificacao}"): "validação pública do QR-Code",
    ("GET", "/api/v1/avaliacoes/profissionais/{id_profissional}/media"): "vitrine pública",
    ("GET", "/api/v1/avaliacoes/profissionais/{id_profissional}/avaliacoes"): "vitrine pública",
    ("GET", "/api/v1/avaliacoes/profissionais/melhor-avaliados"): "vitrine pública",
    ("GET", "/profissionais/buscar-info-profissional/{id_usuario}"): "perfil público do profissional",
    ("GET", "/profissionais/buscar-imagem-profissional/{id_usuario}"): "foto pública do profissional",
    ("GET", "/profissionais/lista-especialidade"): "lista de especialidades",
    ("GET", "/profissional/horarios"): "horários livres na tela de agendamento do paciente (sem dados de paciente)",
    ("POST", "/avaliacao/buscar-avaliacoes"): "vitrine pública (ver achado sobre nome do paciente)",
    ("GET", "/api/v1/pagamento/retorno/sucesso"): "retorno do Mercado Pago",
    ("GET", "/api/v1/pagamento/retorno/pendente"): "retorno do Mercado Pago",
    ("GET", "/api/v1/pagamento/retorno/falha"): "retorno do Mercado Pago",
    ("POST", "/api/v1/pagamento/notificacao"): "webhook do Mercado Pago",
}

# Achado 1 do relatório: públicas hoje, mas deveriam exigir login.
PUBLICAS_POR_ENGANO = {
    ("POST", "/profissional/horarios"),
    ("PUT", "/profissional/horarios/{id_horario}"),
    ("DELETE", "/profissional/horarios/{id_horario}"),
    ("GET", "/api/v1/consultas_profissionais/{id_profissional}/consultas"),
    ("POST", "/consulta/confirmar-consulta"),
}

ACHADO_1 = "Achado 1 (docs/seguranca.md): rota sem autenticação/autorização"


# --------------------------------------------------------------------------- #
# App com as rotas do main.py
# --------------------------------------------------------------------------- #


def _routers_do_main():
    """Lê o main.py e devolve [(router, prefixo)] na ordem em que são incluídos."""
    codigo = "\n".join(
        linha for linha in MAIN.read_text(encoding="utf-8").splitlines()
        if not linha.lstrip().startswith("#")
    )
    apelidos = dict(
        (apelido, modulo)
        for modulo, apelido in re.findall(r"from (routers\.[\w.]+) import router as (\w+)", codigo)
    )
    incluidos = re.findall(r"app\.include_router\((\w+)(?:,\s*prefix=\"([^\"]*)\")?", codigo)
    return [(importlib.import_module(apelidos[nome]).router, prefixo) for nome, prefixo in incluidos]


def _rotas(app):
    """Todas as rotas da API como [(metodo, caminho, APIRoute)]."""
    rotas = []
    for router, prefixo in _routers_do_main():
        for rota in router.routes:
            if isinstance(rota, APIRoute):
                for metodo in rota.methods:
                    rotas.append((metodo, prefixo + rota.path, rota))
    return rotas


def _exige_login(rota: APIRoute) -> bool:
    """True se alguma dependência (em qualquer nível) for de autenticação."""
    pendentes = list(rota.dependant.dependencies)
    while pendentes:
        dependencia = pendentes.pop()
        if dependencia.call in DEPENDENCIAS_DE_LOGIN:
            return True
        pendentes.extend(dependencia.dependencies)
    return False


@pytest.fixture
def api(db):
    """App com todas as rotas do main.py sobre o SQLite de teste (sem override de login)."""
    aplicacao = FastAPI()
    registrar_erros(aplicacao)
    for router, prefixo in _routers_do_main():
        aplicacao.include_router(router, prefix=prefixo)
    aplicacao.dependency_overrides[get_db] = lambda: db
    return TestClient(aplicacao)


TODAS_AS_ROTAS = _rotas(None)
ROTAS_PROTEGIDAS = [(m, p, r) for m, p, r in TODAS_AS_ROTAS if _exige_login(r)]


# --------------------------------------------------------------------------- #
# Dados e tokens
# --------------------------------------------------------------------------- #


def _token(db, usuario: Usuario, encerrada: bool = False) -> str:
    """Abre uma sessão real no banco e devolve o JWT dela."""
    agora = agora_utc()
    sessao = SessaoLogin(
        id=uuid.uuid4(),
        id_usuario=usuario.id,
        criada_em=agora,
        ultima_atividade_em=agora,
        encerrada_em=agora if encerrada else None,
    )
    db.add(sessao)
    db.commit()
    return gerar_token_acesso(usuario.id, sessao.id)


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _novo_usuario(db, n: int, **campos) -> Usuario:
    usuario = Usuario(
        id=uuid.uuid4(),
        nome=f"Usuário {n}",
        cpf=f"222.222.22{n:02d}",
        orgao_emissor="SSP-PI",
        data_nascimento=date(1991, 2, 3),
        genero="Não informado",
        telefone=f"(86) 97777-{n:04d}",
        email=f"usuario{n}@email.com",
        status=True,
        **campos,
    )
    db.add(usuario)
    db.flush()
    return usuario


@pytest.fixture
def pessoas(db, cenario):
    """Paciente 1 (com consultas), paciente 2 (sem nada), profissionais 1 e 2 e um admin."""
    paciente1 = db.get(Usuario, cenario["paciente"].id_usuario)
    usuario_p2 = _novo_usuario(db, 50)
    db.add(Paciente(id_usuario=usuario_p2.id))
    usuario_admin = _novo_usuario(db, 51)
    db.add(Administrador(id_usuario=usuario_admin.id))
    db.commit()
    prof1 = db.get(Usuario, cenario["profissionais"][1].id_usuario)
    prof2 = db.get(Usuario, cenario["profissionais"][2].id_usuario)
    return {
        "paciente1": paciente1,
        "paciente2": db.get(Usuario, usuario_p2.id),
        "prof1": prof1,
        "prof2": prof2,
        "admin": db.get(Usuario, usuario_admin.id),
        "consulta_prof1": cenario["consultas"][1],
    }


def _valor_ficticio(tipo):
    if tipo is int:
        return "999999"
    if tipo is uuid.UUID:
        return str(uuid.uuid4())
    return "abc"


def _url(caminho: str, rota: APIRoute) -> str:
    """Troca os {parametros} do caminho por valores do tipo certo."""
    for parametro in rota.dependant.path_params:
        caminho = caminho.replace("{%s}" % parametro.name, _valor_ficticio(parametro.field_info.annotation))
    return caminho


# --------------------------------------------------------------------------- #
# 1. Rotas protegidas exigem token válido (401/403)
# --------------------------------------------------------------------------- #


def test_mapa_de_rotas_tem_rotas_protegidas():
    """Sanidade: o mapa achou as rotas do main.py e boa parte exige login."""
    assert len(TODAS_AS_ROTAS) >= 60
    assert len(ROTAS_PROTEGIDAS) >= 35


@pytest.mark.parametrize(
    "metodo,caminho,rota", ROTAS_PROTEGIDAS, ids=[f"{m} {p}" for m, p, _ in ROTAS_PROTEGIDAS]
)
def test_rota_protegida_sem_token_responde_401(api, metodo, caminho, rota):
    resposta = api.request(metodo, _url(caminho, rota), json={})
    assert resposta.status_code == 401, resposta.text


@pytest.mark.parametrize(
    "metodo,caminho,rota", ROTAS_PROTEGIDAS, ids=[f"{m} {p}" for m, p, _ in ROTAS_PROTEGIDAS]
)
def test_rota_protegida_com_token_invalido_responde_401(api, metodo, caminho, rota):
    resposta = api.request(metodo, _url(caminho, rota), json={}, headers=_auth("nao.e.um.jwt"))
    assert resposta.status_code == 401, resposta.text


def test_rotas_publicas_sao_so_as_esperadas():
    """Toda rota sem login precisa estar na lista de públicas (ou nos achados conhecidos)."""
    publicas = {(m, p) for m, p, r in TODAS_AS_ROTAS if not _exige_login(r)}
    inesperadas = publicas - set(PUBLICAS_ESPERADAS) - PUBLICAS_POR_ENGANO
    assert not inesperadas, f"Rotas públicas novas, sem justificativa: {sorted(inesperadas)}"


@pytest.mark.xfail(strict=True, reason=ACHADO_1)
@pytest.mark.parametrize("metodo,caminho", sorted(PUBLICAS_POR_ENGANO))
def test_rotas_da_agenda_e_consultas_exigem_login(api, metodo, caminho):
    rota = next(r for m, p, r in TODAS_AS_ROTAS if (m, p) == (metodo, caminho))
    corpo = {
        "id_esp_prof": 1, "datas": ["2030-01-01"],
        "lista_horarios": [{"hora_inicio": "08:00", "hora_fim": "09:00"}],
        "hora_inicio": "08:00", "hora_fim": "09:00",
    }
    resposta = api.request(metodo, _url(caminho, rota), json=corpo, params={"id_esp_prof": 1})
    assert resposta.status_code in (401, 403), resposta.text


def test_token_com_assinatura_de_outra_chave_responde_401(api, db, pessoas):
    sessao_token = _token(db, pessoas["paciente1"])
    payload = jwt.decode(sessao_token, options={"verify_signature": False})
    forjado = jwt.encode(payload, "chave-do-atacante", algorithm="HS256")
    assert api.get("/api/v1/auth/eu", headers=_auth(forjado)).status_code == 401


def test_token_sem_assinatura_alg_none_responde_401(api, db, pessoas):
    sessao_token = _token(db, pessoas["paciente1"])
    payload = jwt.decode(sessao_token, options={"verify_signature": False})
    sem_assinatura = jwt.encode(payload, key=None, algorithm="none")
    assert api.get("/api/v1/auth/eu", headers=_auth(sem_assinatura)).status_code == 401


def test_token_de_sessao_encerrada_responde_401(api, db, pessoas):
    token = _token(db, pessoas["paciente1"], encerrada=True)
    assert api.get("/api/v1/auth/eu", headers=_auth(token)).status_code == 401


def test_token_de_sessao_inexistente_responde_401(api, pessoas):
    token = gerar_token_acesso(pessoas["paciente1"].id, uuid.uuid4())
    assert api.get("/api/v1/auth/eu", headers=_auth(token)).status_code == 401


def test_token_valido_e_aceito(api, db, pessoas):
    """Controle: o mesmo caminho com token bom funciona (os 401 acima não são falso positivo)."""
    resposta = api.get("/api/v1/auth/eu", headers=_auth(_token(db, pessoas["paciente1"])))
    assert resposta.status_code == 200, resposta.text


def test_conta_inativa_nao_usa_token_antigo(api, db, pessoas):
    token = _token(db, pessoas["paciente1"])
    pessoas["paciente1"].status = False
    db.commit()
    assert api.get("/api/v1/auth/eu", headers=_auth(token)).status_code == 401


@pytest.mark.parametrize("perfil", ["paciente1", "prof1"])
def test_rotas_de_administracao_recusam_quem_nao_e_admin(api, db, pessoas, perfil):
    token = _token(db, pessoas[perfil])
    for caminho in ("/api/v1/administracao/profissionais/pendentes", "/api/v1/administracao/logs"):
        assert api.get(caminho, headers=_auth(token)).status_code == 403


def test_admin_acessa_rotas_de_administracao(api, db, pessoas):
    token = _token(db, pessoas["admin"])
    assert api.get("/api/v1/administracao/logs", headers=_auth(token)).status_code == 200


# --------------------------------------------------------------------------- #
# 2. Um usuário não acessa dados de outro (IDOR)
# --------------------------------------------------------------------------- #


def test_usuario_nao_le_dados_de_outra_conta(api, db, pessoas):
    token = _token(db, pessoas["paciente2"])
    alvo = pessoas["paciente1"].id
    assert api.get(f"/usuario/buscar-info-usuario/{alvo}", headers=_auth(token)).status_code == 403
    assert api.get(f"/usuario/buscar-info-endereco/{alvo}", headers=_auth(token)).status_code == 403


def test_usuario_nao_altera_nem_exclui_outra_conta(api, db, pessoas):
    token = _token(db, pessoas["paciente2"])
    alvo = str(pessoas["paciente1"].id)
    r1 = api.put("/usuario/altera-info-pessoal", json={"id": alvo, "nome": "Invasor"}, headers=_auth(token))
    r2 = api.request("DELETE", "/usuario/excluir-usuario", json={"id": alvo, "tipo": "paciente"}, headers=_auth(token))
    r3 = api.patch("/usuario/inativar-usuario", params={"id_usuario": alvo}, headers=_auth(token))
    assert (r1.status_code, r2.status_code, r3.status_code) == (403, 403, 403)
    db.refresh(pessoas["paciente1"])
    assert pessoas["paciente1"].nome == "Paciente 1" and pessoas["paciente1"].status is True


def test_profissional_nao_altera_valor_de_outro_profissional(api, db, pessoas):
    token = _token(db, pessoas["prof2"])
    corpo = {"id_usuario": str(pessoas["prof1"].id), "id_especialidade": 1, "valor_consulta": 1}
    assert api.put("/profissionais/alterar-valor-consulta", json=corpo, headers=_auth(token)).status_code == 403


def test_paciente_nao_ve_consulta_de_outro_paciente(api, db, pessoas):
    token = _token(db, pessoas["paciente2"])
    id_consulta = pessoas["consulta_prof1"].id_consulta
    assert api.get(f"/consultas/minhas/{id_consulta}", headers=_auth(token)).status_code == 404
    assert api.get("/consultas/minhas", headers=_auth(token)).json()["total"] == 0


def test_paciente_nao_ve_pagamento_de_consulta_alheia(api, db, pessoas):
    token = _token(db, pessoas["paciente2"])
    id_consulta = pessoas["consulta_prof1"].id_consulta
    assert api.get(f"/api/v1/pagamento/{id_consulta}", headers=_auth(token)).status_code == 404


def test_estranho_nao_ve_videochamada_da_consulta(api, db, pessoas):
    id_consulta = pessoas["consulta_prof1"].id_consulta
    for intruso in ("prof2", "paciente2"):
        token = _token(db, pessoas[intruso])
        resposta = api.get(f"/api/v1/consultas/{id_consulta}/videochamada", headers=_auth(token))
        assert resposta.status_code == 404, intruso


def test_profissional_nao_emite_receita_em_consulta_de_outro(api, db, pessoas):
    token = _token(db, pessoas["prof2"])
    corpo = {
        "id_consulta": pessoas["consulta_prof1"].id_consulta,
        "medicamentos": [{"medicamento": "X", "dosagem": "1", "posologia": "1", "quantidade": "1"}],
    }
    assert api.post("/api/v1/receitas", json=corpo, headers=_auth(token)).status_code == 403
    assert db.query(DocumentoClinico).count() == 0


def test_paciente_nao_le_documento_de_outro_paciente(api, db, pessoas):
    documento = DocumentoClinico(id_consulta=pessoas["consulta_prof1"].id_consulta, observacoes="x", tipo=True)
    db.add(documento)
    db.commit()
    token = _token(db, pessoas["paciente2"])
    resposta = api.get(f"/api/v1/documentos/{documento.id_documento}", headers=_auth(token))
    assert resposta.status_code in (403, 404)


def test_paciente_nao_avalia_consulta_de_outro(api, db, pessoas):
    token = _token(db, pessoas["paciente2"])
    id_consulta = pessoas["consulta_prof1"].id_consulta
    resposta = api.post(
        f"/api/v1/avaliacoes/consultas/{id_consulta}/avaliacao", json={"nota": 5}, headers=_auth(token)
    )
    assert resposta.status_code in (403, 404)
    assert db.query(Avaliacao).count() == 0


@pytest.mark.xfail(strict=True, reason=ACHADO_1)
def test_anonimo_nao_le_consultas_e_dados_de_pacientes_do_profissional(api, pessoas):
    id_profissional = pessoas["prof1"].profissional.id_profissional
    resposta = api.get(
        f"/api/v1/consultas_profissionais/{id_profissional}/consultas", params={"status": "realizada"}
    )
    assert resposta.status_code in (401, 403)
    assert "paciente1@email.com" not in resposta.text


def test_listagem_publica_de_horarios_so_traz_dados_da_agenda(api, db, pessoas):
    """GET /profissional/horarios é público (agendamento); não pode trazer dado pessoal."""
    esp_prof = pessoas["consulta_prof1"].id_esp_prof
    db.add(DataHorario(id_esp_prof=esp_prof, data_consulta=date(2030, 1, 1),
                       hora_inicio=time(8), hora_fim=time(9), ocupado=True))
    db.commit()
    resposta = api.get("/profissional/horarios", params={"id_esp_prof": esp_prof, "data": "2030-01-01"})
    assert resposta.status_code == 200
    campos = {chave for horario in resposta.json() for chave in horario}
    assert campos <= {"id_horario", "id_esp_prof", "data_consulta", "hora_inicio", "hora_fim", "ocupado"}
    assert "paciente" not in resposta.text.lower() and "@" not in resposta.text


@pytest.mark.xfail(strict=True, reason=ACHADO_1)
def test_anonimo_nao_apaga_horario_de_profissional(api, db, pessoas):
    esp_prof = pessoas["consulta_prof1"].id_esp_prof
    horario = DataHorario(id_esp_prof=esp_prof, data_consulta=date(2030, 1, 1),
                          hora_inicio=time(8), hora_fim=time(9), ocupado=False)
    db.add(horario)
    db.commit()
    id_horario = horario.id_horario
    api.delete(f"/profissional/horarios/{id_horario}")
    db.expire_all()
    assert db.get(DataHorario, id_horario) is not None


@pytest.mark.xfail(strict=True, reason=ACHADO_1)
def test_anonimo_nao_marca_consulta_em_nome_de_paciente(api, db, pessoas):
    corpo = {
        "id_usuario_paciente": str(pessoas["paciente1"].id),
        "id_usuario_profissional": str(pessoas["prof1"].id),
        "id_especialidade": 1,
        "data": "2030-01-01",
        "hora": "10:00",
        "tipo": "consulta",
        "status": "agendado",
        "valor": 0.01,  # o cliente escolhe até o preço da consulta
    }
    antes = db.query(Consulta).count()
    resposta = api.post("/consulta/confirmar-consulta", json=corpo)
    db.expire_all()
    assert resposta.status_code in (401, 403)
    assert db.query(Consulta).count() == antes


@pytest.mark.xfail(strict=True, reason="Achado 6 (docs/seguranca.md): nome completo do paciente exposto")
def test_vitrine_de_avaliacoes_nao_expoe_nome_completo_do_paciente(api, db, pessoas):
    consulta = pessoas["consulta_prof1"]
    db.add(Avaliacao(id_consulta=consulta.id_consulta, avaliacao=5, feedback="Ótimo",
                     data=date(2026, 1, 21), hora=time(9)))
    db.commit()
    resposta = api.post("/avaliacao/buscar-avaliacoes", json={"id_usuario": str(pessoas["prof1"].id)})
    assert resposta.status_code == 200
    assert "Paciente 1" not in resposta.text


# --------------------------------------------------------------------------- #
# 3. Entradas inválidas ou maliciosas são rejeitadas com segurança
# --------------------------------------------------------------------------- #

INJECOES_SQL = ["' OR '1'='1", "'; DROP TABLE usuario; --", "\" OR 1=1 --", "1 UNION SELECT senha_hash FROM credencial"]


@pytest.mark.parametrize("payload", INJECOES_SQL)
def test_busca_de_profissional_trata_sql_injection_como_texto(api, db, pessoas, payload):
    resposta = api.get("/api/v1/profissionais/busca", params={"especialidade": payload})
    assert resposta.status_code == 200
    assert resposta.json() == []
    assert db.query(Usuario).count() >= 5  # tabela intacta


@pytest.mark.parametrize("payload", INJECOES_SQL)
def test_validacao_de_documento_trata_sql_injection_como_texto(api, payload):
    resposta = api.get(f"/api/v1/documentos/validar/{payload}")
    assert resposta.status_code < 500
    assert resposta.status_code == 404 or resposta.json().get("valido") is False


@pytest.mark.parametrize("payload", INJECOES_SQL)
def test_login_com_sql_injection_e_recusado_sem_detalhes(api, payload):
    resposta = api.post("/api/v1/auth/login", json={"identificador": payload, "senha": payload})
    assert resposta.status_code in (401, 422)  # credencial inválida ou formato recusado
    assert "sql" not in resposta.text.lower() and "traceback" not in resposta.text.lower()


def test_login_nao_revela_se_a_conta_existe(api, db, pessoas):
    db.add(Credencial(id_usuario=pessoas["paciente1"].id, senha_hash=gerar_hash_senha("SenhaCerta1")))
    db.commit()
    existe = api.post("/api/v1/auth/login", json={"identificador": "paciente1@email.com", "senha": "errada123"})
    nao_existe = api.post("/api/v1/auth/login", json={"identificador": "ninguem@email.com", "senha": "errada123"})
    assert existe.status_code == nao_existe.status_code == 401
    assert existe.json() == nao_existe.json()


def test_login_bloqueia_apos_tentativas_erradas(api, db, pessoas):
    db.add(Credencial(id_usuario=pessoas["paciente1"].id, senha_hash=gerar_hash_senha("SenhaCerta1")))
    db.commit()
    corpo = {"identificador": "paciente1@email.com", "senha": "errada123"}
    for _ in range(login_max_tentativas()):
        api.post("/api/v1/auth/login", json=corpo)
    certa = api.post("/api/v1/auth/login", json={**corpo, "senha": "SenhaCerta1"})
    assert certa.status_code == 429


def test_senha_nao_e_guardada_em_texto_puro(db, pessoas):
    db.add(Credencial(id_usuario=pessoas["paciente1"].id, senha_hash=gerar_hash_senha("SenhaCerta1")))
    db.commit()
    guardada = db.get(Credencial, pessoas["paciente1"].id).senha_hash
    assert "SenhaCerta1" not in guardada and guardada.startswith("$argon2")


CADASTRO_VALIDO = {
    "nome": "Fulano de Tal", "cpf": "529.982.247-25", "orgao_emissor": "SSP",
    "data_nascimento": "1990-01-01", "genero": "Outro", "telefone": "86999990000",
    "email": "fulano@email.com", "senha": "SenhaForte1", "consentimento_lgpd": True,
    "cep": "64000-000", "cidade": "Teresina", "logradouro": "Rua A", "numero": "1", "bairro": "Centro",
}


def test_controle_cadastro_valido_e_aceito(api):
    """Controle: prova que o 422 dos casos abaixo vem só do campo alterado."""
    resposta = api.post("/api/v1/cadastro/paciente", json=CADASTRO_VALIDO)
    assert resposta.status_code in (200, 201), resposta.text


@pytest.mark.parametrize(
    "campo,valor",
    [
        ("senha", "curta"),                 # menos de 8 caracteres
        ("nome", "A" * 151),                # acima do max_length
        ("cpf", "111.111.111-11"),          # CPF inválido
        ("email", "nao-e-email"),
        ("nome", None),                     # obrigatório
    ],
)
def test_cadastro_rejeita_entrada_invalida(api, db, campo, valor):
    corpo = dict(CADASTRO_VALIDO)
    corpo[campo] = valor
    antes = db.query(Usuario).count()
    resposta = api.post("/api/v1/cadastro/paciente", json=corpo)
    assert resposta.status_code == 422, resposta.text
    assert db.query(Usuario).count() == antes


def test_html_no_nome_e_guardado_como_texto_e_devolvido_como_json(api, db, pessoas):
    """A API responde JSON; um <script> no nome não é interpretado pelo servidor."""
    token = _token(db, pessoas["paciente1"])
    nome = "<script>alert(1)</script>"
    resposta = api.put(
        "/usuario/altera-info-pessoal", json={"id": str(pessoas["paciente1"].id), "nome": nome}, headers=_auth(token)
    )
    assert resposta.status_code == 200
    assert resposta.headers["content-type"].startswith("application/json")


def test_controle_avaliacao_valida_e_aceita(api, db, pessoas):
    token = _token(db, pessoas["paciente1"])
    id_consulta = pessoas["consulta_prof1"].id_consulta
    resposta = api.post(
        f"/api/v1/avaliacoes/consultas/{id_consulta}/avaliacao", json={"nota": 5}, headers=_auth(token)
    )
    assert resposta.status_code in (200, 201), resposta.text


@pytest.mark.parametrize(
    "corpo", [{"nota": 6}, {"nota": 0}, {"nota": "5 OR 1=1"}, {"feedback": "x" * 5000}, {"nota": 5, "id_paciente": 1}]
)
def test_avaliacao_rejeita_nota_fora_da_faixa_ou_texto_gigante(api, db, pessoas, corpo):
    token = _token(db, pessoas["paciente1"])
    id_consulta = pessoas["consulta_prof1"].id_consulta
    resposta = api.post(f"/api/v1/avaliacoes/consultas/{id_consulta}/avaliacao", json=corpo, headers=_auth(token))
    assert resposta.status_code == 422, resposta.text
    assert db.query(Avaliacao).count() == 0


def test_controle_atestado_valido_e_aceito(api, db, pessoas):
    token = _token(db, pessoas["prof1"])
    corpo = {"id_consulta": pessoas["consulta_prof1"].id_consulta, "dias_afastamento": 2, "data_inicio": "2026-01-20"}
    resposta = api.post("/api/v1/atestados", json=corpo, headers=_auth(token))
    assert resposta.status_code in (200, 201), resposta.text


@pytest.mark.parametrize("dias", [0, -5, 10_000])
def test_atestado_rejeita_dias_invalidos(api, db, pessoas, dias):
    token = _token(db, pessoas["prof1"])
    corpo = {"id_consulta": pessoas["consulta_prof1"].id_consulta, "dias_afastamento": dias, "data_inicio": "2026-01-20"}
    assert api.post("/api/v1/atestados", json=corpo, headers=_auth(token)).status_code == 422


PNG_1X1 = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)


def test_controle_upload_de_imagem_valida_e_aceito(api, db, pessoas, tmp_path, monkeypatch):
    from services import porfissional_minha_conta as servico
    monkeypatch.setattr(servico, "PASTA_IMAGENS", tmp_path)
    token = _token(db, pessoas["prof1"])
    resposta = api.post(
        "/profissionais/salvar-imagem-profissional",
        data={"id_usuario": str(pessoas["prof1"].id)},
        files={"imagem": ("foto.png", PNG_1X1, "image/png")},
        headers=_auth(token),
    )
    assert resposta.status_code == 200, resposta.text


def test_upload_de_foto_recusa_arquivo_que_nao_e_imagem(api, db, pessoas):
    token = _token(db, pessoas["prof1"])
    resposta = api.post(
        "/profissionais/salvar-imagem-profissional",
        data={"id_usuario": str(pessoas["prof1"].id)},
        files={"imagem": ("shell.php", b"<?php system($_GET['c']); ?>", "application/x-php")},
        headers=_auth(token),
    )
    assert resposta.status_code == 400


OUVIDORIA_VALIDA = {
    "solicitante": "paciente", "tipo": "reclamacao", "assunto": "Assunto de teste",
    "descricao": "Descrição com mais de vinte caracteres.", "aceite_lgpd": "true",
}


def test_controle_ouvidoria_com_pdf_real_e_aceita(api, tmp_path, monkeypatch):
    monkeypatch.setenv("OUVIDORIA_PASTA_UPLOADS", str(tmp_path))
    resposta = api.post(
        "/api/v1/ouvidoria/manifestacoes",
        data=OUVIDORIA_VALIDA,
        files={"anexos": ("nota.pdf", b"%PDF-1.4\n%fim", "application/pdf")},
    )
    assert resposta.status_code in (200, 201), resposta.text


def test_ouvidoria_recusa_anexo_com_conteudo_falso(api, tmp_path, monkeypatch):
    monkeypatch.setenv("OUVIDORIA_PASTA_UPLOADS", str(tmp_path))
    resposta = api.post(
        "/api/v1/ouvidoria/manifestacoes",
        data=OUVIDORIA_VALIDA,
        files={"anexos": ("nota.pdf", b"MZ\x90\x00 isto nao e um pdf", "application/pdf")},
    )
    assert resposta.status_code == 422


def test_json_invalido_no_campo_dados_nao_vaza_detalhes(api, db, pessoas):
    token = _token(db, pessoas["prof1"])
    resposta = api.put(
        "/profissionais/alterar-info-profissional", data={"dados": "{isto nao e json"}, headers=_auth(token)
    )
    assert 400 <= resposta.status_code < 500
    assert "Traceback" not in resposta.text and "File \"" not in resposta.text


def test_erro_de_validacao_nao_ecoa_stack_trace(api):
    resposta = api.post("/api/v1/auth/login", data="{quebrado", headers={"Content-Type": "application/json"})
    assert resposta.status_code == 422
    assert "Traceback" not in resposta.text
