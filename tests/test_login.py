# Arquivo criado por Victor
from tests.apoio import CPF_MARIA, SENHA, dados_profissional, dados_usuario
from tests.conftest import AmbienteTeste, autorizar, entrar, gravar_administrador


def test_login_por_email_e_por_cpf(ambiente: AmbienteTeste):
    """Entra com e-mail, sem diferenciar maiúsculas, e também com o CPF mascarado.

    Passo a passo:
    1. Cadastra a paciente.
    2. Login com Maria@Example.com e confere o token bearer e o perfil.
    3. Login com o CPF pontuado e confere os 11 dígitos gravados.
    """
    ambiente.cliente.post("/api/v1/cadastro/paciente", json=dados_usuario())
    por_email = entrar(ambiente, "Maria@Example.com")
    assert por_email["token_type"] == "bearer"
    assert por_email["usuario"]["perfil"] == "paciente"
    assert "expira_em" not in por_email

    por_cpf = entrar(ambiente, "529.982.247-25")
    assert por_cpf["usuario"]["cpf"] == CPF_MARIA


def test_senha_errada_continua_generica(ambiente: AmbienteTeste):
    """Senha errada, mesmo repetida, responde a mesma frase. Não há bloqueio aqui.

    Passo a passo:
    1. Cadastra a paciente.
    2. Erra a senha seis vezes e espera 401 com "incorretos".
    3. A senha correta ainda entra com 200.
    """
    ambiente.cliente.post("/api/v1/cadastro/paciente", json=dados_usuario())
    for _ in range(6):
        resposta = ambiente.cliente.post(
            "/api/v1/auth/login",
            json={"identificador": "maria@example.com", "senha": "Errada123"},
        )
        assert resposta.status_code == 401
        assert "incorretos" in resposta.json()["mensagem"]

    certa = entrar(ambiente, "maria@example.com", SENHA)
    assert certa["usuario"]["perfil"] == "paciente"


def test_usuario_inexistente_nao_revela_a_conta(ambiente: AmbienteTeste):
    """Login de e-mail que não existe usa a mesma frase de senha errada.

    Passo a passo:
    1. Não cadastra ninguém.
    2. Tenta entrar com ninguem@example.com.
    3. Espera 401 e a palavra "incorretos", sem dizer que a conta não existe.
    """
    resposta = ambiente.cliente.post(
        "/api/v1/auth/login",
        json={"identificador": "ninguem@example.com", "senha": SENHA},
    )
    assert resposta.status_code == 401
    assert "incorretos" in resposta.json()["mensagem"]


def test_autentica_paciente_profissional_e_administrador(ambiente: AmbienteTeste):
    """O token identifica os três perfis em /auth/eu.

    Passo a passo:
    1. Cadastra paciente e profissional de saúde.
    2. Insere o administrador direto no banco e valida o profissional.
    3. Cada login chama /auth/eu e confere o perfil.
    4. Sem token, a mesma rota responde 401.
    """
    ambiente.cliente.post("/api/v1/cadastro/paciente", json=dados_usuario())
    criado = ambiente.cliente.post("/api/v1/cadastro/profissional", json=dados_profissional())
    assert criado.status_code == 201
    gravar_administrador(ambiente)
    token_admin = entrar(ambiente, "admin@example.com")["access_token"]
    validacao = ambiente.cliente.post(
        f"/api/v1/administracao/profissionais/{criado.json()['id_profissional']}/validar",
        headers=autorizar(token_admin),
    )
    assert validacao.status_code == 200, validacao.json()

    for identificador, perfil in (
        ("maria@example.com", "paciente"),
        ("joao@example.com", "profissional"),
        ("admin@example.com", "administrador"),
    ):
        token = entrar(ambiente, identificador)["access_token"]
        eu = ambiente.cliente.get("/api/v1/auth/eu", headers=autorizar(token))
        assert eu.status_code == 200, eu.json()
        assert eu.json()["perfil"] == perfil

    sem_token = ambiente.cliente.get("/api/v1/auth/eu")
    assert sem_token.status_code == 401


def test_profissional_so_entra_depois_da_validacao(ambiente: AmbienteTeste):
    """O profissional de saúde não entra enquanto o administrador não validar.

    Passo a passo:
    1. Cadastra o profissional e tenta o login. Espera 403.
    2. O administrador lista os pendentes e valida o id.
    3. O mesmo login passa com 200.
    4. O paciente não consegue chamar a lista de pendentes.
    """
    ambiente.cliente.post("/api/v1/cadastro/paciente", json=dados_usuario())
    ambiente.cliente.post("/api/v1/cadastro/profissional", json=dados_profissional())
    gravar_administrador(ambiente)

    bloqueado = ambiente.cliente.post(
        "/api/v1/auth/login",
        json={"identificador": "joao@example.com", "senha": SENHA},
    )
    assert bloqueado.status_code == 403
    assert "administrador" in bloqueado.json()["mensagem"]

    token_admin = entrar(ambiente, "admin@example.com")["access_token"]
    pendentes = ambiente.cliente.get(
        "/api/v1/administracao/profissionais/pendentes",
        headers=autorizar(token_admin),
    )
    assert pendentes.status_code == 200
    assert len(pendentes.json()) == 1
    id_profissional = pendentes.json()[0]["id_profissional"]

    validacao = ambiente.cliente.post(
        f"/api/v1/administracao/profissionais/{id_profissional}/validar",
        headers=autorizar(token_admin),
    )
    assert validacao.status_code == 200
    assert validacao.json()["status"] is True

    liberado = entrar(ambiente, "joao@example.com")
    assert liberado["usuario"]["perfil"] == "profissional"

    token_paciente = entrar(ambiente, "maria@example.com")["access_token"]
    proibido = ambiente.cliente.get(
        "/api/v1/administracao/profissionais/pendentes",
        headers=autorizar(token_paciente),
    )
    assert proibido.status_code == 403
