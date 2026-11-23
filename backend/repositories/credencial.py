"""Consultas da tabela credencial."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.acesso import Credencial


class RepositorioCredencial:
    """Senha e contador de falhas. A trava da linha evita duas tentativas ao mesmo tempo."""

    def __init__(self, db: Session) -> None:
        """Guarda a sessão do banco usada nas consultas.

        Args:
            db (Session): Sessão do banco de dados.
        """
        self.db = db

    def buscar_para_atualizar(self, id_usuario: uuid.UUID) -> Credencial | None:
        """Credencial do usuário com a linha travada (FOR UPDATE), ou None.

        populate_existing recarrega o objeto mesmo que ele já esteja na sessão.

        Args:
            id_usuario (uuid.UUID): Id do usuário.

        Returns:
            Credencial | None: Credencial travada, ou None se não existir.
        """
        comando = (
            select(Credencial)
            .where(Credencial.id_usuario == id_usuario)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return self.db.execute(comando).scalar_one_or_none()

    def adicionar(self, credencial: Credencial) -> Credencial:
        """Inclui a credencial na sessão, sem flush nem commit.

        Args:
            credencial (Credencial): Credencial a incluir.

        Returns:
            Credencial: A mesma credencial recebida.
        """
        self.db.add(credencial)
        return credencial
