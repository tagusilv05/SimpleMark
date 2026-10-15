# Testes do login em duas etapas: POST /auth/login (senha) e
# POST /auth/login/confirmar (código enviado por e-mail).
#
# O envio de e-mail é trocado por uma lista em memória: nenhum teste usa o SMTP.
import uuid
from datetime import date, timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from core.parametros import login_max_tentativas
from core.seguranca import gerar_hash_senha
from core.tempo import agora_utc
from dependencies.database import get_db
from dependencies.erros import registrar_erros
from models.acesso import CodigoLogin, Credencial
from models.models import Paciente, Usuario
from routers.auth import router as auth_router

SENHA = "Senha123"
EMAIL = "ana.teste@gmail.com"
CPF = "390.533.447-05"
ENVIO = "services.LoginService.codigo_login.enviar_codigo_login"


@pytest.fixture
def client_login(db):
    aplicacao = FastAPI()
    registrar_erros(aplicacao)
    aplicacao.include_router(auth_router, prefix="/api/v1")
    aplicacao.dependency_overrides[get_db] = lambda: db
    return TestClient(aplicacao)


@pytest.fixture
def emails(monkeypatch):
    """Lista de (destinatário, código) no lugar do envio real."""
    enviados: list[tuple[str, str]] = []
    monkeypatch.setattr(ENVIO, lambda destinatario, codigo: enviados.append((destinatario, codigo)))
    return enviados


@pytest.fixture
def conta(db):
    usuario = Usuario(
        id=uuid.uuid4(),
        nome="Ana Teste",
        cpf=CPF,
        orgao_emissor="SSP-PI",
        data_nascimento=date(1990, 1, 10),
        genero="feminino",
        telefone="86999990001",
        email=EMAIL,
        status=True,
    )
    db.add(usuario)
    db.flush()
    db.add(Paciente(id_usuario=usuario.id))
    db.add(Credencial(id_usuario=usuario.id, senha_hash=gerar_hash_senha(SENHA), consentimento_lgpd=True))
    db.commit()
    return usuario


def _login(client, senha=SENHA, identificador=EMAIL):
    return client.post("/api/v1/auth/login", json={"identificador": identificador, "senha": senha})


def _confirmar(client, id_desafio, codigo):
    return client.post(
        "/api/v1/auth/login/confirmar",
        json={"id_desafio": str(id_desafio), "codigo": codigo},
    )


def _pedir_codigo(client, emails) -> tuple[str, str]:
    resposta = _login(client)
    assert resposta.status_code == 200
    return resposta.json()["id_desafio"], emails[-1][1]


def _codigo_errado(codigo: str) -> str:
    return "000000" if codigo != "000000" else "111111"


def test_senha_correta_envia_codigo_e_nao_devolve_token(client_login, conta, emails):
    resposta = _login(client_login)

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert "access_token" not in corpo
    assert corpo["email_mascarado"] == "a***@gmail.com"
    assert corpo["expira_em_segundos"] == 300
    assert len(emails) == 1
    destinatario, codigo = emails[0]
    assert destinatario == EMAIL
    assert len(codigo) == 6 and codigo.isdigit()


def test_login_por_cpf_tambem_envia_codigo(client_login, conta, emails):
    resposta = _login(client_login, identificador="39053344705")

    assert resposta.status_code == 200
    assert emails[0][0] == EMAIL


def test_banco_guarda_so_o_hash_do_codigo(client_login, conta, emails, db):
    _id_desafio, codigo = _pedir_codigo(client_login, emails)

    registro = db.scalars(select(CodigoLogin)).one()
    assert registro.codigo_hash != codigo
    assert len(registro.codigo_hash) == 64


def test_senha_errada_nao_envia_codigo(client_login, conta, emails):
    resposta = _login(client_login, senha="SenhaErrada1")

    assert resposta.status_code == 401
    assert emails == []


def test_codigo_correto_abre_a_sessao(client_login, conta, emails):
    id_desafio, codigo = _pedir_codigo(client_login, emails)

    resposta = _confirmar(client_login, id_desafio, codigo)

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["token_type"] == "bearer"
    assert corpo["usuario"]["email"] == EMAIL
    eu = client_login.get(
        "/api/v1/auth/eu",
        headers={"Authorization": f"Bearer {corpo['access_token']}"},
    )
    assert eu.status_code == 200


