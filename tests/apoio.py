# Arquivo criado por Victor
"""Dados usados pelos testes de autenticação."""

SENHA = "Senha123"


def gerar_cpf(nove_digitos: str) -> str:
    """Calcula os dois dígitos verificadores e devolve o CPF com 11 números.

    Passo a passo:
    1. digito multiplica cada número por um peso decrescente e usa o resto de 11.
    2. O primeiro dígito sai dos 9 números.
    3. O segundo sai dos 9 mais o primeiro.
    4. A função devolve a base mais os dois dígitos.
    """
    def digito(base: str) -> str:
        soma = sum(int(numero) * peso for numero, peso in zip(base, range(len(base) + 1, 1, -1)))
        resto = soma % 11
        if resto < 2:
            return "0"
        return str(11 - resto)

    primeiro = digito(nove_digitos)
    segundo = digito(nove_digitos + primeiro)
    return nove_digitos + primeiro + segundo


CPF_MARIA = gerar_cpf("529982247")
CPF_JOAO = gerar_cpf("390533447")
CPF_ADMIN = gerar_cpf("111444777")

assert CPF_MARIA == "52998224725"


def endereco() -> dict:
    """Devolve CEP e o endereço em um único texto, para o JSON de cadastro."""
    return {
        "cep": "64000-000",
        "endereco": "Rua das Laranjeiras, 100, Teresina",
    }


def dados_usuario(
    *,
    nome: str = "Maria da Silva",
    email: str = "maria@example.com",
    cpf: str = CPF_MARIA,
    telefone: str = "86988887777",
) -> dict:
    """Monta o JSON de paciente ou administrador, já com consentimento e senha de teste.

    Os argumentos nomeados trocam e-mail, CPF ou telefone quando o teste precisa de outra pessoa.
    """
    return {
        "nome": nome,
        "cpf": cpf,
        "orgao_emissor": "SSP/PI",
        "data_nascimento": "1998-05-20",
        "genero": "feminino",
        "telefone": telefone,
        "email": email,
        "senha": SENHA,
        "consentimento_lgpd": True,
        "cep": endereco()["cep"],
        "endereco": endereco()["endereco"],
    }


def dados_profissional(
    *,
    nome: str = "João Marcos Souza",
    email: str = "joao@example.com",
    cpf: str = CPF_JOAO,
    telefone: str = "86977776666",
    numero_conselho: str = "123456",
    especialidades: list[str] | None = None,
) -> dict:
    """Parte do JSON de usuário e acrescenta conselho e especialidades.

    Passo a passo:
    1. Reaproveita dados_usuario.
    2. Inclui número do conselho, órgão, texto profissional e a lista de especialidades.
    3. A lista padrão repete Clínica médica de propósito, para o cadastro gravar só uma.
    """
    dados = dados_usuario(nome=nome, email=email, cpf=cpf, telefone=telefone)
    dados.update(
        {
            "numero_conselho": numero_conselho,
            "orgao_conselho": "CRM",
            "info_profissional": "Clínico geral com atuação em telemedicina.",
            "especialidades": especialidades or ["Clínica médica", "Clínica médica"],
        }
    )
    return dados
