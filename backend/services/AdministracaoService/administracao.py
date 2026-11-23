"""Regras da tela de administração: consulta de IDs, banimento e logs."""

from sqlalchemy.orm import Session

from core.excecoes import ErroNegocio
from core.tempo import agora_utc
from models.administracao import Banimento, LogAcaoAdministrador
from models.models import Profissional, Usuario
from repositories.administracao import RepositorioAdministracao
from schemas.administracao import (
    IdsUsuariosResposta,
    LogAcaoResposta,
    PacienteIdResposta,
    ProfissionalIdResposta,
)


class ServicoAdministracao:
    """Consulta de IDs, banimento de contas e registro das ações do administrador."""

    def __init__(self, db: Session) -> None:
        """Guarda a sessão do banco e monta o repositório de administração.

        Args:
            db (Session): Sessão do SQLAlchemy usada nas consultas e gravações.
        """
        self.db = db
        self.repo = RepositorioAdministracao(db)

    def esta_banido(self, id_usuario) -> bool:
        """Diz se o usuário tem banimento registrado.

        Args:
            id_usuario (uuid.UUID): ID do usuário a verificar.

        Returns:
            bool: ``True`` se houver banimento registrado para o usuário.
        """
        return self.repo.esta_banido(id_usuario)

    def sem_banidos(self, profissionais: list[Profissional]) -> list[Profissional]:
        """Remove da lista os profissionais cujas contas estão banidas.

        Args:
            profissionais (list[Profissional]): Profissionais a filtrar.

        Returns:
            list[Profissional]: Os profissionais cujas contas não estão banidas.
        """
        banidos = self.repo.ids_usuarios_banidos()
        return [item for item in profissionais if item.id_usuario not in banidos]

    def listar_ids_usuarios(self) -> IdsUsuariosResposta:
        """Lista os IDs de profissionais e pacientes, deixando de fora os banidos.

        Returns:
            IdsUsuariosResposta: IDs dos profissionais e dos pacientes não banidos.
        """
        banidos = self.repo.ids_usuarios_banidos()
        profissionais = [
            ProfissionalIdResposta.de_profissional(item)
            for item in self.repo.listar_profissionais()
            if item.id_usuario not in banidos
        ]
        pacientes = [
            PacienteIdResposta.de_paciente(item)
            for item in self.repo.listar_pacientes()
            if item.id_usuario not in banidos
        ]
        return IdsUsuariosResposta(profissionais=profissionais, pacientes=pacientes)

    def registrar_validacao(self, admin: Usuario, id_profissional: int, id_usuario_alvo) -> None:
        """Grava no log a validação do profissional e faz o commit.

        Args:
            admin (Usuario): Administrador que validou o cadastro.
            id_profissional (int): ID do profissional validado.
            id_usuario_alvo (uuid.UUID): ID do usuário do profissional validado.
        """
        self._registrar_log(
            admin=admin,
            acao="validar_profissional",
            alvo_tipo="profissional",
            alvo_id=id_profissional,
            id_usuario_alvo=id_usuario_alvo,
            detalhe="Cadastro do profissional validado.",
        )
        self.db.commit()

    def recusar_se_banido(self, id_usuario) -> None:
        """Responde 409 se o usuário estiver banido, impedindo a validação.

        Args:
            id_usuario (uuid.UUID): ID do usuário a verificar.

        Raises:
            ErroNegocio: Com status 409, quando o usuário está banido.
        """
        if self.repo.esta_banido(id_usuario):
            raise ErroNegocio("Este profissional foi banido e não pode ser validado.", 409)

    def recusar_validacao_se_banido(self, id_profissional: int) -> None:
        """Recusa a validação (409) se o profissional estiver banido.

        Profissional inexistente passa sem erro.

        Args:
            id_profissional (int): ID do profissional a validar.

        Raises:
            ErroNegocio: Com status 409, quando o profissional está banido.
        """
        profissional = self.repo.buscar_profissional(id_profissional)
        if profissional is not None:
            self.recusar_se_banido(profissional.id_usuario)

    def banir_profissional(self, id_profissional: int, admin: Usuario, motivo: str | None) -> None:
        """Bane a conta do profissional.

        Responde 404 se ele não existir. As demais regras ficam em _banir.

        Args:
            id_profissional (int): ID do profissional a banir.
            admin (Usuario): Administrador que realiza o banimento.
            motivo (str | None): Motivo do banimento, opcional.

        Raises:
            ErroNegocio: Com status 404, quando o profissional não existe.
        """
        profissional = self.repo.buscar_profissional(id_profissional)
        if profissional is None:
            raise ErroNegocio("Não encontramos este profissional de saúde.", 404)
        self._banir(
            usuario=profissional.usuario,
            admin=admin,
            acao="banir_profissional",
            alvo_tipo="profissional",
            alvo_id=id_profissional,
            motivo=motivo,
        )

    def banir_paciente(self, id_paciente: int, admin: Usuario, motivo: str | None) -> None:
        """Bane a conta do paciente.

        Responde 404 se ele não existir. As demais regras ficam em _banir.

        Args:
            id_paciente (int): ID do paciente a banir.
            admin (Usuario): Administrador que realiza o banimento.
            motivo (str | None): Motivo do banimento, opcional.

        Raises:
            ErroNegocio: Com status 404, quando o paciente não existe.
        """
        paciente = self.repo.buscar_paciente(id_paciente)
        if paciente is None:
            raise ErroNegocio("Não encontramos este paciente.", 404)
        self._banir(
            usuario=paciente.usuario,
            admin=admin,
            acao="banir_paciente",
            alvo_tipo="paciente",
            alvo_id=id_paciente,
            motivo=motivo,
        )

    def listar_logs(self) -> list[LogAcaoResposta]:
        """Lista as ações registradas pelos administradores.

        Returns:
            list[LogAcaoResposta]: Os registros de ações dos administradores.
        """
        return [LogAcaoResposta.de_log(item) for item in self.repo.listar_logs()]

    def _banir(
        self,
        usuario: Usuario,
        admin: Usuario,
        acao: str,
        alvo_tipo: str,
        alvo_id: int,
        motivo: str | None,
    ) -> None:
        """Registra o banimento, encerra as sessões abertas do usuário e grava o log.

        Administrador não pode ser banido (403) e conta já banida responde 409.
        Faz o commit.

        Args:
            usuario (Usuario): Usuário cuja conta será banida.
            admin (Usuario): Administrador que realiza o banimento.
            acao (str): Nome da ação gravada no log.
            alvo_tipo (str): Tipo do alvo gravado no log (profissional ou paciente).
            alvo_id (int): ID do profissional ou do paciente banido.
            motivo (str | None): Motivo do banimento; vazio vira ``None``.

        Raises:
            ErroNegocio: Com status 403, quando o usuário é administrador, ou 409,
                quando a conta já está banida.
        """
        if usuario.administrador is not None:
            raise ErroNegocio("Não é permitido banir um administrador.", 403)
        if self.repo.esta_banido(usuario.id):
            raise ErroNegocio("Esta conta já está banida.", 409)

        agora = agora_utc()
        motivo_limpo = (motivo or "").strip() or None
        self.repo.adicionar_banimento(
            Banimento(
                id_usuario=usuario.id,
                id_administrador=admin.administrador.id_administrador,
                motivo=motivo_limpo,
                banido_em=agora,
            )
        )
        self.repo.encerrar_sessoes(usuario.id, agora)
        self._registrar_log(
            admin=admin,
            acao=acao,
            alvo_tipo=alvo_tipo,
            alvo_id=alvo_id,
            id_usuario_alvo=usuario.id,
            detalhe=motivo_limpo or "Conta banida pelo administrador.",
        )
        self.db.commit()

    def _registrar_log(
        self,
        admin: Usuario,
        acao: str,
        alvo_tipo: str,
        alvo_id: int,
        id_usuario_alvo,
        detalhe: str | None,
    ) -> None:
        """Adiciona o registro da ação do administrador, sem fazer commit.

        Args:
            admin (Usuario): Administrador que realizou a ação.
            acao (str): Nome da ação.
            alvo_tipo (str): Tipo do alvo da ação.
            alvo_id (int): ID do alvo da ação.
            id_usuario_alvo (uuid.UUID): ID do usuário afetado pela ação.
            detalhe (str | None): Texto complementar do registro.
        """
        self.repo.adicionar_log(
            LogAcaoAdministrador(
                id_administrador=admin.administrador.id_administrador,
                acao=acao,
                alvo_tipo=alvo_tipo,
                alvo_id=alvo_id,
                id_usuario_alvo=id_usuario_alvo,
                detalhe=detalhe,
                realizada_em=agora_utc(),
            )
        )