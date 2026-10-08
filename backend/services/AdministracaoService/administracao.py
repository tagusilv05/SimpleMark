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
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = RepositorioAdministracao(db)

    def esta_banido(self, id_usuario) -> bool:
        return self.repo.esta_banido(id_usuario)

    def sem_banidos(self, profissionais: list[Profissional]) -> list[Profissional]:
        banidos = self.repo.ids_usuarios_banidos()
        return [item for item in profissionais if item.id_usuario not in banidos]

    def listar_ids_usuarios(self) -> IdsUsuariosResposta:
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
        if self.repo.esta_banido(id_usuario):
            raise ErroNegocio("Este profissional foi banido e não pode ser validado.", 409)

    def recusar_validacao_se_banido(self, id_profissional: int) -> None:
        profissional = self.repo.buscar_profissional(id_profissional)
        if profissional is not None:
            self.recusar_se_banido(profissional.id_usuario)

    def banir_profissional(self, id_profissional: int, admin: Usuario, motivo: str | None) -> None:
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