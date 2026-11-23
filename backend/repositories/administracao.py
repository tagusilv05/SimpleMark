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
        """Guarda a sessão do banco usada nas consultas.

        Args:
            db (Session): Sessão do banco de dados.
        """
        self.db = db

    def ids_usuarios_banidos(self) -> set[uuid.UUID]:
        """Ids de todos os usuários com banimento registrado.

        Returns:
            set[uuid.UUID]: Ids dos usuários banidos.
        """
        consulta = select(Banimento.id_usuario)
        return set(self.db.scalars(consulta).all())

    def esta_banido(self, id_usuario: uuid.UUID) -> bool:
        """Indica se o usuário tem banimento registrado.

        Args:
            id_usuario (uuid.UUID): Id do usuário.

        Returns:
            bool: True se o usuário está banido.
        """
        return self.buscar_banimento(id_usuario) is not None

    def buscar_banimento(self, id_usuario: uuid.UUID) -> Banimento | None:
        """Banimento do usuário, ou None se ele não estiver banido.

        Args:
            id_usuario (uuid.UUID): Id do usuário.

        Returns:
            Banimento | None: Banimento encontrado, ou None.
        """
        return self.db.scalar(select(Banimento).where(Banimento.id_usuario == id_usuario))

    def listar_profissionais(self) -> list[Profissional]:
        """Todos os profissionais, com o usuário já carregado, em ordem de id.

        Returns:
            list[Profissional]: Profissionais cadastrados.
        """
        consulta = (
            select(Profissional)
            .join(Profissional.usuario)
            .options(selectinload(Profissional.usuario))
            .order_by(Profissional.id_profissional)
        )
        return list(self.db.scalars(consulta))

    def listar_pacientes(self) -> list[Paciente]:
        """Todos os pacientes, com o usuário já carregado, em ordem de id.

        Returns:
            list[Paciente]: Pacientes cadastrados.
        """
        consulta = (
            select(Paciente)
            .join(Paciente.usuario)
            .options(selectinload(Paciente.usuario))
            .order_by(Paciente.id_paciente)
        )
        return list(self.db.scalars(consulta))

    def buscar_profissional(self, id_profissional: int) -> Profissional | None:
        """Profissional pelo id, ou None se não existir.

        Args:
            id_profissional (int): Id do profissional.

        Returns:
            Profissional | None: Profissional encontrado, ou None.
        """
        return self.db.get(Profissional, id_profissional)

    def buscar_paciente(self, id_paciente: int) -> Paciente | None:
        """Paciente pelo id, ou None se não existir.

        Args:
            id_paciente (int): Id do paciente.

        Returns:
            Paciente | None: Paciente encontrado, ou None.
        """
        return self.db.get(Paciente, id_paciente)

    def adicionar_banimento(self, banimento: Banimento) -> Banimento:
        """Inclui o banimento na sessão, sem flush nem commit.

        Args:
            banimento (Banimento): Banimento a incluir.

        Returns:
            Banimento: O mesmo banimento recebido.
        """
        self.db.add(banimento)
        return banimento

    def encerrar_sessoes(self, id_usuario: uuid.UUID, agora: datetime) -> None:
        """Encerra as sessões de login ainda abertas do usuário.

        UPDATE em lote com synchronize_session=False: objetos SessaoLogin já
        carregados na sessão não enxergam a mudança.

        Args:
            id_usuario (uuid.UUID): Id do usuário.
            agora (datetime): Instante gravado como encerramento.
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
        """Inclui o log de ação na sessão, sem flush nem commit.

        Args:
            log (LogAcaoAdministrador): Log a incluir.

        Returns:
            LogAcaoAdministrador: O mesmo log recebido.
        """
        self.db.add(log)
        return log

    def listar_logs(self) -> list[LogAcaoAdministrador]:
        """Logs de ações administrativas, do mais recente ao mais antigo.

        Returns:
            list[LogAcaoAdministrador]: Logs ordenados por data decrescente.
        """
        consulta = select(LogAcaoAdministrador).order_by(LogAcaoAdministrador.realizada_em.desc())
        return list(self.db.scalars(consulta))
