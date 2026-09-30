# Arquivo criado por Victor
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import ErroNegocio

logger = logging.getLogger("simplemark.api")

_ROTULOS = {
    "nome": "nome",
    "cpf": "CPF",
    "orgao_emissor": "órgão emissor",
    "data_nascimento": "data de nascimento",
    "genero": "gênero",
    "telefone": "telefone",
    "email": "e-mail",
    "senha": "senha",
    "identificador": "identificador",
    "token": "token",
    "endereco": "endereço",
    "cep": "CEP",
    "consentimento_lgpd": "consentimento",
    "numero_conselho": "número do conselho",
    "orgao_conselho": "órgão do conselho",
    "info_profissional": "informações profissionais",
    "especialidades": "especialidades",
}


def registrar_erros(app: FastAPI) -> None:
    """Liga os quatro tradutores de erro na aplicação.

    Passo a passo:
    1. ErroNegocio vira JSON com a mensagem da regra.
    2. Erro de validação do Pydantic vira 422 em português.
    3. HTTPException, inclusive 404, vira o mesmo formato de mensagem.
    4. Qualquer outra exceção vira 500 genérico, com o detalhe só no log.
    """
    app.add_exception_handler(ErroNegocio, _erro_negocio)
    app.add_exception_handler(RequestValidationError, _erro_validacao)
    app.add_exception_handler(HTTPException, _erro_http)
    app.add_exception_handler(Exception, _erro_interno)


def _erro_negocio(_request: Request, exc: Exception) -> JSONResponse:
    """Devolve a mensagem da regra e o status escolhido pelo service.

    Passo a passo:
    1. Confirma que a exceção é ErroNegocio.
    2. No 401, acrescenta o header WWW-Authenticate para o cliente saber que falta Bearer.
    3. Responde {"mensagem": "..."} sem rastreio interno.
    """
    erro = exc if isinstance(exc, ErroNegocio) else ErroNegocio("Não foi possível concluir a solicitação.")
    headers = {"WWW-Authenticate": "Bearer"} if erro.status_code == 401 else None
    return JSONResponse(status_code=erro.status_code, content={"mensagem": erro.mensagem}, headers=headers)


def _erro_validacao(_request: Request, exc: Exception) -> JSONResponse:
    """Junta os erros de campo numa frase só, em português (RNF3).

    Passo a passo:
    1. Lê a lista errors() do Pydantic.
    2. Traduz cada item em _mensagem_validacao.
    3. Une as frases com espaço e responde 422.
    """
    erros = exc.errors() if isinstance(exc, RequestValidationError) else []
    mensagens = [_mensagem_validacao(erro) for erro in erros]
    texto = " ".join(mensagens) if mensagens else "Revise os dados enviados e tente novamente."
    return JSONResponse(status_code=422, content={"mensagem": texto})


def _erro_http(_request: Request, exc: Exception) -> JSONResponse:
    """Traduz HTTPException para o JSON de mensagem.

    Passo a passo:
    1. Se não for HTTPException, cai no 500 genérico.
    2. 404 padrão do FastAPI ganha a frase sobre URL inexistente.
    3. Os outros status reaproveitam o detail quando ele já é texto.
    """
    if not isinstance(exc, HTTPException):
        return JSONResponse(status_code=500, content={"mensagem": "Ocorreu um erro interno. Tente novamente em instantes."})
    if exc.status_code == 404 and exc.detail == "Not Found":
        mensagem = "O endereço solicitado não existe. Verifique a URL e tente novamente."
    elif isinstance(exc.detail, str):
        mensagem = exc.detail
    else:
        mensagem = "Não foi possível concluir a solicitação. Tente novamente."
    return JSONResponse(status_code=exc.status_code, content={"mensagem": mensagem}, headers=exc.headers)


def _erro_interno(_request: Request, exc: Exception) -> JSONResponse:
    """Esconde falha inesperada do cliente e registra o traceback no log.

    Passo a passo:
    1. logger.exception grava a pilha completa no terminal do uvicorn.
    2. O cliente recebe só a frase genérica e o status 500.
    """
    logger.exception("Falha não tratada na API")
    return JSONResponse(
        status_code=500,
        content={"mensagem": "Ocorreu um erro interno. Tente novamente em instantes."},
    )


def _mensagem_validacao(erro: dict) -> str:
    """Traduz um item do Pydantic para uma frase com o que corrigir.

    Passo a passo:
    1. Lê o tipo do erro e a mensagem original.
    2. Remove o prefixo "Value error, " que o Pydantic coloca na frente.
    3. Troca o nome técnico do campo pelo rótulo em português.
    4. Casos conhecidos (obrigatório, extra, inteiro, data, especialidade) ganham frase própria.
    5. O restante devolve a mensagem já limpa, que veio do validador do schema.
    """
    tipo = str(erro.get("type", ""))
    texto = str(erro.get("msg", "Revise os dados enviados e tente novamente."))
    prefixo = "Value error, "
    if texto.startswith(prefixo):
        texto = texto[len(prefixo):]
    campo = _rotulo(erro.get("loc", ()))
    if tipo == "json_invalid" or texto.startswith("JSON decode error"):
        return (
            "O corpo da requisição não é um JSON válido. "
            "Confira aspas duplas, vírgulas e as chaves, e envie de novo."
        )
    if tipo == "missing":
        return f"O campo {campo} é obrigatório. Preencha-o e tente novamente."
    if tipo == "extra_forbidden":
        return f"O campo {campo} não faz parte desta requisição. Remova-o e tente novamente."
    if tipo in {"int_parsing", "int_type"}:
        return "O identificador informado é inválido. Envie um número inteiro."
    if tipo in {"date_parsing", "date_from_datetime_parsing"}:
        return "A data de nascimento é inválida. Use o formato AAAA-MM-DD."
    if tipo == "too_short" and campo == "especialidades":
        return "Informe ao menos uma especialidade para o profissional atuar na plataforma."
    return texto


def _rotulo(loc: object) -> str:
    """Pega o último nome do caminho do campo e troca pelo rótulo amigável.

    Passo a passo:
    1. loc vem como ("body", "endereco", "cep"). O último item é o campo.
    2. Se o caminho vier vazio, usa "informado".
    3. Procura o rótulo em _ROTULOS. Se não houver, devolve o nome cru.
    """
    if not isinstance(loc, (tuple, list)) or not loc:
        return "informado"
    nome = str(loc[-1])
    return _ROTULOS.get(nome, nome)
