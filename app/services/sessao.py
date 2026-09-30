# Arquivo criado por Gustavo
"""Sessão de login: abrir, validar, renovar e encerrar (RNF14)."""

import uuid
from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ErroNegocio
from app.core.tempo import agora_utc, como_utc
from app.models.sessao import Sessao
from app.repositories.sessao import RepositorioSessao

# A última atividade só é regravada se a gravada tiver mais que isso. Sem este intervalo,
# toda requisição faria um UPDATE. Para uma janela de 24h, 5 minutos de precisão bastam.
INTERVALO_RENOVACAO = timedelta(minutes=5)

MENSAGEM_TOKEN_INVALIDO = "Token inválido. Entre novamente."


class ServicoSessao:
    def __init__(self, db: Session):
        self.db = db
        self.sessoes = RepositorioSessao(db)

    def abrir(self, id_usuario: int) -> Sessao:
        """Cria a sessão de um login que acabou de dar certo.

        Passo a passo:
        1. Insere a sessão com o horário atual.
        2. Faz commit, para a sessão existir antes de o token sair da API.
        """
        sessao = self.sessoes.criar(id_usuario, agora_utc())
        self.db.commit()
        return sessao

    def validar_e_renovar(self, id_sessao: uuid.UUID, id_usuario: int) -> Sessao:
        """Confere se a sessão ainda vale e registra que a conta está em uso.

        Passo a passo:
        1. Busca a sessão pelo id e pelo dono. Não achou: token inválido (401).
        2. Sessão encerrada por logout: 401.
        3. Última atividade há 24h ou mais: a sessão expirou por inatividade (401).
        4. Senão, a sessão vale. Se a última atividade já tem mais de 5 minutos,
           grava o momento atual, o que empurra o prazo de 24h para frente.
        5. O commit vem na hora: se a rota falhar depois, o uso já foi registrado.
        """
        agora = agora_utc()
        sessao = self.sessoes.buscar(id_sessao, id_usuario)
        if sessao is None:
            raise ErroNegocio(MENSAGEM_TOKEN_INVALIDO, 401)
        if sessao.encerrada_em is not None:
            raise ErroNegocio("Sessão encerrada. Entre novamente.", 401)

        parada_ha = agora - como_utc(sessao.ultima_atividade_em)
        if parada_ha >= timedelta(hours=settings.sessao_inatividade_horas):
            raise ErroNegocio("Sua sessão expirou por inatividade. Entre novamente.", 401)

        if parada_ha >= INTERVALO_RENOVACAO:
            self.sessoes.registrar_atividade(sessao.id, agora, agora - INTERVALO_RENOVACAO)
            self.db.commit()
        return sessao

    def encerrar(self, sessao: Sessao) -> None:
        """Encerra a sessão (logout). O token dela deixa de valer na hora."""
        sessao.encerrada_em = agora_utc()
        self.db.commit()
