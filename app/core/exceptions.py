# Arquivo criado por Victor
class ErroNegocio(Exception):
    """Falha de regra de negócio que a API devolve ao cliente, em português (RNF3)."""

    def __init__(self, mensagem: str, status_code: int = 400) -> None:
        """Guarda a frase em português e o código HTTP que a rota deve devolver.

        Passo a passo:
        1. mensagem fica no JSON {"mensagem": "..."}.
        2. status_code vira o status da resposta. O padrão é 400.
        3. A Exception base também recebe o texto, para o log mostrar a mesma frase.
        """
        self.mensagem = mensagem
        self.status_code = status_code
        super().__init__(mensagem)
