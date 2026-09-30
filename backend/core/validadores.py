"""Normaliza CPF, e-mail, CEP e telefone para caber nas colunas do grupo."""


def normalizar_cpf(valor: str) -> str:
    """Devolve o CPF mascarado (14 caracteres), no tamanho da coluna usuario.cpf."""
    digitos = "".join(caractere for caractere in valor if caractere.isdigit())
    if len(digitos) != 11 or digitos == digitos[0] * 11:
        raise ValueError("O CPF informado é inválido. Confira os números e tente novamente.")

    def digito(base: str) -> str:
        soma = sum(int(numero) * peso for numero, peso in zip(base, range(len(base) + 1, 1, -1)))
        resto = soma % 11
        if resto < 2:
            return "0"
        return str(11 - resto)

    if digito(digitos[:9]) != digitos[9] or digito(digitos[:10]) != digitos[10]:
        raise ValueError("O CPF informado é inválido. Confira os números e tente novamente.")
    return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"


def normalizar_email(valor: str) -> str:
    """E-mail em minúsculas, no máximo 150 caracteres (coluna usuario.email)."""
    email = valor.strip().lower()
    if len(email) > 150 or " " in email or email.count("@") != 1:
        raise ValueError("O e-mail informado é inválido. Verifique e tente novamente.")
    local, dominio = email.split("@")
    if not local or "." not in dominio or dominio.startswith(".") or dominio.endswith("."):
        raise ValueError("O e-mail informado é inválido. Verifique e tente novamente.")
    return email


def normalizar_cep(valor: str) -> str:
    """CEP com hífen (9 caracteres), no tamanho da coluna endereco.cep."""
    digitos = "".join(caractere for caractere in valor if caractere.isdigit())
    if len(digitos) != 8:
        raise ValueError("O CEP informado é inválido. Use 8 números.")
    return f"{digitos[:5]}-{digitos[5:]}"


def normalizar_telefone(valor: str) -> str:
    """Guarda só os dígitos. A coluna telefone aceita até 20 caracteres."""
    digitos = "".join(caractere for caractere in valor if caractere.isdigit())
    if len(digitos) < 10 or len(digitos) > 20:
        raise ValueError("O telefone informado é inválido. Informe o DDD e o número.")
    return digitos