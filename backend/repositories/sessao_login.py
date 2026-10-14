"""Consultas da tabela sessao_login."""

import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from models.acesso import SessaoLogin


class RepositorioSessaoLogin:
    """Sessões de login: criação, busca e registro de atividade. Não aplica regra de negócio."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def criar(self, id_usuario: uuid.UUID, agora: datetime) -> SessaoLogin:
        """Abre uma sessão para o usuário e faz flush para o id já ficar disponível."""
        sessao = SessaoLogin(
            id_usuario=id_usuario,
            criada_em=agora,
            ultima_atividade_em=agora,
        )
        self.db.add(sessao)
        self.db.flush()
        return sessao

    def buscar(self, id_sessao: uuid.UUID, id_usuario: uuid.UUID) -> SessaoLogin | None:
        """Sessão pelo id, só se pertencer ao usuário; senão None."""
        comando = select(SessaoLogin).where(
            SessaoLogin.id == id_sessao,
            SessaoLogin.id_usuario == id_usuario,
        )
        return self.db.scalar(comando)

    def registrar_atividade(self, id_sessao: uuid.UUID, agora: datetime, anterior_a: datetime) -> None:
        """Marca a última atividade da sessão como agora.

        Só grava se a atividade registrada for anterior a anterior_a, o que poupa
        um UPDATE a cada requisição. Não sincroniza objetos já carregados na sessão.
        """
        comando = (
            update(SessaoLogin)
            .where(
                SessaoLogin.id == id_sessao,
                SessaoLogin.ultima_atividade_em < anterior_a,
            )
            .values(ultima_atividade_em=agora)
            .execution_options(synchronize_session=False)
        )
        self.db.execute(comando)
