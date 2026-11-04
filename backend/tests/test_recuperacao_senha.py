# Testes da recuperação de senha em duas etapas: POST /auth/senha/esqueci (e-mail)
# e POST /auth/senha/redefinir (código do e-mail + nova senha).
#
# O envio de e-mail é trocado por uma lista em memória: nenhum teste usa o SMTP.
"""Testes da recuperação de senha: pedir o código por e-mail e redefinir."""
import uuid
from datetime import date, timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select

from core.parametros import login_max_tentativas
from core.seguranca import gerar_hash_senha, verificar_senha
from core.tempo import agora_utc
from dependencies.database import get_db
from dependencies.erros import registrar_erros
from models.acesso import CodigoLogin, Credencial, SessaoLogin
from models.models import Paciente, Usuario
from models.recuperacao_senha import CodigoRecuperacaoSenha
from routers.auth import router as auth_router
from routers.recuperacao_senha import router as recuperacao_router
from services.SessaoService.sessao import ServicoSessao

SENHA = "Senha123"
NOVA_SENHA = "NovaSenha456"
EMAIL = "bia.teste@gmail.com"
CPF = "390.533.447-05"
ENVIO = "services.RecuperacaoService.recuperacao_senha.enviar_codigo_recuperacao"


@pytest.fixture
def client_recuperacao(db):
    """Cliente de teste de um app só com os routers de autenticação e recuperação."""
    aplicacao = FastAPI()
    registrar_erros(aplicacao)
    aplicacao.include_router(auth_router, prefix="/api/v1")
    aplicacao.include_router(recuperacao_router, prefix="/api/v1")
    aplicacao.dependency_overrides[get_db] = lambda: db
    return TestClient(aplicacao)


@pytest.fixture
def emails(monkeypatch):
    """Lista de (destinatário, código) no lugar do envio real."""
    enviados: list[tuple[str, str]] = []
    monkeypatch.setattr(
        ENVIO,
        lambda destinatario, codigo, validade_minutos: enviados.append((destinatario, codigo)),
    )
    return enviados


@pytest.fixture
def conta(db):
    """Cria um paciente ativo com senha cadastrada."""
    usuario = Usuario(
        id=uuid.uuid4(),
        nome="Bia Teste",
        cpf=CPF,
        orgao_emissor="SSP-PI",
        data_nascimento=date(1990, 1, 10),
        genero="feminino",
        telefone="86999990002",
        email=EMAIL,
        status=True,
    )
    db.add(usuario)
    db.flush()
    db.add(Paciente(id_usuario=usuario.id))
    db.add(Credencial(id_usuario=usuario.id, senha_hash=gerar_hash_senha(SENHA), consentimento_lgpd=True))
    db.commit()
    return usuario


def _esqueci(client, email=EMAIL):
    """Envia a primeira etapa (e-mail)."""
    return client.post("/api/v1/auth/senha/esqueci", json={"email": email})


def _redefinir(client, id_desafio, codigo, nova_senha=NOVA_SENHA):
    """Envia a segunda etapa (código e nova senha)."""
    return client.post(
        "/api/v1/auth/senha/redefinir",
        json={"id_desafio": str(id_desafio), "codigo": codigo, "nova_senha": nova_senha},
    )


def _pedir_codigo(client, emails) -> tuple[str, str]:
    """Pede o código e devolve o id do desafio e o código enviado."""
    resposta = _esqueci(client)
    assert resposta.status_code == 200
    return resposta.json()["id_desafio"], emails[-1][1]


def _codigo_errado(codigo: str) -> str:
    """Devolve um código de 6 dígitos diferente do informado."""
    return "000000" if codigo != "000000" else "111111"


def _senha_atual_confere(db, usuario, senha) -> bool:
    """Confere a senha gravada no banco para a conta."""
    db.expire_all()
    credencial = db.get(Credencial, usuario.id)
    return verificar_senha(senha, credencial.senha_hash)[0]


