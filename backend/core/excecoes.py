"""Erro de regra de negócio, com a mensagem que a API devolve ao cliente."""


class ErroNegocio(Exception):
    def __init__(self, mensagem: str, status_code: int = 400) -> None:
        self.mensagem = mensagem
        self.status_code = status_code
        super().__init__(mensagem)