"""Recuperação de senha em duas etapas: pedir o código e redefinir.

Etapa 1 (solicitar): recebe o e-mail e envia um código de 6 dígitos para ele.
Etapa 2 (redefinir): confere o código e grava a nova senha.

Regras que seguem o login em duas etapas:
- O código vale poucos minutos, só pode ser usado uma vez e só o HMAC dele vai
  para o banco.
- Erros de código contam no mesmo contador do login (`tentativas_login_falhas`):
  cinco erros seguidos bloqueiam a conta. Assim não existe um caminho paralelo
  para tentar adivinhar códigos sem limite.
- A resposta da etapa 1 é a mesma exista a conta ou não, para não revelar quem
  tem cadastro. Se não há conta, nada é enviado e o id devolvido não vale.
- Pedir de novo dentro de INTERVALO_MINIMO não envia outro e-mail: devolve o
  desafio que já está em aberto (evita encher a caixa de entrada de alguém).
- Ao trocar a senha, todas as sessões abertas e os códigos de login pendentes
  da conta são encerrados.
"""

import hashlib
import hmac
import logging
import math
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from core.excecoes import ErroNegocio
from core.parametros import login_bloqueio_minutos, login_max_tentativas, segredo_jwt
from core.seguranca import gerar_codigo_login, gerar_hash_senha, verificar_senha
from core.tempo import agora_utc, como_utc
from models.acesso import Credencial
from repositories.administracao import RepositorioAdministracao
from repositories.codigo_login import RepositorioCodigoLogin
from repositories.credencial import RepositorioCredencial
from repositories.recuperacao_senha import RepositorioRecuperacaoSenha
from repositories.usuario import RepositorioUsuario
from services.LoginService.codigo_login import mascarar_email
from services.RecuperacaoService.email import enviar_codigo_recuperacao

logger = logging.getLogger("simplemark.recuperacao_senha")

# Por quanto tempo os códigos antigos ficam guardados. Enquanto existirem,
# o sorteio de um código novo recusa qualquer repetição.
RETENCAO_HISTORICO = timedelta(hours=24)
TENTATIVAS_DE_SORTEIO = 10
# Intervalo mínimo entre dois e-mails de recuperação para a mesma conta.
INTERVALO_MINIMO = timedelta(seconds=60)

MENSAGEM_CODIGO_INVALIDO = "Código de recuperação inválido. Peça um novo código."
MENSAGEM_CODIGO_EXPIRADO = "O código expirou. Peça um novo código."
MENSAGEM_CODIGO_INCORRETO = "Código incorreto. Verifique o e-mail e tente novamente."
MENSAGEM_SENHA_IGUAL = "A nova senha deve ser diferente da senha atual."


def validade_minutos() -> int:
    """Quanto tempo o código de recuperação vale, em minutos (padrão 10)."""
    return int(os.getenv("CODIGO_RECUPERACAO_VALIDADE_MINUTOS", "10"))


def calcular_hash_codigo(id_usuario: uuid.UUID, codigo: str) -> str:
    """HMAC do código, ligado ao usuário e a este uso.

    O prefixo "recuperacao:" faz o hash ser diferente do hash de um código de
    login, então um código de um fluxo nunca serve no outro.
    """
    mensagem = f"recuperacao:{id_usuario}:{codigo}".encode("utf-8")
    return hmac.new(segredo_jwt().encode("utf-8"), mensagem, hashlib.sha256).hexdigest()


def codigo_confere(hash_guardado: str, id_usuario: uuid.UUID, codigo: str) -> bool:
    """Compara o hash guardado com o do código informado, em tempo constante."""
    return hmac.compare_digest(hash_guardado, calcular_hash_codigo(id_usuario, codigo))