def test_pedido_envia_codigo_ao_email_da_conta(client_recuperacao, conta, emails):
    """E-mail de uma conta envia código de 6 dígitos e devolve o desafio."""
    resposta = _esqueci(client_recuperacao)

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["email_mascarado"] == "b***@gmail.com"
    assert corpo["expira_em_segundos"] == 600
    assert len(emails) == 1
    destinatario, codigo = emails[0]
    assert destinatario == EMAIL
    assert len(codigo) == 6 and codigo.isdigit()


def test_email_com_maiusculas_e_espacos_acha_a_conta(client_recuperacao, conta, emails):
    """O e-mail é normalizado antes da busca."""
    resposta = _esqueci(client_recuperacao, email="  BIA.Teste@Gmail.com ")

    assert resposta.status_code == 200
    assert emails[0][0] == EMAIL


def test_banco_guarda_so_o_hash_do_codigo(client_recuperacao, conta, emails, db):
    """O banco guarda só o hash do código, nunca o código em claro."""
    _id_desafio, codigo = _pedir_codigo(client_recuperacao, emails)

    registro = db.scalars(select(CodigoRecuperacaoSenha)).one()
    assert registro.codigo_hash != codigo
    assert len(registro.codigo_hash) == 64


def test_email_sem_conta_responde_igual_e_nao_envia(client_recuperacao, conta, emails):
    """Quem não tem conta recebe a mesma resposta 200, sem e-mail enviado."""
    resposta = _esqueci(client_recuperacao, email="ninguem@gmail.com")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["email_mascarado"] == "n***@gmail.com"
    assert corpo["expira_em_segundos"] == 600
    assert emails == []
    # O id devolvido não vale para nada.
    falso = _redefinir(client_recuperacao, corpo["id_desafio"], "123456")
    assert falso.status_code == 400
    assert "inválido" in falso.json()["mensagem"]


def test_email_invalido_responde_422(client_recuperacao, emails):
    """E-mail mal formatado responde 422."""
    resposta = _esqueci(client_recuperacao, email="isso-nao-e-email")

    assert resposta.status_code == 422
    assert emails == []


def test_falha_no_envio_responde_503_e_nao_guarda_codigo(client_recuperacao, conta, monkeypatch, db):
    """Se o e-mail não sai, a API responde 503 e nenhum código fica gravado."""

    def _falha(destinatario, codigo, validade_minutos):
        """Simula o servidor SMTP fora do ar."""
        raise OSError("sem rede")

    monkeypatch.setattr(ENVIO, _falha)

    resposta = _esqueci(client_recuperacao)

    assert resposta.status_code == 503
    assert db.scalars(select(CodigoRecuperacaoSenha)).all() == []


def test_codigo_correto_troca_a_senha(client_recuperacao, conta, emails, db):
    """Código certo grava a nova senha; a antiga deixa de valer."""
    id_desafio, codigo = _pedir_codigo(client_recuperacao, emails)

    resposta = _redefinir(client_recuperacao, id_desafio, codigo)

    assert resposta.status_code == 200
    assert "redefinida" in resposta.json()["mensagem"]
    assert _senha_atual_confere(db, conta, NOVA_SENHA)
    assert not _senha_atual_confere(db, conta, SENHA)


def test_depois_de_trocar_o_login_pede_a_senha_nova(client_recuperacao, conta, emails, db, monkeypatch):
    """A senha antiga é recusada no login (401) e a nova é aceita (200)."""
    id_desafio, codigo = _pedir_codigo(client_recuperacao, emails)
    assert _redefinir(client_recuperacao, id_desafio, codigo).status_code == 200
    monkeypatch.setattr(
        "services.LoginService.codigo_login.enviar_codigo_login",
        lambda destinatario, codigo: None,
    )

    antiga = client_recuperacao.post(
        "/api/v1/auth/login", json={"identificador": EMAIL, "senha": SENHA}
    )
    nova = client_recuperacao.post(
        "/api/v1/auth/login", json={"identificador": EMAIL, "senha": NOVA_SENHA}
    )

    assert antiga.status_code == 401
    assert nova.status_code == 200


