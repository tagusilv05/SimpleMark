import uuid
from datetime import datetime

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from models.acesso import CodigoLogin


class RepositorioCodigoLogin:
    """Consultas de codigo_login. Não aplica regra de negócio."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def criar(
        self,
        id_usuario: uuid.UUID,
        codigo_hash: str,
        agora: datetime,
        expira_em: datetime,
    ) -> CodigoLogin:
        codigo = CodigoLogin(
            id_usuario=id_usuario,
            codigo_hash=codigo_hash,
            criado_em=agora,
            expira_em=expira_em,
        )
        self.db.add(codigo)
        self.db.flush()
        return codigo

    def buscar(self, id_codigo: uuid.UUID) -> CodigoLogin | None:
        return self.db.get(CodigoLogin, id_codigo)

    def buscar_para_atualizar(self, id_codigo: uuid.UUID) -> CodigoLogin | None:
        """Trava a linha: dois envios do mesmo código ao mesmo tempo não passam juntos."""
        comando = (
            select(CodigoLogin)
            .where(CodigoLogin.id == id_codigo)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return self.db.execute(comando).scalar_one_or_none()

    def existe_hash(self, id_usuario: uuid.UUID, codigo_hash: str) -> bool:
        comando = select(CodigoLogin.id).where(
            CodigoLogin.id_usuario == id_usuario,
            CodigoLogin.codigo_hash == codigo_hash,
        )
        return self.db.scalar(comando) is not None

    def encerrar_pendentes(self, id_usuario: uuid.UUID, agora: datetime) -> None:
        comando = (
            update(CodigoLogin)
            .where(CodigoLogin.id_usuario == id_usuario, CodigoLogin.encerrado_em.is_(None))
            .values(encerrado_em=agora)
            .execution_options(synchronize_session=False)
        )
        self.db.execute(comando)

    def apagar_anteriores_a(self, id_usuario: uuid.UUID, limite: datetime) -> None:
        comando = (
            delete(CodigoLogin)
            .where(CodigoLogin.id_usuario == id_usuario, CodigoLogin.criado_em < limite)
            .execution_options(synchronize_session=False)
        )
        self.db.execute(comando)
