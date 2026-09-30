# Arquivo criado por Victor
from app.models.usuario import Usuario
from tests.apoio import CPF_ADMIN, dados_profissional, dados_usuario
from tests.conftest import AmbienteTeste


def test_cadastra_paciente_e_recusa_cpf_duplicado(ambiente: AmbienteTeste):
    """Cadastra um paciente e recusa o mesmo CPF em outro e-mail.

    Passo a passo:
    1. POST /cadastro/paciente e confere 201, perfil paciente, status ativo e ausência de senha.
    2. Repete o POST com outro e-mail e o mesmo CPF.
    3. Espera 409 e a mensagem citando o CPF.
    """
    resposta = ambiente.cliente.post("/api/v1/cadastro/paciente", json=dados_usuario())
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["perfil"] == "paciente"
    assert corpo["status"] is True
    assert corpo["id_paciente"] is not None
    assert "senha" not in corpo
    assert "senha_hash" not in corpo

    repetido = dados_usuario(email="outra@example.com", telefone="86911112222")
    duplicado = ambiente.cliente.post("/api/v1/cadastro/paciente", json=repetido)
    assert duplicado.status_code == 409
    assert "CPF" in duplicado.json()["mensagem"]


def test_rejeita_cpf_invalido_senha_curta_e_consentimento(ambiente: AmbienteTeste):
    """Recusa CPF inválido, senha curta e consentimento falso antes de gravar.

    Passo a passo:
    1. Envia CPF 111.111.111-11 e espera 422 falando de CPF.
    2. Envia senha com 3 caracteres e espera 422 falando de 8 caracteres.
    3. Envia consentimento falso e espera 422 falando de consentimento ou autorização.
    """
    invalido = dados_usuario(cpf="111.111.111-11")
    resposta = ambiente.cliente.post("/api/v1/cadastro/paciente", json=invalido)
    assert resposta.status_code == 422
    assert "CPF" in resposta.json()["mensagem"]

    curta = dados_usuario()
    curta["senha"] = "123"
    resposta = ambiente.cliente.post("/api/v1/cadastro/paciente", json=curta)
    assert resposta.status_code == 422
    assert "8 caracteres" in resposta.json()["mensagem"]

    sem_consentimento = dados_usuario()
    sem_consentimento["consentimento_lgpd"] = False
    resposta = ambiente.cliente.post("/api/v1/cadastro/paciente", json=sem_consentimento)
    assert resposta.status_code == 422
    assert "consentimento" in resposta.json()["mensagem"].lower() or "autorizar" in resposta.json()["mensagem"]


def test_profissional_nasce_inativo_e_guarda_conselho_unico(ambiente: AmbienteTeste):
    """Profissional de saúde entra inativo e o mesmo número de conselho não pode repetir.

    Passo a passo:
    1. Cadastra o profissional e confere 201, perfil profissional e status falso.
    2. Cadastra outra pessoa com o mesmo número de conselho.
    3. Espera 409 e a mensagem citando o conselho.
    """
    resposta = ambiente.cliente.post("/api/v1/cadastro/profissional", json=dados_profissional())
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["perfil"] == "profissional"
    assert corpo["status"] is False

    repetido = dados_profissional(
        nome="Ana Souza",
        email="ana@example.com",
        cpf=CPF_ADMIN,
        telefone="86933334444",
        numero_conselho="123456",
    )
    conflito = ambiente.cliente.post("/api/v1/cadastro/profissional", json=repetido)
    assert conflito.status_code == 409
    assert "conselho" in conflito.json()["mensagem"]


def test_senha_fica_com_hash_argon2(ambiente: AmbienteTeste):
    """Confere que o banco guarda o hash Argon2 e o consentimento, nunca a senha pura.

    Passo a passo:
    1. Cadastra o paciente.
    2. Lê a única linha de usuario no SQLite do teste.
    3. O hash precisa começar com $argon2 e o consentimento precisa estar verdadeiro.
    """
    ambiente.cliente.post("/api/v1/cadastro/paciente", json=dados_usuario())
    db = ambiente.sessoes()
    try:
        usuario = db.query(Usuario).one()
        assert usuario.senha_hash.startswith("$argon2")
        assert usuario.consentimento_lgpd is True
        assert usuario.endereco.cep == "64000000"
        assert usuario.endereco.endereco == "Rua das Laranjeiras, 100, Teresina"
        assert usuario.cpf == "52998224725"
    finally:
        db.close()


def test_nao_existe_cadastro_de_administrador(ambiente: AmbienteTeste):
    """O administrador entra direto no banco. A rota de cadastro não existe.

    Passo a passo:
    1. Envia um POST para /cadastro/administrador.
    2. Espera 404, porque essa rota não foi registrada.
    """
    resposta = ambiente.cliente.post("/api/v1/cadastro/administrador", json=dados_usuario(cpf=CPF_ADMIN))
    assert resposta.status_code == 404
