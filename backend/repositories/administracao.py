import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session, selectinload

from models.acesso import SessaoLogin
from models.administracao import Banimento, LogAcaoAdministrador
from models.models import Paciente, Profissional


class RepositorioAdministracao:
    def __init__(self, db: Session) -> None:
        self.db = db

    def ids_usuarios_banidos(self) -> set[uuid.UUID]:
        consulta = select(Banimento.id_usuario)
        return set(self.db.scalars(consulta).all())

    def esta_banido(self, id_usuario: uuid.UUID) -> bool:
        return self.buscar_banimento(id_usuario) is not None

    def buscar_banimento(self, id_usuario: uuid.UUID) -> Banimento | None:
        return self.db.scalar(select(Banimento).where(Banimento.id_usuario == id_usuario))

    def listar_profissionais(self) -> list[Profissional]:
        consulta = (
            select(Profissional)
            .join(Profissional.usuario)
            .options(selectinload(Profissional.usuario))
            .order_by(Profissional.id_profissional)
        )
        return list(self.db.scalars(consulta))

    def listar_pacientes(self) -> list[Paciente]:
        consulta = (
            select(Paciente)
            .join(Paciente.usuario)
            .options(selectinload(Paciente.usuario))
            .order_by(Paciente.id_paciente)
        )
        return list(self.db.scalars(consulta))

    def buscar_profissional(self, id_profissional: int) -> Profissional | None:
        return self.db.get(Profissional, id_profissional)

    def buscar_paciente(self, id_paciente: int) -> Paciente | None:
        return self.db.get(Paciente, id_paciente)

    def adicionar_banimento(self, banimento: Banimento) -> Banimento:
        self.db.add(banimento)
        return banimento

    def encerrar_sessoes(self, id_usuario: uuid.UUID, agora: datetime) -> None:
        comando = (
            update(SessaoLogin)
            .where(
                SessaoLogin.id_usuario == id_usuario,
                SessaoLogin.encerrada_em.is_(None),
            )
            .values(encerrada_em=agora)
            .execution_options(synchronize_session=False)
        )
        self.db.execute(comando)

    def adicionar_log(self, log: LogAcaoAdministrador) -> LogAcaoAdministrador:
        self.db.add(log)
        return log

    def listar_logs(self) -> list[LogAcaoAdministrador]:
        consulta = select(LogAcaoAdministrador).order_by(LogAcaoAdministrador.realizada_em.desc())
        return list(self.db.scalars(consulta))