def test_codigo_so_vale_uma_vez(client_recuperacao, conta, emails):
    """Código já usado é recusado na segunda tentativa."""
    id_desafio, codigo = _pedir_codigo(client_recuperacao, emails)
    assert _redefinir(client_recuperacao, id_desafio, codigo).status_code == 200

    segunda = _redefinir(client_recuperacao, id_desafio, codigo, nova_senha="OutraSenha789")

    assert segunda.status_code == 400
    assert "inválido" in segunda.json()["mensagem"]


def test_codigo_incorreto_nao_troca_e_o_certo_continua_valendo(client_recuperacao, conta, emails, db):
    """Código errado é recusado e o certo continua valendo."""
    id_desafio, codigo = _pedir_codigo(client_recuperacao, emails)

    errado = _redefinir(client_recuperacao, id_desafio, _codigo_errado(codigo))

    assert errado.status_code == 400
    assert "incorreto" in errado.json()["mensagem"]
    assert _senha_atual_confere(db, conta, SENHA)
    assert _redefinir(client_recuperacao, id_desafio, codigo).status_code == 200


def test_codigo_expirado_e_recusado(client_recuperacao, conta, emails, db):
    """Código expirado é recusado; pedindo de novo, um código novo funciona."""
    id_desafio, codigo = _pedir_codigo(client_recuperacao, emails)
    registro = db.get(CodigoRecuperacaoSenha, uuid.UUID(id_desafio))
    registro.expira_em = agora_utc() - timedelta(seconds=1)
    registro.criado_em = agora_utc() - timedelta(minutes=11)
    db.commit()

    resposta = _redefinir(client_recuperacao, id_desafio, codigo)

    assert resposta.status_code == 400
    assert "expirou" in resposta.json()["mensagem"]
    novo_id, novo_codigo = _pedir_codigo(client_recuperacao, emails)
    assert _redefinir(client_recuperacao, novo_id, novo_codigo).status_code == 200


def test_pedir_de_novo_logo_em_seguida_nao_reenvia_o_email(client_recuperacao, conta, emails):
    """Dois pedidos em menos de 1 minuto mandam um só e-mail e devolvem o mesmo desafio."""
    primeiro_id, codigo = _pedir_codigo(client_recuperacao, emails)

    segundo = _esqueci(client_recuperacao)

    assert segundo.status_code == 200
    assert segundo.json()["id_desafio"] == primeiro_id
    assert len(emails) == 1
    assert _redefinir(client_recuperacao, primeiro_id, codigo).status_code == 200


def test_pedido_depois_do_intervalo_gera_codigo_novo_e_invalida_o_anterior(
    client_recuperacao, conta, emails, db
):
    """Passado o intervalo, um novo pedido envia outro código e o anterior deixa de valer."""
    primeiro_id, primeiro_codigo = _pedir_codigo(client_recuperacao, emails)
    registro = db.get(CodigoRecuperacaoSenha, uuid.UUID(primeiro_id))
    registro.criado_em = agora_utc() - timedelta(minutes=2)
    db.commit()

    segundo_id, segundo_codigo = _pedir_codigo(client_recuperacao, emails)

    assert segundo_id != primeiro_id
    assert primeiro_codigo != segundo_codigo
    assert len(emails) == 2
    antigo = _redefinir(client_recuperacao, primeiro_id, primeiro_codigo)
    assert antigo.status_code == 400
    assert _redefinir(client_recuperacao, segundo_id, segundo_codigo).status_code == 200


