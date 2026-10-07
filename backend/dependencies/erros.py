"""Erros das rotas novas. As rotas de horários do grupo mantêm o formato original."""

from fastapi import FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from core.excecoes import ErroNegocio

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
    "cep": "CEP",
    "cidade": "cidade",
    "logradouro": "logradouro",
    "numero": "número",
    "bairro": "bairro",
    "complemento": "complemento",
    "consentimento_lgpd": "consentimento",
    "numero_conselho": "número do conselho",
    "orgao_conselho": "órgão do conselho",
    "info_profissional": "informações profissionais",
    "especialidades": "especialidades",
    "nota": "nota",
    "feedback": "comentário",
}


def registrar_erros(app: FastAPI) -> None:
    app.add_exception_handler(ErroNegocio, _erro_negocio)
    app.add_exception_handler(RequestValidationError, _erro_validacao)


def _erro_negocio(_request: Request, exc: Exception) -> JSONResponse:
    erro = exc if isinstance(exc, ErroNegocio) else ErroNegocio("Não foi possível concluir a solicitação.")
    headers = {"WWW-Authenticate": "Bearer"} if erro.status_code == 401 else None
    return JSONResponse(status_code=erro.status_code, content={"mensagem": erro.mensagem}, headers=headers)


async def _erro_validacao(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, RequestValidationError) or not request.url.path.startswith("/api/v1"):
        if isinstance(exc, RequestValidationError):
            return await request_validation_exception_handler(request, exc)
        return JSONResponse(status_code=422, content={"detail": "Revise os dados enviados."})
    mensagens = [_mensagem_validacao(erro) for erro in exc.errors()]
    texto = " ".join(mensagens) if mensagens else "Revise os dados enviados e tente novamente."
    return JSONResponse(status_code=422, content={"mensagem": texto})


def _mensagem_validacao(erro: dict) -> str:
    tipo = str(erro.get("type", ""))
    texto = str(erro.get("msg", "Revise os dados enviados e tente novamente."))
    prefixo = "Value error, "
    if texto.startswith(prefixo):
        texto = texto[len(prefixo):]
    campo = _rotulo(erro.get("loc", ()))
    if tipo == "missing":
        return f"O campo {campo} é obrigatório. Preencha-o e tente novamente."
    if tipo == "extra_forbidden":
        return f"O campo {campo} não faz parte desta requisição. Remova-o e tente novamente."
    if tipo in {"date_parsing", "date_from_datetime_parsing"}:
        return "A data de nascimento é inválida. Use o formato AAAA-MM-DD."
    if campo == "nota" and tipo in {"int_type", "int_parsing"}:
        return "A nota deve ser um número inteiro de 1 a 5 estrelas."
    if campo == "limite" and tipo in {"int_parsing", "greater_than_equal", "less_than_equal"}:
        return "O limite deve ser um número inteiro de 1 a 50."
    if tipo == "too_short" and campo == "especialidades":
        return "Informe ao menos uma especialidade para o profissional atuar na plataforma."
    if tipo == "too_short" and campo == "senha":
        return "A senha deve ter no mínimo 8 caracteres."
    return texto


def _rotulo(loc: object) -> str:
    if not isinstance(loc, (tuple, list)) or not loc:
        return "informado"
    nome = str(loc[-1])
    return _ROTULOS.get(nome, nome)