def _mensagem_bloqueio(restante: timedelta) -> str:
    """Mensagem de bloqueio com o tempo restante arredondado para cima, em minutos."""
    minutos = max(1, math.ceil(restante.total_seconds() / 60))
    unidade = "minuto" if minutos == 1 else "minutos"
    return (
        "Conta temporariamente bloqueada após várias tentativas incorretas. "
        f"Tente novamente em {minutos} {unidade}."
    )


@dataclass
class DesafioRecuperacao:
    """Resposta da primeira etapa: o desafio que espera o código."""

    id_desafio: uuid.UUID
    email_mascarado: str
    expira_em_segundos: int


class ServicoRecuperacaoSenha:
    """Pede o código de recuperação e redefine a senha."""

    def __init__(self, db: Session) -> None:
        """Guarda a sessão do banco e monta os repositórios usados."""
        self.db = db
        self.usuarios = RepositorioUsuario(db)
        self.credenciais = RepositorioCredencial(db)
        self.codigos = RepositorioRecuperacaoSenha(db)
        self.codigos_login = RepositorioCodigoLogin(db)

    # ------------------------------------------------------------------ etapa 1
    def solicitar(self, email: str) -> DesafioRecuperacao:
        """Envia o código de recuperação para o e-mail, se houver conta.

        Sem conta (ou com conta banida) não envia nada, mas responde igual.
        """
        validade = timedelta(minutes=validade_minutos())
        segundos = int(validade.total_seconds())
        mascarado = mascarar_email(email)

        usuario = self.usuarios.buscar_por_email(email)
        if usuario is None or RepositorioAdministracao(self.db).esta_banido(usuario.id):
            return DesafioRecuperacao(uuid.uuid4(), mascarado, segundos)

        # A trava da credencial serializa pedidos simultâneos da mesma conta.
        credencial = self.credenciais.buscar_para_atualizar(usuario.id)
        if credencial is None:
            self.db.rollback()
            return DesafioRecuperacao(uuid.uuid4(), mascarado, segundos)

        agora = agora_utc()
        recente = self.codigos.buscar_pendente_criado_apos(usuario.id, agora - INTERVALO_MINIMO, agora)
        if recente is not None:
            restante = max(1, int((como_utc(recente.expira_em) - agora).total_seconds()))
            id_recente = recente.id
            self.db.rollback()  # libera a trava; nada foi alterado
            return DesafioRecuperacao(id_recente, mascarado, restante)

        self.codigos.apagar_anteriores_a(usuario.id, agora - RETENCAO_HISTORICO)
        self.codigos.encerrar_pendentes(usuario.id, agora)
        codigo, codigo_hash = self._sortear_inedito(usuario.id)
        registro = self.codigos.criar(usuario.id, codigo_hash, agora, agora + validade)
        id_desafio = registro.id

        try:
            enviar_codigo_recuperacao(usuario.email, codigo, validade_minutos())
        except Exception as exc:
            self.db.rollback()
            logger.exception("Falha ao enviar o código de recuperação de senha por e-mail.")
            raise ErroNegocio(
                "Não foi possível enviar o código de recuperação por e-mail. "
                "Tente novamente em instantes.",
                503,
            ) from exc

        self.db.commit()
        return DesafioRecuperacao(id_desafio, mascarar_email(usuario.email), segundos)

    # ------------------------------------------------------------------ etapa 2
    def redefinir(self, id_desafio: uuid.UUID, codigo: str, nova_senha: str) -> None:
        """Confere o código e grava a nova senha.

        Código errado conta no contador de falhas do login. Código certo, mas
        senha igual à atual, é recusado sem gastar o código.
        """
        desafio = self.codigos.buscar(id_desafio)
        if desafio is None:
            raise ErroNegocio(MENSAGEM_CODIGO_INVALIDO)

        usuario = self.usuarios.buscar_por_id(desafio.id_usuario)
        credencial = self.credenciais.buscar_para_atualizar(desafio.id_usuario)
        if usuario is None or credencial is None:
            raise ErroNegocio(MENSAGEM_CODIGO_INVALIDO)

        agora = agora_utc()
        restante = self._bloqueio_restante(credencial, agora)
        if restante is not None:
            raise ErroNegocio(_mensagem_bloqueio(restante), 429)

        # Relê o código já com a linha travada: duas requisições com o mesmo
        # código não passam as duas.
        desafio = self.codigos.buscar_para_atualizar(id_desafio)
        if desafio is None or desafio.encerrado_em is not None:
            raise ErroNegocio(MENSAGEM_CODIGO_INVALIDO)

        if como_utc(desafio.expira_em) <= agora:
            desafio.encerrado_em = agora
            self.db.commit()
            raise ErroNegocio(MENSAGEM_CODIGO_EXPIRADO)

        if not codigo_confere(desafio.codigo_hash, usuario.id, codigo):
            restante = self._registrar_falha(credencial, agora)
            if restante is not None:
                self.codigos.encerrar_pendentes(usuario.id, agora)
                self.db.commit()
                raise ErroNegocio(_mensagem_bloqueio(restante), 429)
            raise ErroNegocio(MENSAGEM_CODIGO_INCORRETO)

        if RepositorioAdministracao(self.db).esta_banido(usuario.id):
            raise ErroNegocio("Esta conta foi banida pelo administrador.", 403)

        igual_a_atual, _ = verificar_senha(nova_senha, credencial.senha_hash)
        if igual_a_atual:
            self.db.rollback()  # libera a trava; o código continua valendo
            raise ErroNegocio(MENSAGEM_SENHA_IGUAL)

        # Código certo: grava a senha, gasta o código, zera o contador e derruba
        # as sessões abertas e os códigos de login pendentes.
        credencial.senha_hash = gerar_hash_senha(nova_senha)
        credencial.tentativas_login_falhas = 0
        credencial.bloqueado_ate = None
        desafio.encerrado_em = agora
        self.codigos_login.encerrar_pendentes(usuario.id, agora)
        self.codigos.encerrar_sessoes_abertas(usuario.id, agora)
        self.db.commit()

    # ---------------------------------------------------------------- auxiliares
    def _sortear_inedito(self, id_usuario: uuid.UUID) -> tuple[str, str]:
        """Sorteia um código cujo hash ainda não existe para o usuário.

        Devolve o código e o hash. Tenta até TENTATIVAS_DE_SORTEIO vezes e, se não
        achar um livre, levanta ErroNegocio 503.
        """
        for _ in range(TENTATIVAS_DE_SORTEIO):
            codigo = gerar_codigo_login()
            codigo_hash = calcular_hash_codigo(id_usuario, codigo)
            if not self.codigos.existe_hash(id_usuario, codigo_hash):
                return codigo, codigo_hash
        raise ErroNegocio("Não foi possível gerar o código agora. Tente novamente.", 503)

    def _bloqueio_restante(self, credencial: Credencial, agora: datetime) -> timedelta | None:
        """Tempo que falta de bloqueio, ou None.

        Bloqueio vencido é limpo junto com a contagem de falhas, sem commit.
        """
        if credencial.bloqueado_ate is None:
            return None
        limite = como_utc(credencial.bloqueado_ate)
        if limite > agora:
            return limite - agora
        credencial.bloqueado_ate = None
        credencial.tentativas_login_falhas = 0
        return None

    def _registrar_falha(self, credencial: Credencial, agora: datetime) -> timedelta | None:
        """Conta o código errado e bloqueia a conta ao atingir o limite de tentativas.

        Devolve a duração do bloqueio quando ele começa, ou None. Faz o commit.
        """
        credencial.tentativas_login_falhas += 1
        restante = None
        if credencial.tentativas_login_falhas >= login_max_tentativas():
            duracao = timedelta(minutes=login_bloqueio_minutos())
            credencial.bloqueado_ate = agora + duracao
            credencial.tentativas_login_falhas = 0
            restante = duracao
        self.db.commit()
        return restante