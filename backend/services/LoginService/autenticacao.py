"""Login por e-mail ou CPF, com bloqueio depois de senhas erradas seguidas."""

import math
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from core.excecoes import ErroNegocio
from core.parametros import login_bloqueio_minutos, login_max_tentativas
from core.seguranca import gerar_token_acesso, verificar_senha
from core.tempo import agora_utc, como_utc
from core.validadores import normalizar_cpf, normalizar_email
from models.acesso import Credencial
from models.models import Usuario
from repositories.administracao import RepositorioAdministracao
from repositories.credencial import RepositorioCredencial
from repositories.usuario import RepositorioUsuario
from services.SessaoService.sessao import ServicoSessao

MENSAGEM_CREDENCIAL_INVALIDA = (
    "E-mail, CPF ou senha incorretos. Verifique os dados e tente novamente."
)


def _mensagem_bloqueio(restante: timedelta) -> str:
    minutos = max(1, math.ceil(restante.total_seconds() / 60))
    unidade = "minuto" if minutos == 1 else "minutos"
    return (
        "Conta temporariamente bloqueada após várias tentativas de login incorretas. "
        f"Tente novamente em {minutos} {unidade}."
    )


@dataclass
class ResultadoLogin:
    token: str
    usuario: Usuario


class ServicoAutenticacao:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.usuarios = RepositorioUsuario(db)
        self.credenciais = RepositorioCredencial(db)

    def autenticar(self, identificador: str, senha: str) -> ResultadoLogin:
        """Entra com e-mail ou CPF.

        A conta bloqueada responde 429 sem conferir a senha. Na quinta senha
        errada seguida, a conta fica bloqueada. Acertar a senha zera a contagem.
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
        credencial.tentativas_login_falhas = 0
        credencial.bloqueado_ate = None
        self.db.commit()

        if RepositorioAdministracao(self.db).esta_banido(usuario.id):
            raise ErroNegocio("Esta conta foi banida pelo administrador.", 403)

        if not usuario.status:
            if usuario.profissional is not None:
                raise ErroNegocio(
                    "O cadastro do profissional de saúde ainda aguarda a validação do administrador.",
                    403,
                )
            raise ErroNegocio("Esta conta ainda não está ativa.", 403)

        sessao = ServicoSessao(self.db).abrir(usuario.id)
        return ResultadoLogin(token=gerar_token_acesso(usuario.id, sessao.id), usuario=usuario)

    def _bloqueio_restante(self, credencial: Credencial, agora: datetime) -> timedelta | None:
        if credencial.bloqueado_ate is None:
            return None
        limite = como_utc(credencial.bloqueado_ate)
        if limite > agora:
            return limite - agora
        credencial.bloqueado_ate = None
        credencial.tentativas_login_falhas = 0
        return None

    def _registrar_falha(self, credencial: Credencial, agora: datetime) -> timedelta | None:
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