def test_codigo_so_vale_uma_vez(client_login, conta, emails):
    id_desafio, codigo = _pedir_codigo(client_login, emails)
    assert _confirmar(client_login, id_desafio, codigo).status_code == 200

    segunda = _confirmar(client_login, id_desafio, codigo)

    assert segunda.status_code == 401
    assert "inválido" in segunda.json()["mensagem"]


def test_codigo_incorreto_nao_abre_sessao_e_o_certo_continua_valendo(client_login, conta, emails):
    id_desafio, codigo = _pedir_codigo(client_login, emails)

    errado = _confirmar(client_login, id_desafio, _codigo_errado(codigo))

    assert errado.status_code == 401
    assert "incorreto" in errado.json()["mensagem"]
    assert _confirmar(client_login, id_desafio, codigo).status_code == 200


def test_codigo_expirado_e_recusado(client_login, conta, emails, db):
    id_desafio, codigo = _pedir_codigo(client_login, emails)
    registro = db.get(CodigoLogin, uuid.UUID(id_desafio))
    registro.expira_em = agora_utc() - timedelta(seconds=1)
    db.commit()

    resposta = _confirmar(client_login, id_desafio, codigo)

    assert resposta.status_code == 401
    assert "expirou" in resposta.json()["mensagem"]
    # Entrando de novo, um código novo funciona.
    novo_id, novo_codigo = _pedir_codigo(client_login, emails)
    assert _confirmar(client_login, novo_id, novo_codigo).status_code == 200


def test_novo_login_invalida_o_codigo_anterior_e_nao_repete(client_login, conta, emails):
    primeiro_id, primeiro_codigo = _pedir_codigo(client_login, emails)
    segundo_id, segundo_codigo = _pedir_codigo(client_login, emails)

    assert primeiro_codigo != segundo_codigo
    antigo = _confirmar(client_login, primeiro_id, primeiro_codigo)
    assert antigo.status_code == 401
    assert _confirmar(client_login, segundo_id, segundo_codigo).status_code == 200


def test_codigos_errados_seguidos_bloqueiam_a_conta(client_login, conta, emails):
    id_desafio, codigo = _pedir_codigo(client_login, emails)
    errado = _codigo_errado(codigo)
    limite = login_max_tentativas()

    for _ in range(limite - 1):
        assert _confirmar(client_login, id_desafio, errado).status_code == 401
    assert _confirmar(client_login, id_desafio, errado).status_code == 429

    # Com a conta bloqueada, nem o código certo nem a senha servem.
    assert _confirmar(client_login, id_desafio, codigo).status_code == 429
    assert _login(client_login).status_code == 429


def test_acertar_a_senha_nao_zera_as_falhas(client_login, conta, emails):
    limite = login_max_tentativas()
    for _ in range(limite - 1):
        assert _login(client_login, senha="SenhaErrada1").status_code == 401

    assert _login(client_login).status_code == 200  # senha certa, sem confirmar o código
    assert _login(client_login, senha="SenhaErrada1").status_code == 429


def test_codigo_com_formato_invalido_responde_422(client_login, conta, emails):
    id_desafio, _codigo = _pedir_codigo(client_login, emails)

    curto = _confirmar(client_login, id_desafio, "12345")
    letras = _confirmar(client_login, id_desafio, "abc123")

    assert curto.status_code == 422
    assert "6 números" in curto.json()["mensagem"]
    assert letras.status_code == 422


def test_identificador_de_confirmacao_invalido_responde_422(client_login, conta):
    resposta = _confirmar(client_login, "isto-nao-e-um-uuid", "123456")

    assert resposta.status_code == 422
    assert "identificador" in resposta.json()["mensagem"]


def test_confirmacao_desconhecida_responde_401(client_login, conta):
    resposta = _confirmar(client_login, uuid.uuid4(), "123456")

    assert resposta.status_code == 401


def test_conta_inativa_nao_recebe_codigo(client_login, conta, emails, db):
    conta.status = False
    db.commit()

    resposta = _login(client_login)

    assert resposta.status_code == 403
    assert emails == []


def test_falha_no_envio_responde_503_e_nao_deixa_codigo_valido(client_login, conta, monkeypatch, db):
    def smtp_fora(_destinatario, _codigo):
        raise OSError("servidor de e-mail fora do ar")

    monkeypatch.setattr(ENVIO, smtp_fora)

    resposta = _login(client_login)

    assert resposta.status_code == 503
    assert db.scalar(select(func.count()).select_from(CodigoLogin)) == 0
