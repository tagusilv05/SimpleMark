"""Código de confirmação do login, enviado por e-mail depois da senha."""

import logging
import uuid
from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy.orm import Session

from core.excecoes import ErroNegocio
from core.parametros import codigo_login_validade_minutos
from core.seguranca import calcular_hash_codigo_login, gerar_codigo_login
from core.tempo import agora_utc
from models.models import Usuario
from repositories.codigo_login import RepositorioCodigoLogin
from services.LoginService.email import enviar_codigo_login

logger = logging.getLogger("simplemark.codigo_login")

# Por quanto tempo os códigos antigos ficam guardados. Enquanto existirem,
# o sorteio de um código novo recusa qualquer repetição.
RETENCAO_HISTORICO = timedelta(hours=24)
TENTATIVAS_DE_SORTEIO = 10


@dataclass
class DesafioLogin:
    id_desafio: uuid.UUID
    email_mascarado: str
    expira_em_segundos: int


def mascarar_email(email: str) -> str:
    """ana.souza@gmail.com vira a***@gmail.com."""
    local, _, dominio = email.partition("@")
    return f"{local[:1]}***@{dominio}"


class ServicoCodigoLogin:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.codigos = RepositorioCodigoLogin(db)

    def emitir(self, usuario: Usuario) -> DesafioLogin:
        """Gera um código novo, manda por e-mail e invalida os anteriores.

        O código só fica valendo se o e-mail saiu. Se o envio falhar, nada é
        gravado e a API responde 503. Quem chama já segura a trava da credencial.
        """
        agora = agora_utc()
        validade = timedelta(minutes=codigo_login_validade_minutos())

        self.codigos.apagar_anteriores_a(usuario.id, agora - RETENCAO_HISTORICO)
        self.codigos.encerrar_pendentes(usuario.id, agora)
        codigo, codigo_hash = self._sortear_inedito(usuario.id)
        registro = self.codigos.criar(usuario.id, codigo_hash, agora, agora + validade)
        id_desafio = registro.id
        email = usuario.email

        try:
            enviar_codigo_login(email, codigo)
        except Exception as exc:
            self.db.rollback()
            logger.exception("Falha ao enviar o código de login por e-mail.")
            raise ErroNegocio(
                "Não foi possível enviar o código de confirmação por e-mail. "
                "Tente novamente em instantes.",
                503,
            ) from exc

        self.db.commit()
        return DesafioLogin(
            id_desafio=id_desafio,
            email_mascarado=mascarar_email(email),
            expira_em_segundos=int(validade.total_seconds()),
        )

    def _sortear_inedito(self, id_usuario: uuid.UUID) -> tuple[str, str]:
        for _ in range(TENTATIVAS_DE_SORTEIO):
            codigo = gerar_codigo_login()
            codigo_hash = calcular_hash_codigo_login(id_usuario, codigo)
            if not self.codigos.existe_hash(id_usuario, codigo_hash):
                return codigo, codigo_hash
        raise ErroNegocio("Não foi possível gerar o código agora. Tente novamente.", 503)
