"""Valida e normaliza CPF, e-mail, CEP, telefone e campos de texto do cadastro.

Regra do grupo: o campo que só aceita números RECUSA letras e símbolos
(em vez de apagá-los em silêncio), e o campo que só aceita letras RECUSA números.
Assim "abc123.456.789-09xyz" deixa de ser aceito como CPF.
"""

import re
import unicodedata

# [0-9] explícito: o \d do Python também casa dígitos de outros alfabetos.
_CPF = re.compile(r"[0-9]{11}|[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}")
_CEP = re.compile(r"[0-9]{5}-?[0-9]{3}")
_TELEFONE = re.compile(r"\+?[0-9()\s\-]+")

_LETRA = r"[^\W\d_]"  # qualquer letra, com acento, sem número nem "_"

# Cada padrão é um "fullmatch": o texto inteiro precisa obedecer.
_NOME = re.compile(rf"{_LETRA}(?:{_LETRA}|[ '’.\-])*")
_SIGLA = re.compile(rf"(?:{_LETRA}|[0-9])(?:{_LETRA}|[0-9]|[ ./\-])*")  # SSP-PI, CRM-PI
_LOGRADOURO = re.compile(rf"(?:{_LETRA}|[0-9])(?:{_LETRA}|[0-9]|[ .,'/\-ºª°])*")
_NUMERO_ENDERECO = re.compile(r"[0-9]{1,8}")
_NUMERO_ENDERECO_EDICAO = re.compile(r"(?i)S/?N|[0-9]{1,8}(?:[ /\-]?[A-Z0-9]{1,4})?")
_COMPLEMENTO = re.compile(rf"(?:{_LETRA}|[0-9])(?:{_LETRA}|[0-9]|[ .,'/\-ºª°#()])*")
_NUMERO_CONSELHO = re.compile(r"[0-9]{1,15}")


def _nfc(valor: str) -> str:
    """Junta letra + acento soltos (NFD) em um só caractere, para a regex reconhecer."""
    return unicodedata.normalize("NFC", valor.strip())


def normalizar_cpf(valor: str) -> str:
    """Devolve o CPF mascarado (14 caracteres), no tamanho da coluna usuario.cpf.

    Aceita só 11 números ou o formato 000.000.000-00. Qualquer outro caractere é recusado.
    """
    texto = valor.strip()
    if not _CPF.fullmatch(texto):
        raise ValueError("O CPF deve conter apenas números (11 dígitos), com ou sem pontos e traço.")
    digitos = "".join(caractere for caractere in texto if caractere.isdigit())
    if digitos == digitos[0] * 11:
        raise ValueError("O CPF informado é inválido. Confira os números e tente novamente.")

    def digito(base: str) -> str:
        """Calcula o dígito verificador do CPF para a base informada."""
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
    texto = valor.strip()
    if not _CEP.fullmatch(texto):
        raise ValueError("O CEP deve conter apenas 8 números, com ou sem hífen.")
    digitos = texto.replace("-", "")
    return f"{digitos[:5]}-{digitos[5:]}"


def normalizar_telefone(valor: str) -> str:
    """Guarda só os dígitos. A coluna telefone aceita até 20 caracteres.

    Aceita números, espaço, parênteses, hífen e "+" no começo. Letras são recusadas.
    """
    texto = valor.strip()
    if not _TELEFONE.fullmatch(texto):
        raise ValueError("O telefone deve conter apenas números (com DDD). Use no máximo espaço, parênteses e hífen.")
    digitos = "".join(caractere for caractere in texto if caractere.isdigit())
    if len(digitos) < 10 or len(digitos) > 20:
        raise ValueError("O telefone informado é inválido. Informe o DDD e o número.")
    return digitos


def validar_nome(valor: str, rotulo: str) -> str:
    """Texto só com letras (nome, cidade, bairro, gênero): aceita espaço, apóstrofo, ponto e hífen."""
    texto = _nfc(valor)
    if not _NOME.fullmatch(texto):
        raise ValueError(f"O campo {rotulo} deve conter apenas letras (sem números ou símbolos).")
    return texto


def validar_sigla(valor: str, rotulo: str) -> str:
    """Órgão emissor ou conselho (SSP-PI, CRM-PI): letras, números, espaço, "/" e hífen."""
    texto = _nfc(valor)
    if not _SIGLA.fullmatch(texto):
        raise ValueError(f"O campo {rotulo} deve conter apenas letras, números, espaço, hífen ou barra.")
    return texto


def validar_logradouro(valor: str) -> str:
    """Rua/avenida: letras, números e . , ' / - º ª."""
    texto = _nfc(valor)
    if not _LOGRADOURO.fullmatch(texto):
        raise ValueError("O logradouro contém caracteres não permitidos. Use letras, números e pontuação simples.")
    return texto


def validar_numero_endereco(valor: str) -> str:
    """Número da casa: só números (até 8 dígitos)."""
    texto = valor.strip()
    if not _NUMERO_ENDERECO.fullmatch(texto):
        raise ValueError("O número do endereço deve conter apenas números.")
    return texto


def validar_numero_endereco_edicao(valor: str) -> str:
    """Número ao editar o endereço em "minha conta": como o cadastro antigo, aceita
    também sufixo curto (120-A) e S/N, para não travar quem já tem esse valor salvo.
    Maiúsculas e minúsculas são mantidas como a pessoa digitou.
    """
    texto = valor.strip()
    if not _NUMERO_ENDERECO_EDICAO.fullmatch(texto):
        raise ValueError('O número do endereço deve conter números (ex.: 120, 120-A) ou "S/N".')
    return texto


def validar_complemento(valor: str) -> str:
    """Complemento: letras, números e . , ' / - # ( ) º ª."""
    texto = _nfc(valor)
    if not _COMPLEMENTO.fullmatch(texto):
        raise ValueError("O complemento contém caracteres não permitidos. Use letras, números e pontuação simples.")
    return texto


def validar_numero_conselho(valor: str) -> str:
    """Número do conselho: só números (a sigla, como CRM-PI, vai no campo órgão do conselho)."""
    texto = valor.strip()
    if not _NUMERO_CONSELHO.fullmatch(texto):
        raise ValueError("O número do conselho deve conter apenas números.")
    return texto


def validar_especialidade(valor: str) -> str:
    """Nome da especialidade: letras, espaço e . ' / - ( )."""
    texto = _nfc(valor)
    if not re.fullmatch(rf"{_LETRA}(?:{_LETRA}|[ .'/\-()])*", texto):
        raise ValueError("A especialidade deve conter apenas letras (sem números ou símbolos).")
    return texto