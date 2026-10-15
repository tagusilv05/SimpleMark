"""Erro de regra de negócio, com a mensagem que a API devolve ao cliente."""


class ErroNegocio(Exception):
    """Falha de regra de negócio com mensagem e status HTTP (400 por padrão)."""

    def __init__(self, mensagem: str, status_code: int = 400) -> None:
        """Guarda a mensagem e o status HTTP da resposta."""
        self.mensagem = mensagem
        self.status_code = status_code
        super().__init__(mensagem)