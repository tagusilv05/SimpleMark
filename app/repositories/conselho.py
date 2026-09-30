# Arquivo criado por Victor
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.info_conselho import InfoConselho

# Classe para representar o repositório de conselhos.
class RepositorioConselho:
    """Consulta o par número + órgão do conselho, que é único no banco."""

    # Método para inicializar o repositório de conselhos.
    def __init__(self, db: Session) -> None:
        """Guarda a sessão da requisição."""
        self.db = db

    def buscar(self, numero_conselho: str, orgao_conselho: str) -> InfoConselho | None:
        """Procura um conselho já cadastrado com o mesmo número e o mesmo órgão.

        Passo a passo:
        1. Filtra info_conselho pelos dois campos ao mesmo tempo.
        2. Devolve a linha ou None. None significa que o par ainda está livre.
        """
        return self.db.scalar(
            select(InfoConselho).where(
                InfoConselho.numero_conselho == numero_conselho,
                InfoConselho.orgao_conselho == orgao_conselho,
            )
        )

    # Esse método não salva no banco de dados, apenas adiciona na sessão. Pois, quem decide se salva ou não é o Service.
    def adicionar(self, conselho: InfoConselho) -> InfoConselho:
        """Marca o conselho para INSERT no commit.

        Passo a passo:
        1. db.add inclui o objeto na sessão.
        2. Devolve o mesmo objeto para o service ligar ao profissional.
        """
        
        # Adiciona o conselho na sessão.
        self.db.add(conselho)

        # Devolve o mesmo objeto para o service ligar ao profissional.
        return conselho