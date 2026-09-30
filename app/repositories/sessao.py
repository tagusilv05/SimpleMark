# Arquivo criado por Gustavo
import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.sessao import Sessao


class RepositorioSessao:
    """Acesso à tabela sessao. Regras de expiração ficam no service."""

    def __init__(self, db: Session):
        self.db = db

    def criar(self, id_usuario: int, agora: datetime) -> Sessao:
        """Insere uma sessão nova, com criação e última atividade no momento do login.

        Passo a passo:
        1. Monta a linha com o id do usuário e o horário.
        2. flush envia o INSERT e gera o id, sem confirmar. Quem chama faz o commit.
        """
        sessao = Sessao(id_usuario=id_usuario, criada_em=agora, ultima_atividade_em=agora)
        self.db.add(sessao)
        self.db.flush()
        return sessao

    def buscar(self, id_sessao: uuid.UUID, id_usuario: int) -> Sessao | None:
        """Busca a sessão pelo id E pelo dono.

        Exigir os dois impede usar o id de uma sessão com o token de outra conta.
        """
        comando = select(Sessao).where(Sessao.id == id_sessao, Sessao.id_usuario == id_usuario)
        return self.db.scalar(comando)

    def registrar_atividade(self, id_sessao: uuid.UUID, agora: datetime, anterior_a: datetime) -> None:
        """Atualiza a última atividade, mas só se a gravada for mais velha que anterior_a.

        Passo a passo:
        1. Um único UPDATE faz a conferência e a gravação juntas.
        2. Duas requisições simultâneas não se atrapalham: nenhuma lê um valor para
           depois regravar, então não existe o risco de sobrescrever a outra.
        3. synchronize_session=False: o SQLAlchemy não tenta repetir o UPDATE, em Python,
           no objeto Sessao já carregado. Ninguém lê esse campo do objeto depois,
           e essa repetição comparava datas com e sem fuso horário.
        """
        comando = (
            update(Sessao)
            .where(Sessao.id == id_sessao, Sessao.ultima_atividade_em < anterior_a)
            .values(ultima_atividade_em=agora)
            .execution_options(synchronize_session=False)
        )
        self.db.execute(comando)
