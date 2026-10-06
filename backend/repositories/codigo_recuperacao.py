import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from models.acesso import CodigoRecuperacao


class RepositorioCodigoRecuperacao:
    """Códigos de recuperação de senha. As regras ficam no service."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def criar(
        self,
        id_usuario: uuid.UUID,
        codigo_hash: str,
        agora: datetime,
        expira_em: datetime,
    ) -> CodigoRecuperacao:
        registro = CodigoRecuperacao(
            id_usuario=id_usuario,
            codigo_hash=codigo_hash,
            criado_em=agora,
            expira_em=expira_em,
            tentativas=0,
        )
        self.db.add(registro)
        self.db.flush()
        return registro

    def ultimo_do_usuario(self, id_usuario: uuid.UUID) -> CodigoRecuperacao | None:
        comando = (
            select(CodigoRecuperacao)
            .where(CodigoRecuperacao.id_usuario == id_usuario)
            .order_by(CodigoRecuperacao.criado_em.desc(), CodigoRecuperacao.id.desc())
            .limit(1)
        )
        return self.db.scalar(comando)

    def encerrar_abertos_do_usuario(self, id_usuario: uuid.UUID, agora: datetime) -> None:
        """Encerra todo código e token ainda abertos da conta (um código novo substitui os antigos)."""
        comando = (
            update(CodigoRecuperacao)
            .where(
                CodigoRecuperacao.id_usuario == id_usuario,
                CodigoRecuperacao.encerrado_em.is_(None),
            )
            .values(encerrado_em=agora)
            .execution_options(synchronize_session=False)
        )
        self.db.execute(comando)

    def existe_aberto_com_hash(self, codigo_hash: str, agora: datetime) -> bool:
        """Diz se algum código ainda válido, de qualquer conta, já usa esse hash."""
        comando = (
            select(CodigoRecuperacao.id)
            .where(
                CodigoRecuperacao.codigo_hash == codigo_hash,
                CodigoRecuperacao.encerrado_em.is_(None),
                CodigoRecuperacao.expira_em > agora,
            )
            .limit(1)
        )
        return self.db.scalar(comando) is not None

    def buscar_aguardando_codigo(self, id_usuario: uuid.UUID, agora: datetime) -> CodigoRecuperacao | None:
        """Código da conta que ainda não expirou nem foi conferido. Trava a linha."""
        comando = (
            select(CodigoRecuperacao)
            .where(
                CodigoRecuperacao.id_usuario == id_usuario,
                CodigoRecuperacao.encerrado_em.is_(None),
                CodigoRecuperacao.verificado_em.is_(None),
                CodigoRecuperacao.expira_em > agora,
            )
            .order_by(CodigoRecuperacao.criado_em.desc(), CodigoRecuperacao.id.desc())
            .limit(1)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return self.db.scalar(comando)

    def buscar_por_token(self, token_hash: str) -> CodigoRecuperacao | None:
        return self.db.scalar(
            select(CodigoRecuperacao).where(CodigoRecuperacao.token_hash == token_hash)
        )

    def buscar_por_token_para_atualizar(self, token_hash: str) -> CodigoRecuperacao | None:
        comando = (
            select(CodigoRecuperacao)
            .where(CodigoRecuperacao.token_hash == token_hash)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return self.db.scalar(comando)
