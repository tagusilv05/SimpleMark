# Arquivo criado por Victor
from datetime import date

from email_validator import EmailNotValidError, validate_email


def normalizar_cpf(valor: str) -> str:
    """Tira a máscara do CPF e confere os dois dígitos verificadores (RNF4).

    Passo a passo:
    1. Fica só com os números. Ponto e traço são ignorados.
    2. _cpf_valido recusa tamanho diferente de 11, sequência repetida e dígito errado.
    3. Se passar, devolve os 11 dígitos. É assim que o CPF fica gravado.
    """
    digitos = "".join(caractere for caractere in valor if caractere.isdigit())
    if not _cpf_valido(digitos):
        raise ValueError(
            "O CPF informado é inválido. Confira os onze dígitos e tente novamente."
        )
    return digitos


def normalizar_email(valor: str) -> str:
    """Confere o formato do e-mail e devolve em minúsculas (RNF4, RN1).

    Passo a passo:
    1. Tira espaços das pontas.
    2. A biblioteca email_validator confere o formato, sem consultar DNS.
    3. Formato inválido vira ValueError, que o schema mostra em português.
    4. Devolve o endereço normalizado em minúsculas, para o único do banco
       não separar Maria@email.com de maria@email.com.
    """
    texto = valor.strip()
    try:
        resultado = validate_email(texto, check_deliverability=False)
    except EmailNotValidError:
        raise ValueError(
            "O e-mail informado é inválido. Revise o endereço e tente novamente."
        ) from None
    return resultado.normalized.lower()


def normalizar_telefone(valor: str) -> str:
    """Aceita telefone com DDD, com ou sem máscara (RNF4).

    Passo a passo:
    1. Fica só com os dígitos.
    2. Exige 10 dígitos (fixo com DDD) ou 11 (celular com DDD).
    3. Devolve só os números.
    """
    digitos = "".join(caractere for caractere in valor if caractere.isdigit())
    if len(digitos) not in (10, 11):
        raise ValueError(
            "O telefone informado é inválido. Informe o DDD e o número, com 10 ou 11 dígitos."
        )
    return digitos


def normalizar_cep(valor: str) -> str:
    """Aceita CEP com ou sem hífen e guarda os 8 dígitos (RNF4).

    Passo a passo:
    1. Remove tudo que não for número.
    2. Exige exatamente 8 dígitos.
    3. Devolve esses 8 dígitos.
    """
    digitos = "".join(caractere for caractere in valor if caractere.isdigit())
    if len(digitos) != 8:
        raise ValueError("O CEP informado é inválido. Informe os 8 dígitos do CEP.")
    return digitos


def normalizar_nome(valor: str) -> str:
    """Exige nome e sobrenome e limita o tamanho ao da coluna nome.

    Passo a passo:
    1. Junta espaços repetidos em um só e tira os das pontas.
    2. Exige pelo menos duas palavras, porque o RF1 pede nome completo.
    3. Recusa acima de 150 caracteres, que é o tamanho da coluna.
    4. Devolve o nome limpo, sem alterar maiúsculas.
    """
    nome = " ".join(valor.split())
    if len(nome.split()) < 2:
        raise ValueError("Informe o nome completo, com nome e sobrenome.")
    if len(nome) > 150:
        raise ValueError("O nome completo deve ter no máximo 150 caracteres.")
    return nome


def texto_obrigatorio(valor: str, rotulo: str, maximo: int) -> str:
    """Limpa um texto obrigatório e aplica o tamanho máximo da coluna.

    Passo a passo:
    1. Junta espaços repetidos.
    2. Recusa vazio, citando o nome do campo na mensagem.
    3. Recusa texto maior que o limite da coluna.
    4. Devolve o texto limpo.
    """
    texto = " ".join(valor.split())
    if not texto:
        raise ValueError(f"O campo {rotulo} é obrigatório. Preencha-o e tente novamente.")
    if len(texto) > maximo:
        raise ValueError(f"O campo {rotulo} deve ter no máximo {maximo} caracteres.")
    return texto


def validar_senha(valor: str) -> str:
    """Exige senha entre 8 e 128 caracteres, sem cortar espaços do meio.

    Passo a passo:
    1. Não remove espaços: senha com espaço no fim é senha diferente.
    2. Recusa menos de 8 caracteres.
    3. Recusa mais de 128, para não estourar o uso do hash.
    4. Devolve a senha original. O hash só é calculado no service.
    """
    if len(valor) < 8:
        raise ValueError(
            "A senha deve ter no mínimo 8 caracteres. Escolha uma senha mais longa."
        )
    if len(valor) > 128:
        raise ValueError("A senha deve ter no máximo 128 caracteres.")
    return valor


def validar_data_nascimento(valor: date) -> date:
    """Recusa data de nascimento no futuro.

    Passo a passo:
    1. Compara com a data de hoje no relógio do servidor.
    2. Se for futura, interrompe com mensagem para corrigir o campo.
    3. Se não for, devolve a mesma data.
    """
    if valor > date.today():
        raise ValueError(
            "A data de nascimento não pode ser futura. Informe a data correta."
        )
    return valor


def _cpf_valido(cpf: str) -> bool:
    """Aplica a regra oficial dos dois dígitos do CPF.

    Passo a passo:
    1. Exige 11 números.
    2. Recusa sequências como 111.111.111-11, que passam na conta e não são CPF.
    3. Recalcula o primeiro dígito com os 9 primeiros números.
    4. Recalcula o segundo com os 9 primeiros mais o primeiro dígito.
    5. Compara os dois dígitos calculados com os dois últimos informados.
    """
    if len(cpf) != 11 or not cpf.isdigit():
        return False
    if cpf == cpf[0] * 11:
        return False
    return cpf[-2:] == _digito(cpf[:9]) + _digito(cpf[:10])


def _digito(base: str) -> str:
    """Calcula um dígito verificador do CPF.

    Passo a passo:
    1. Multiplica cada número por um peso decrescente. Para 9 números o peso
       começa em 10. Para 10 números, começa em 11.
    2. Soma os produtos e pega o resto da divisão por 11.
    3. Resto 0 ou 1 vira dígito 0. Nos outros casos, o dígito é 11 menos o resto.
    """
    peso_inicial = len(base) + 1
    soma = sum(int(numero) * peso for numero, peso in zip(base, range(peso_inicial, 1, -1)))
    resto = soma % 11
    if resto < 2:
        return "0"
    return str(11 - resto)
