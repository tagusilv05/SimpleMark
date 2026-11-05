"""Testes da área "Minha conta" (rotas /usuario e /profissionais) como o frontend usa."""

import io
from datetime import date, time, timedelta

import pytest

from core.seguranca import gerar_hash_senha, verificar_senha
from dependencies.autenticacao import usuario_atual
from models.acesso import Credencial
from models.administracao import LogAcaoAdministrador
from models.models import (
    Administrador,
    Avaliacao,
    Consulta,
    DocumentoClinico,
    Endereco,
    Especialidade,
    InfoConselho,
    Profissional,
    ProfissionalEspecialidade,
    Receita,
    Usuario,
)
from routers.porfissional_minha_conta import router as profissional_router
from routers.usuario_minha_conta import router as usuario_router
from services import porfissional_minha_conta as servico_profissional


@pytest.fixture
def chaves_estrangeiras(engine):
    """Liga a checagem de FK do SQLite, como no PostgreSQL."""
    conexao = engine.raw_connection()
    conexao.driver_connection.execute("PRAGMA foreign_keys=ON")
    conexao.close()


@pytest.fixture
def conta(app, client):
    """Cliente com as rotas da conta e uma função para logar um usuário."""
    app.include_router(usuario_router, prefix="/usuario")
    app.include_router(profissional_router, prefix="/profissionais")

    def logar(usuario):
        app.dependency_overrides[usuario_atual] = lambda: usuario
        return usuario

    yield client, logar
    app.dependency_overrides.pop(usuario_atual, None)


@pytest.fixture
def paciente(db, cenario):
    usuario = db.get(Usuario, cenario["paciente"].id_usuario)
    db.add(Endereco(id_usuario=usuario.id, cep="64000-000", cidade="Teresina", logradouro="Rua A", numero="S/N", bairro="Centro"))
    db.add(Credencial(id_usuario=usuario.id, senha_hash=gerar_hash_senha("SenhaAntiga1")))
    db.commit()
    return usuario


def _profissional(db, cenario, n=1):
    return db.get(Usuario, cenario["profissionais"][n].id_usuario)


# ---------- Usuário ----------


def test_rotas_exigem_login(conta, paciente):
    client, _ = conta
    assert client.get(f"/usuario/buscar-info-usuario/{paciente.id}").status_code == 401


def test_nao_acessa_conta_de_outro(conta, db, cenario, paciente):
    client, logar = conta
    logar(_profissional(db, cenario))
    assert client.get(f"/usuario/buscar-info-usuario/{paciente.id}").status_code == 403
    resposta = client.put("/usuario/altera-info-pessoal", json={"id": str(paciente.id), "nome": "Invasor"})
    assert resposta.status_code == 403


def test_le_dados_e_endereco_sem_complemento(conta, paciente):
    client, logar = conta
    logar(paciente)

    dados = client.get(f"/usuario/buscar-info-usuario/{paciente.id}")
    endereco = client.get(f"/usuario/buscar-info-endereco/{paciente.id}")

    assert dados.status_code == 200 and dados.json()["nome"] == "Paciente 1"
    assert endereco.status_code == 200, endereco.text
    assert endereco.json()["numero"] == "S/N"
    assert endereco.json()["complemento"] is None


def test_altera_dados_pessoais_e_endereco(conta, db, paciente):
    client, logar = conta
    logar(paciente)

    r1 = client.put(
        "/usuario/altera-info-pessoal",
        json={"id": str(paciente.id), "nome": "Paciente Novo", "email": "NOVO@Email.com", "telefone": "(86) 99999-1234"},
    )
    r2 = client.put(
        "/usuario/altera-endereco",
        json={"id_usuario": str(paciente.id), "cep": "64001000", "numero": "120-A", "complemento": "Apto 2"},
    )

    assert r1.status_code == 200, r1.text
    assert r1.json() == {"nome": "Paciente Novo", "email": "novo@email.com", "telefone": "86999991234"}
    assert r2.status_code == 200, r2.text
    assert r2.json()["cep"] == "64001-000" and r2.json()["numero"] == "120-A"


