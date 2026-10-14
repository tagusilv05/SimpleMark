"""Consultas de banimentos, sessões e logs usadas na administração."""

import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session, selectinload

from models.acesso import SessaoLogin
from models.administracao import Banimento, LogAcaoAdministrador
from models.models import Paciente, Profissional


class RepositorioAdministracao:
    """Consultas da área administrativa. Não aplica regra de negócio."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def ids_usuarios_banidos(self) -> set[uuid.UUID]:
        """Ids de todos os usuários com banimento registrado."""
        consulta = select(Banimento.id_usuario)
        return set(self.db.scalars(consulta).all())

    def esta_banido(self, id_usuario: uuid.UUID) -> bool:
        """Indica se o usuário tem banimento registrado."""
        return self.buscar_banimento(id_usuario) is not None

    def buscar_banimento(self, id_usuario: uuid.UUID) -> Banimento | None:
        """Banimento do usuário, ou None se ele não estiver banido."""
        return self.db.scalar(select(Banimento).where(Banimento.id_usuario == id_usuario))

    def listar_profissionais(self) -> list[Profissional]:
        """Todos os profissionais, com o usuário já carregado, em ordem de id."""
        consulta = (
            select(Profissional)
            .join(Profissional.usuario)
            .options(selectinload(Profissional.usuario))
            .order_by(Profissional.id_profissional)
        )
        return list(self.db.scalars(consulta))

    def listar_pacientes(self) -> list[Paciente]:
        """Todos os pacientes, com o usuário já carregado, em ordem de id."""
        consulta = (
            select(Paciente)
            .join(Paciente.usuario)
            .options(selectinload(Paciente.usuario))
            .order_by(Paciente.id_paciente)
        )
        return list(self.db.scalars(consulta))

    def buscar_profissional(self, id_profissional: int) -> Profissional | None:
        """Profissional pelo id, ou None se não existir."""
        return self.db.get(Profissional, id_profissional)

    def buscar_paciente(self, id_paciente: int) -> Paciente | None:
        """Paciente pelo id, ou None se não existir."""
        return self.db.get(Paciente, id_paciente)

    def adicionar_banimento(self, banimento: Banimento) -> Banimento:
        """Inclui o banimento na sessão, sem flush nem commit."""
        self.db.add(banimento)
        return banimento

    def encerrar_sessoes(self, id_usuario: uuid.UUID, agora: datetime) -> None:
        """Encerra as sessões de login ainda abertas do usuário.

        UPDATE em lote com synchronize_session=False: objetos SessaoLogin já
        carregados na sessão não enxergam a mudança.
        """
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
        """Inclui o log de ação na sessão, sem flush nem commit."""
        self.db.add(log)
        return log

    def listar_logs(self) -> list[LogAcaoAdministrador]:
        """Logs de ações administrativas, do mais recente ao mais antigo."""
        consulta = select(LogAcaoAdministrador).order_by(LogAcaoAdministrador.realizada_em.desc())
        return list(self.db.scalars(consulta))
