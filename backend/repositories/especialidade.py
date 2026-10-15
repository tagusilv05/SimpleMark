"""Consultas da tabela especialidade."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.models import Especialidade


class RepositorioEspecialidade:
    """Reaproveita a especialidade pelo nome, sem diferenciar maiúsculas."""

    def __init__(self, db: Session) -> None:
        """Guarda a sessão do banco usada nas consultas."""
        self.db = db

    def obter_ou_criar(self, nome: str) -> Especialidade:
        """Especialidade com esse nome, criada se ainda não existir.

        Compara com casefold em Python, carregando todas as especialidades.
        Quando cria, faz flush para o id já ficar disponível.
        """
        existentes = self.db.scalars(select(Especialidade)).all()
        for item in existentes:
            if item.especialidade.casefold() == nome.casefold():
                return item
        criada = Especialidade(especialidade=nome)
        self.db.add(criada)
        self.db.flush()
        return criada
