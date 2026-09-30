"""Sessão de login: abrir, validar, renovar e encerrar."""

import uuid
from datetime import timedelta

from sqlalchemy.orm import Session

from core.excecoes import ErroNegocio
from core.parametros import sessao_inatividade_horas
from core.tempo import agora_utc, como_utc
from models.acesso import SessaoLogin
from repositories.sessao_login import RepositorioSessaoLogin

# A última atividade só é regravada se a gravada tiver mais que isso.
INTERVALO_RENOVACAO = timedelta(minutes=5)

MENSAGEM_TOKEN_INVALIDO = "Token inválido. Entre novamente."


class ServicoSessao:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.sessoes = RepositorioSessaoLogin(db)

    def abrir(self, id_usuario: uuid.UUID) -> SessaoLogin:
        sessao = self.sessoes.criar(id_usuario, agora_utc())
        self.db.commit()
        return sessao

    def validar_e_renovar(self, id_sessao: uuid.UUID, id_usuario: uuid.UUID) -> SessaoLogin:
        """Confere se a sessão ainda vale e empurra o prazo de inatividade.

        Sessão encerrada ou parada pelo tempo configurado responde 401.
        """
        agora = agora_utc()
        sessao = self.sessoes.buscar(id_sessao, id_usuario)
        if sessao is None:
            raise ErroNegocio(MENSAGEM_TOKEN_INVALIDO, 401)
        if sessao.encerrada_em is not None:
            raise ErroNegocio("Sessão encerrada. Entre novamente.", 401)

        parada_ha = agora - como_utc(sessao.ultima_atividade_em)
        if parada_ha >= timedelta(hours=sessao_inatividade_horas()):
            raise ErroNegocio("Sua sessão expirou por inatividade. Entre novamente.", 401)

        if parada_ha >= INTERVALO_RENOVACAO:
            self.sessoes.registrar_atividade(sessao.id, agora, agora - INTERVALO_RENOVACAO)
            self.db.commit()
        return sessao

    def encerrar(self, sessao: SessaoLogin) -> None:
        sessao.encerrada_em = agora_utc()
        self.db.commit()
