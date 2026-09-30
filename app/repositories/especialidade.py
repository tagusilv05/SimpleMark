# Arquivo criado por Victor
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.especialidade import Especialidade


# Classe para representar o repositório de especialidades.
class RepositorioEspecialidade:
    """Reaproveita a especialidade quando o nome já existe, sem diferenciar maiúsculas."""

    def __init__(self, db: Session) -> None:
        """Guarda a sessão da requisição."""
        self.db = db

    def obter_ou_criar(self, nome: str) -> Especialidade:
        """Devolve a especialidade existente ou insere uma nova.

        Passo a passo:
        1. Procura uma linha cujo nome, em minúsculas, seja igual ao informado.
        2. Se achar, devolve essa linha. Não cria duplicata.
        3. Se não achar, cria o objeto, faz flush para obter o id e devolve.
        """
        # Busca a especialidade existente.
        existente = self.db.scalar(
            select(Especialidade).where(func.lower(Especialidade.nome) == nome.casefold())
        )
        # Se a especialidade existente for encontrada, devolve a especialidade existente.
        if existente is not None:
            return existente

        # Se a especialidade existente não for encontrada, cria a especialidade.
        criada = Especialidade(nome=nome)

        # coloca o objeto na "fila" da sessão pra ser inserido no banco no próximo commit
        self.db.add(criada)
        # manda o objeto para o banco de dados, para ser inserido no banco no próximo commit
        self.db.flush()
        
        # Devolve o objeto com o id já preenchido (por causa do flush) para o service ligar ao profissional.
        return criada