def test_email_de_outra_conta_responde_409(conta, db, cenario, paciente):
    client, logar = conta
    logar(paciente)
    resposta = client.put(
        "/usuario/altera-info-pessoal", json={"id": str(paciente.id), "email": "profissional1@email.com"}
    )
    assert resposta.status_code == 409


def test_altera_senha(conta, db, paciente):
    client, logar = conta
    logar(paciente)

    errada = client.put("/usuario/alterar-senha", json={"senha_atual": "errada123", "nova_senha": "SenhaNova@1"})
    certa = client.put("/usuario/alterar-senha", json={"senha_atual": "SenhaAntiga1", "nova_senha": "SenhaNova@1"})

    assert errada.status_code == 400
    assert certa.status_code == 200, certa.text
    db.expire_all()
    assert verificar_senha("SenhaNova@1", db.get(Credencial, paciente.id).senha_hash)[0]


def test_inativa_conta(conta, db, paciente):
    client, logar = conta
    logar(paciente)
    resposta = client.patch("/usuario/inativar-usuario", params={"id_usuario": str(paciente.id)})
    assert resposta.status_code == 200
    db.expire_all()
    assert db.get(Usuario, paciente.id).status is False


def test_nao_exclui_com_consulta_futura(conta, db, cenario, paciente):
    client, logar = conta
    logar(paciente)
    base = cenario["consultas"][1]
    db.add(Consulta(id_paciente=base.id_paciente, id_esp_prof=base.id_esp_prof, data=date.today() + timedelta(days=3),
                    hora=time(10, 0), tipo="consulta", status="agendada", valor=100))
    db.commit()

    resposta = client.request("DELETE", "/usuario/excluir-usuario", json={"id": str(paciente.id), "tipo": "paciente"})
    assert resposta.status_code == 409


def test_exclui_paciente_com_historico(conta, db, cenario, paciente, chaves_estrangeiras):
    client, logar = conta
    logar(paciente)
    consulta = cenario["consultas"][1]
    documento = DocumentoClinico(id_consulta=consulta.id_consulta, tipo=True)
    db.add(documento)
    db.flush()
    db.add(Receita(id_documento=documento.id_documento))
    db.add(Avaliacao(id_consulta=consulta.id_consulta, nota=5, avaliacao=5, data=date.today(), hora=time(9, 0)))
    db.commit()
    id_usuario = paciente.id

    resposta = client.request("DELETE", "/usuario/excluir-usuario", json={"id": str(id_usuario), "tipo": "paciente"})

    assert resposta.status_code == 200, resposta.text
    db.expire_all()
    assert db.get(Usuario, id_usuario) is None


# ---------- Profissional ----------


def _form(id_usuario, especialidades, info="Cardiologista"):
    import json

    return {"dados": json.dumps({"id_usuario": str(id_usuario), "info_profissional": info, "especialidade": especialidades})}


def test_salvar_especialidade_existente_atualiza_sem_duplicar(conta, db, cenario):
    client, logar = conta
    usuario = logar(_profissional(db, cenario))
    [vinculo] = cenario["profissionais"][1].especialidades
    conselho_original = vinculo.id_conselho  # o cenário usa o mesmo conselho nos dois profissionais

    resposta = client.put(
        "/profissionais/alterar-info-profissional",
        data=_form(usuario.id, [{"id_especialidade": vinculo.id_especialidade, "numero_conselho": "999", "conselho": "CRM-PI", "valor": 250}]),
    )

    assert resposta.status_code == 200, resposta.text
    db.expire_all()
    vinculos = db.query(ProfissionalEspecialidade).filter_by(id_profissional=cenario["profissionais"][1].id_profissional).all()
    assert len(vinculos) == 1
    assert vinculos[0].valor_consulta == 250
    assert vinculos[0].conselho.numero_conselho == "999"
    # O conselho antigo continua existindo: o profissional 2 também o usa
    assert vinculos[0].id_conselho != conselho_original
    assert db.get(InfoConselho, conselho_original).numero_conselho == "12345"


