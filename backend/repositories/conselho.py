"""Consultas da tabela info_conselho."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.models import InfoConselho


class RepositorioConselho:
    """Consultas de conselhos profissionais. Não aplica regra de negócio."""

    def __init__(self, db: Session) -> None:
        """Guarda a sessão do banco usada nas consultas.

        Args:
            db (Session): Sessão do banco de dados.
        """
        self.db = db

    def buscar(self, numero_conselho: str, orgao_conselho: str) -> InfoConselho | None:
        """Conselho pelo número e órgão, ou None se não existir.

        Args:
            numero_conselho (str): Número de registro no conselho.
            orgao_conselho (str): Órgão do conselho.

        Returns:
            InfoConselho | None: Conselho encontrado, ou None.
        """
        return self.db.scalar(
            select(InfoConselho).where(
                InfoConselho.numero_conselho == numero_conselho,
                InfoConselho.orgao_conselho == orgao_conselho,
            )
        )
