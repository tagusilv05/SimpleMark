# Arquivo criado por Victor e Gustavo
"""Login por e-mail ou CPF e emissão do token de acesso."""

import math
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ErroNegocio
from app.core.security import gerar_token_acesso, verificar_senha
from app.core.tempo import agora_utc, como_utc
from app.core.validators import normalizar_cpf, normalizar_email
from app.models.usuario import Usuario
from app.repositories.usuario import RepositorioUsuario
from app.services.sessao import ServicoSessao

MENSAGEM_CREDENCIAL_INVALIDA = (
    "E-mail, CPF ou senha incorretos. Verifique os dados e tente novamente."
)


def _mensagem_bloqueio(restante: timedelta) -> str:
    """Frase de conta bloqueada, com a causa e quanto falta para tentar de novo (RNF3)."""
    minutos = max(1, math.ceil(restante.total_seconds() / 60))
    unidade = "minuto" if minutos == 1 else "minutos"
    return (
        "Conta temporariamente bloqueada após várias tentativas de login incorretas. "
        f"Tente novamente em {minutos} {unidade}."
    )

@dataclass
class ResultadoLogin:
    """Token e conta de um login aceito."""

    token: str
    usuario: Usuario


class ServicoAutenticacao:
    """Confere e-mail ou CPF e senha, e devolve o token.

    A rota só entrega o JSON. A decisão de aceitar ou recusar fica aqui.
    """

    def __init__(self, db: Session) -> None:
        """Guarda a sessão da requisição e o repositório de usuário.

        Passo a passo:
        1. Recebe a sessão aberta por get_db.
        2. Cria o repositório que consulta a tabela usuario nessa mesma sessão.
        """
        self.db = db
        self.usuarios = RepositorioUsuario(db)

    # Método para autenticar o usuário. Indentificador pode ser e-mail ou CPF, senha é a senha do usuário.
    def autenticar(self, identificador: str, senha: str) -> ResultadoLogin:
        """Entra com e-mail ou CPF e devolve o token.

        Passo a passo:
        1. Se o identificador tem @, trata como e-mail. Senão, trata como CPF.
        2. Busca a conta. Se não existir, responde a mesma frase de senha errada.
        3. Trava a linha da conta, para duas tentativas simultâneas não passarem juntas.
        4. Se a conta está bloqueada, recusa com 429 sem nem olhar a senha.
        5. Compara a senha com o hash Argon2.
        6. Se não bater, conta a falha. Na quinta seguida, bloqueia a conta.
        7. Se bater, zera o contador de falhas e grava.
        8. Se a conta estiver inativa, recusa o login.
           No profissional de saúde, a mensagem pede a validação do administrador.
        9. Se a conta estiver ativa, abre uma sessão no banco, assina o JWT com o id do
           usuário e o id da sessão, e devolve a conta.
        """
        # Utiliza o método _localizar, que está própria classe para buscar o usuário.
        usuario = self._localizar(identificador)
        # Se o usuário não for encontrado, retorna um erro de credencial inválida.
        if usuario is None:
            raise ErroNegocio(MENSAGEM_CREDENCIAL_INVALIDA, 401)

        # Trava a linha da conta até o commit. Sem isso, 100 tentativas simultâneas
        # leriam o contador em 0 ao mesmo tempo e todas teriam a senha conferida.
        usuario = self.usuarios.buscar_por_id_para_atualizar(usuario.id)
        agora = agora_utc()

        # Conta bloqueada: nem confere a senha. Se conferisse, quem estivesse
        # adivinhando ficaria sabendo quando acertou, mesmo bloqueado.
        restante = self._bloqueio_restante(usuario, agora)
        if restante is not None:
            raise ErroNegocio(_mensagem_bloqueio(restante), 429)

        # Verifica se a senha é válida.
        valida, novo_hash = verificar_senha(senha, usuario.senha_hash)

        # Se a senha não for válida, conta a falha e recusa.
        if not valida:
            restante = self._registrar_falha(usuario, agora)
            if restante is not None:
                # Esta foi a falha que bloqueou a conta. Avisa já, em vez de um 401.
                raise ErroNegocio(_mensagem_bloqueio(restante), 429)
            raise ErroNegocio(MENSAGEM_CREDENCIAL_INVALIDA, 401)

        # Se a senha for válida, atualiza o hash da senha.
        if novo_hash:
            usuario.senha_hash = novo_hash

        # Acertou a senha: a sequência de falhas acabou.
        usuario.tentativas_login_falhas = 0
        usuario.bloqueado_ate = None
        # O commit grava o contador zerado e libera a trava da linha.
        self.db.commit()

        # Se a conta não estiver ativa, retorna um erro de conta inativa.
        if not usuario.status:
            if usuario.profissional is not None:
                raise ErroNegocio(
                    "O cadastro do profissional de saúde ainda aguarda a validação do administrador.",
                    403,
                )
            raise ErroNegocio("Esta conta ainda não está ativa.", 403)

        # Se a conta estiver ativa, abre a sessão, gera o token ligado a ela e devolve a conta.
        sessao = ServicoSessao(self.db).abrir(usuario.id)
        return ResultadoLogin(token=gerar_token_acesso(usuario.id, sessao.id), usuario=usuario)

    def _bloqueio_restante(self, usuario: Usuario, agora: datetime) -> timedelta | None:
        """Diz quanto falta para a conta ser liberada, ou None se ela não está bloqueada.

        Passo a passo:
        1. Sem data em bloqueado_ate, a conta nunca foi bloqueada.
        2. Data no futuro: a conta está bloqueada e a diferença é o tempo que falta.
        3. Data no passado: o bloqueio venceu. Limpa a marca e o contador,
           e a conta volta a ter todas as tentativas.
        """
        if usuario.bloqueado_ate is None:
            return None
        limite = como_utc(usuario.bloqueado_ate)
        if limite > agora:
            return limite - agora
        usuario.bloqueado_ate = None
        usuario.tentativas_login_falhas = 0
        return None

    def _registrar_falha(self, usuario: Usuario, agora: datetime) -> timedelta | None:
        """Conta uma senha errada e bloqueia a conta ao chegar no limite.

        Passo a passo:
        1. Soma 1 ao contador de falhas seguidas.
        2. Se chegou em LOGIN_MAX_TENTATIVAS, grava bloqueado_ate = agora + duração
           e zera o contador, para a próxima rodada começar do zero.
        3. Faz commit ANTES de a rota devolver o erro. O get_db desfaz tudo quando a
           rota termina com erro, então sem este commit a falha nunca seria gravada
           e o bloqueio jamais aconteceria.
        4. Devolve o tempo de bloqueio se a conta acabou de ser bloqueada, senão None.
        """
        usuario.tentativas_login_falhas += 1
        restante = None
        if usuario.tentativas_login_falhas >= settings.login_max_tentativas:
            duracao = timedelta(minutes=settings.login_bloqueio_minutos)
            usuario.bloqueado_ate = agora + duracao
            usuario.tentativas_login_falhas = 0
            restante = duracao
        self.db.commit()
        return restante

    # Método para localizar o usuário. Identificador pode ser e-mail ou CPF.
    def _localizar(self, identificador: str) -> Usuario | None:
        """Decide se a busca é por e-mail ou por CPF.

        Passo a passo:
        1. Tira espaços das pontas.
        2. Com @, normaliza o e-mail e busca por ele.
        3. Sem @, confere os dígitos do CPF e busca por eles.
        4. Formato inválido vira 422. Conta ausente devolve None.
        """
        # Tira espaços das pontas.
        texto = identificador.strip()
        # Se o identificador tem @, trata como e-mail.
        if "@" in texto:
            # Normaliza o e-mail e busca por ele.
            try:
                email = normalizar_email(texto)
            except ValueError as exc:
                raise ErroNegocio(str(exc), 422) from exc
            return self.usuarios.buscar_por_email(email)
        try:
            cpf = normalizar_cpf(texto)
        except ValueError as exc:
            raise ErroNegocio(str(exc), 422) from exc
        
        # Busca o usuário por CPF.
        return self.usuarios.buscar_por_cpf(cpf)