def test_adiciona_nova_especialidade(conta, db, cenario):
    client, logar = conta
    usuario = logar(_profissional(db, cenario))
    nova = Especialidade(especialidade="Pediatria")
    db.add(nova)
    db.commit()

    resposta = client.put(
        "/profissionais/alterar-info-profissional",
        data=_form(usuario.id, [{"id_especialidade": nova.id_especialidade, "numero_conselho": "1234", "conselho": "CRM-PI", "valor": 180}]),
    )

    assert resposta.status_code == 200, resposta.text
    info = client.get(f"/profissionais/buscar-info-profissional/{usuario.id}").json()
    assert {e["nome"] for e in info["especialidade"]} == {"Cardiologia", "Pediatria"}
    assert info["info_profissional"] == "Cardiologista"


def test_profissional_nao_altera_outro(conta, db, cenario):
    client, logar = conta
    logar(_profissional(db, cenario, 2))
    outro = _profissional(db, cenario, 1)
    resposta = client.put("/profissionais/alterar-info-profissional", data=_form(outro.id, []))
    assert resposta.status_code == 403


def test_nao_remove_especialidade_com_consultas(conta, db, cenario):
    client, logar = conta
    usuario = logar(_profissional(db, cenario))
    [vinculo] = cenario["profissionais"][1].especialidades

    resposta = client.request(
        "DELETE", "/profissionais/excluir-especialidade",
        json={"id_usuario": str(usuario.id), "id_especialidade": vinculo.id_especialidade},
    )
    assert resposta.status_code == 409


def test_remove_especialidade_mantem_conselho_compartilhado(conta, db, cenario, chaves_estrangeiras):
    client, logar = conta
    usuario = logar(_profissional(db, cenario))
    profissional = cenario["profissionais"][1]
    [vinculo] = profissional.especialidades
    extra = Especialidade(especialidade="Clínica Geral")
    db.add(extra)
    db.flush()
    # Mesmo conselho para as duas especialidades, como o cadastro faz
    db.add(ProfissionalEspecialidade(id_profissional=profissional.id_profissional, id_especialidade=extra.id_especialidade,
                                     id_conselho=vinculo.id_conselho, valor_consulta=100))
    db.commit()

    resposta = client.request(
        "DELETE", "/profissionais/excluir-especialidade",
        json={"id_usuario": str(usuario.id), "id_especialidade": extra.id_especialidade},
    )

    assert resposta.status_code == 200, resposta.text
    db.expire_all()
    assert db.get(InfoConselho, vinculo.id_conselho) is not None


def test_foto_aceita_so_imagem(conta, db, cenario, tmp_path, monkeypatch):
    client, logar = conta
    usuario = logar(_profissional(db, cenario))
    monkeypatch.setattr(servico_profissional, "PASTA_IMAGENS", tmp_path)

    texto = client.post("/profissionais/salvar-imagem-profissional", data={"id_usuario": str(usuario.id)},
                        files={"imagem": ("a.txt", io.BytesIO(b"x"), "text/plain")})
    foto = client.post("/profissionais/salvar-imagem-profissional", data={"id_usuario": str(usuario.id)},
                       files={"imagem": ("a.png", io.BytesIO(b"png"), "image/png")})

    assert texto.status_code == 400
    assert foto.status_code == 200, foto.text
    assert len(list(tmp_path.iterdir())) == 1


def test_exclui_profissional_validado(conta, db, cenario, chaves_estrangeiras):
    client, logar = conta
    usuario = logar(_profissional(db, cenario))
    admin_usuario = _profissional(db, cenario, 2)
    admin = Administrador(id_usuario=admin_usuario.id)
    db.add(admin)
    db.flush()
    db.add(LogAcaoAdministrador(id_administrador=admin.id_administrador, acao="validar_profissional",
                                alvo_tipo="profissional", alvo_id=1, id_usuario_alvo=usuario.id,
                                realizada_em=date.today()))
    db.commit()
    id_usuario = usuario.id

    resposta = client.request("DELETE", "/usuario/excluir-usuario", json={"id": str(id_usuario), "tipo": "profissional"})

    assert resposta.status_code == 200, resposta.text
    db.expire_all()
    assert db.get(Usuario, id_usuario) is None
    assert db.query(Profissional).filter_by(id_usuario=id_usuario).first() is None