def test_codigos_errados_seguidos_bloqueiam_a_conta(client_recuperacao, conta, emails, db):
    """Cinco códigos errados bloqueiam a conta (429), até com o código certo."""
    id_desafio, codigo = _pedir_codigo(client_recuperacao, emails)
    errado = _codigo_errado(codigo)

    respostas = [
        _redefinir(client_recuperacao, id_desafio, errado).status_code
        for _ in range(login_max_tentativas())
    ]

    assert respostas[:-1] == [400] * (login_max_tentativas() - 1)
    assert respostas[-1] == 429
    certo = _redefinir(client_recuperacao, id_desafio, codigo)
    assert certo.status_code in (400, 429)
    assert _senha_atual_confere(db, conta, SENHA)


def test_senha_igual_a_atual_e_recusada_sem_gastar_o_codigo(client_recuperacao, conta, emails, db):
    """Repetir a senha atual responde 400 e o código continua valendo."""
    id_desafio, codigo = _pedir_codigo(client_recuperacao, emails)

    igual = _redefinir(client_recuperacao, id_desafio, codigo, nova_senha=SENHA)

    assert igual.status_code == 400
    assert "diferente" in igual.json()["mensagem"]
    assert _redefinir(client_recuperacao, id_desafio, codigo).status_code == 200
    assert _senha_atual_confere(db, conta, NOVA_SENHA)


def test_senha_curta_responde_422(client_recuperacao, conta, emails, db):
    """Nova senha com menos de 8 caracteres responde 422 e não troca nada."""
    id_desafio, codigo = _pedir_codigo(client_recuperacao, emails)

    resposta = _redefinir(client_recuperacao, id_desafio, codigo, nova_senha="curta")

    assert resposta.status_code == 422
    assert "mínimo 8" in resposta.json()["mensagem"]
    assert _senha_atual_confere(db, conta, SENHA)


def test_codigo_com_formato_errado_responde_422(client_recuperacao, conta, emails):
    """Código com letras ou tamanho errado responde 422."""
    id_desafio, _codigo = _pedir_codigo(client_recuperacao, emails)

    assert _redefinir(client_recuperacao, id_desafio, "12345").status_code == 422
    assert _redefinir(client_recuperacao, id_desafio, "12a456").status_code == 422


def test_trocar_a_senha_encerra_as_sessoes_abertas(client_recuperacao, conta, emails, db):
    """Ao redefinir, as sessões de login abertas da conta são encerradas."""
    sessao = ServicoSessao(db).abrir(conta.id)
    id_desafio, codigo = _pedir_codigo(client_recuperacao, emails)

    assert _redefinir(client_recuperacao, id_desafio, codigo).status_code == 200

    db.expire_all()
    assert db.get(SessaoLogin, sessao.id).encerrada_em is not None


def test_trocar_a_senha_zera_o_bloqueio_e_invalida_codigo_de_login_pendente(
    client_recuperacao, conta, emails, db
):
    """Ao redefinir, o contador de falhas zera e códigos de login pendentes são encerrados."""
    credencial = db.get(Credencial, conta.id)
    credencial.tentativas_login_falhas = 3
    pendente = CodigoLogin(
        id_usuario=conta.id,
        codigo_hash="a" * 64,
        criado_em=agora_utc(),
        expira_em=agora_utc() + timedelta(minutes=5),
    )
    db.add(pendente)
    db.commit()
    id_desafio, codigo = _pedir_codigo(client_recuperacao, emails)

    assert _redefinir(client_recuperacao, id_desafio, codigo).status_code == 200

    db.expire_all()
    assert db.get(Credencial, conta.id).tentativas_login_falhas == 0
    assert db.get(CodigoLogin, pendente.id).encerrado_em is not None


def test_codigo_de_login_nao_serve_para_recuperar(client_recuperacao, conta, emails, db, monkeypatch):
    """O hash do código de login não confere com o desafio de recuperação."""
    from core.seguranca import calcular_hash_codigo_login
    from services.RecuperacaoService.recuperacao_senha import calcular_hash_codigo

    assert calcular_hash_codigo_login(conta.id, "123456") != calcular_hash_codigo(conta.id, "123456")