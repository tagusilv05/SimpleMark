"""Login em duas etapas: senha e código enviado por e-mail.

Etapa 1 (iniciar_login): confere e-mail ou CPF e senha e envia o código.
Etapa 2 (confirmar_login): confere o código e só então abre a sessão.

O bloqueio por tentativas vale para as duas etapas e usa o mesmo contador:
cinco erros seguidos, de senha ou de código, bloqueiam a conta. O contador só
volta a zero quando o login termina de verdade. Se zerasse ao acertar a senha,
quem conhece a senha poderia pedir um código novo e testar palpites sem parar.
"""

import math
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from core.excecoes import ErroNegocio
from core.parametros import login_bloqueio_minutos, login_max_tentativas
from core.seguranca import codigo_login_confere, gerar_token_acesso, verificar_senha
from core.tempo import agora_utc, como_utc
from core.validadores import normalizar_cpf, normalizar_email
from models.acesso import Credencial
from models.models import Usuario
from repositories.administracao import RepositorioAdministracao
from repositories.codigo_login import RepositorioCodigoLogin
from repositories.credencial import RepositorioCredencial
from repositories.usuario import RepositorioUsuario
from services.LoginService.codigo_login import DesafioLogin, ServicoCodigoLogin
from services.SessaoService.sessao import ServicoSessao

MENSAGEM_CREDENCIAL_INVALIDA = (
    "E-mail, CPF ou senha incorretos. Verifique os dados e tente novamente."
)
MENSAGEM_CODIGO_INVALIDO = "Código de confirmação inválido. Entre novamente para receber outro."
MENSAGEM_CODIGO_EXPIRADO = "O código expirou. Entre novamente para receber um novo código."
MENSAGEM_CODIGO_INCORRETO = "Código incorreto. Verifique o e-mail e tente novamente."


def _mensagem_bloqueio(restante: timedelta) -> str:
    """Mensagem de bloqueio com o tempo restante arredondado para cima, em minutos."""
    minutos = max(1, math.ceil(restante.total_seconds() / 60))
    unidade = "minuto" if minutos == 1 else "minutos"
    return (
        "Conta temporariamente bloqueada após várias tentativas de login incorretas. "
        f"Tente novamente em {minutos} {unidade}."
    )


@dataclass
class ResultadoLogin:
    """Token de acesso e usuário devolvidos pelo login."""

    token: str
    usuario: Usuario


class ServicoAutenticacao:
    """Autentica o usuário e abre a sessão de login."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.usuarios = RepositorioUsuario(db)
        self.credenciais = RepositorioCredencial(db)
        self.codigos = RepositorioCodigoLogin(db)

    # ------------------------------------------------------------------ etapa 1
    def iniciar_login(self, identificador: str, senha: str) -> DesafioLogin:
        """Confere a senha e envia o código por e-mail. Não abre sessão.

        A conta bloqueada responde 429 sem conferir a senha. Na quinta falha
        seguida, a conta fica bloqueada.
        """
        usuario = self._localizar(identificador)
        if usuario is None:
            raise ErroNegocio(MENSAGEM_CREDENCIAL_INVALIDA, 401)

        credencial = self.credenciais.buscar_para_atualizar(usuario.id)
        if credencial is None:
            raise ErroNegocio(MENSAGEM_CREDENCIAL_INVALIDA, 401)

        agora = agora_utc()
        restante = self._bloqueio_restante(credencial, agora)
        if restante is not None:
            raise ErroNegocio(_mensagem_bloqueio(restante), 429)

        valida, novo_hash = verificar_senha(senha, credencial.senha_hash)
        if not valida:
            restante = self._registrar_falha(credencial, agora)
            if restante is not None:
                raise ErroNegocio(_mensagem_bloqueio(restante), 429)
            raise ErroNegocio(MENSAGEM_CREDENCIAL_INVALIDA, 401)

        if novo_hash:
            credencial.senha_hash = novo_hash

        # Conta banida ou inativa não recebe código. A trava da credencial
        # continua segurada até o envio, então logins do mesmo usuário esperam.
        self._exigir_conta_ativa(usuario)
        return ServicoCodigoLogin(self.db).emitir(usuario)

    # ------------------------------------------------------------------ etapa 2
    def confirmar_login(self, id_desafio: uuid.UUID, codigo: str) -> ResultadoLogin:
        """Confere o código. Se estiver certo, consome o código e abre a sessão."""
        desafio = self.codigos.buscar(id_desafio)
        if desafio is None:
            raise ErroNegocio(MENSAGEM_CODIGO_INVALIDO, 401)

        usuario = self.usuarios.buscar_por_id(desafio.id_usuario)
        credencial = self.credenciais.buscar_para_atualizar(desafio.id_usuario)
        if usuario is None or credencial is None:
            raise ErroNegocio(MENSAGEM_CODIGO_INVALIDO, 401)

        agora = agora_utc()
        restante = self._bloqueio_restante(credencial, agora)
        if restante is not None:
            raise ErroNegocio(_mensagem_bloqueio(restante), 429)

        # Relê o código já com a linha travada: duas requisições com o mesmo
        # código não passam as duas.
        desafio = self.codigos.buscar_para_atualizar(id_desafio)
        if desafio is None or desafio.encerrado_em is not None:
            raise ErroNegocio(MENSAGEM_CODIGO_INVALIDO, 401)

        if como_utc(desafio.expira_em) <= agora:
            desafio.encerrado_em = agora
            self.db.commit()
            raise ErroNegocio(MENSAGEM_CODIGO_EXPIRADO, 401)

        if not codigo_login_confere(desafio.codigo_hash, usuario.id, codigo):
            restante = self._registrar_falha(credencial, agora)
            if restante is not None:
                self.codigos.encerrar_pendentes(usuario.id, agora)
                self.db.commit()
                raise ErroNegocio(_mensagem_bloqueio(restante), 429)
            raise ErroNegocio(MENSAGEM_CODIGO_INCORRETO, 401)

        # Código certo: gasta o código e zera o contador antes de qualquer outra coisa.
        desafio.encerrado_em = agora
        credencial.tentativas_login_falhas = 0
        credencial.bloqueado_ate = None
        self.db.commit()

        self._exigir_conta_ativa(usuario)
        sessao = ServicoSessao(self.db).abrir(usuario.id)
        return ResultadoLogin(token=gerar_token_acesso(usuario.id, sessao.id), usuario=usuario)

    # ---------------------------------------------------------------- auxiliares
    def _exigir_conta_ativa(self, usuario: Usuario) -> None:
        if RepositorioAdministracao(self.db).esta_banido(usuario.id):
            raise ErroNegocio("Esta conta foi banida pelo administrador.", 403)

        if not usuario.status:
            if usuario.profissional is not None:
                raise ErroNegocio(
                    "O cadastro do profissional de saúde ainda aguarda a validação do administrador.",
                    403,
                )
            raise ErroNegocio("Esta conta ainda não está ativa.", 403)

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
        """Conta a senha errada e bloqueia a conta ao atingir o limite de tentativas.

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

    def _localizar(self, identificador: str) -> Usuario | None:
        """Busca o usuário por e-mail (se houver "@") ou por CPF.

        Identificador mal formatado responde 422.
        """
        texto = identificador.strip()
        if "@" in texto:
            try:
                email = normalizar_email(texto)
            except ValueError as exc:
                raise ErroNegocio(str(exc), 422) from exc
            return self.usuarios.buscar_por_email(email)
        try:
            cpf = normalizar_cpf(texto)
        except ValueError as exc:
            raise ErroNegocio(str(exc), 422) from exc
        return self.usuarios.buscar_por_cpf(cpf)
