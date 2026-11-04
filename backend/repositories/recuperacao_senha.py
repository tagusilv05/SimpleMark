"""Consultas da tabela codigo_recuperacao_senha (e o encerramento das sessões abertas)."""

import uuid
from datetime import datetime

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from models.acesso import SessaoLogin
from models.recuperacao_senha import CodigoRecuperacaoSenha


class RepositorioRecuperacaoSenha:
    """Consultas da recuperação de senha. Não aplica regra de negócio."""

    def __init__(self, db: Session) -> None:
        """Guarda a sessão do banco usada nas consultas."""
        self.db = db

    def criar(
        self,
        id_usuario: uuid.UUID,
        codigo_hash: str,
        agora: datetime,
        expira_em: datetime,
    ) -> CodigoRecuperacaoSenha:
        """Registra um código de recuperação e faz flush para o id já ficar disponível."""
        codigo = CodigoRecuperacaoSenha(
            id_usuario=id_usuario,
            codigo_hash=codigo_hash,
            criado_em=agora,
            expira_em=expira_em,
        )
        self.db.add(codigo)
        self.db.flush()
        return codigo

    def buscar(self, id_codigo: uuid.UUID) -> CodigoRecuperacaoSenha | None:
        """Código pelo id, ou None se não existir."""
        return self.db.get(CodigoRecuperacaoSenha, id_codigo)

    def buscar_para_atualizar(self, id_codigo: uuid.UUID) -> CodigoRecuperacaoSenha | None:
        """Trava a linha: dois envios do mesmo código ao mesmo tempo não passam juntos."""
        comando = (
            select(CodigoRecuperacaoSenha)
            .where(CodigoRecuperacaoSenha.id == id_codigo)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return self.db.execute(comando).scalar_one_or_none()

    def buscar_pendente_criado_apos(
        self,
        id_usuario: uuid.UUID,
        criado_apos: datetime,
        agora: datetime,
    ) -> CodigoRecuperacaoSenha | None:
        """Código ainda em aberto, não expirado, criado depois de `criado_apos`."""
        comando = (
            select(CodigoRecuperacaoSenha)
            .where(
                CodigoRecuperacaoSenha.id_usuario == id_usuario,
                CodigoRecuperacaoSenha.encerrado_em.is_(None),
                CodigoRecuperacaoSenha.expira_em > agora,
                CodigoRecuperacaoSenha.criado_em > criado_apos,
            )
            .order_by(CodigoRecuperacaoSenha.criado_em.desc())
            .limit(1)
        )
        return self.db.scalar(comando)

    def existe_hash(self, id_usuario: uuid.UUID, codigo_hash: str) -> bool:
        """Indica se o usuário já teve um código com esse hash."""
        comando = select(CodigoRecuperacaoSenha.id).where(
            CodigoRecuperacaoSenha.id_usuario == id_usuario,
            CodigoRecuperacaoSenha.codigo_hash == codigo_hash,
        )
        return self.db.scalar(comando) is not None

    def encerrar_pendentes(self, id_usuario: uuid.UUID, agora: datetime) -> None:
        """Marca como encerrados os códigos do usuário ainda em aberto."""
        comando = (
            update(CodigoRecuperacaoSenha)
            .where(
                CodigoRecuperacaoSenha.id_usuario == id_usuario,
                CodigoRecuperacaoSenha.encerrado_em.is_(None),
            )
            .values(encerrado_em=agora)
            .execution_options(synchronize_session=False)
        )
        self.db.execute(comando)

    def apagar_anteriores_a(self, id_usuario: uuid.UUID, limite: datetime) -> None:
        """Apaga os códigos do usuário criados antes do limite."""
        comando = (
            delete(CodigoRecuperacaoSenha)
            .where(
                CodigoRecuperacaoSenha.id_usuario == id_usuario,
                CodigoRecuperacaoSenha.criado_em < limite,
            )
            .execution_options(synchronize_session=False)
        )
        self.db.execute(comando)

    def encerrar_sessoes_abertas(self, id_usuario: uuid.UUID, agora: datetime) -> None:
        """Encerra todas as sessões de login abertas do usuário (logout em todos os aparelhos)."""
        comando = (
            update(SessaoLogin)
            .where(SessaoLogin.id_usuario == id_usuario, SessaoLogin.encerrada_em.is_(None))
            .values(encerrada_em=agora)
            .execution_options(synchronize_session=False)
        )
        self.db.execute(comando)