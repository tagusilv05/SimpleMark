"""Recuperação de senha: o código de 6 caracteres é enviado por e-mail, se for valido o usuario poderá inserir a nova senha."""

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy.orm import Session

from core.excecoes import ErroNegocio
from core.parametros import (
    recuperacao_codigo_minutos,
    recuperacao_max_tentativas,
    recuperacao_redefinicao_minutos,
    recuperacao_reenvio_segundos,
    segredo_jwt,
)
from core.seguranca import gerar_hash_senha
from core.tempo import agora_utc, como_utc
from repositories.codigo_recuperacao import RepositorioCodigoRecuperacao
from repositories.credencial import RepositorioCredencial
from repositories.sessao_login import RepositorioSessaoLogin
from repositories.usuario import RepositorioUsuario

# Sem I, L e O (parecem 1 e 0) e sem 0 e 1. Sobram 23 letras e 8 números.
LETRAS = "ABCDEFGHJKMNPQRSTUVWXYZ"
NUMEROS = "23456789"
TAMANHO_CODIGO = 6
TENTATIVAS_DE_UNICIDADE = 10

MENSAGEM_CODIGO_INVALIDO = "Código inválido ou expirado. Confira o código ou solicite um novo."
MENSAGEM_ETAPA_INVALIDA = "Esta etapa expirou ou já foi usada. Recomece a recuperação de senha."


@dataclass
class EnvioCodigo:
    """E-mail pronto para ser enviado depois da resposta da API."""

    destinatario: str
    assunto: str
    texto: str


@dataclass
class TokenRedefinicao:
    token: str
    expira_em_segundos: int


def gerar_codigo() -> str:
    """Sorteia 6 caracteres com secrets, garantindo ao menos uma letra e um número."""
    alfabeto = LETRAS + NUMEROS
    while True:
        codigo = "".join(secrets.choice(alfabeto) for _ in range(TAMANHO_CODIGO))
        if any(c in LETRAS for c in codigo) and any(c in NUMEROS for c in codigo):
            return codigo


def normalizar_codigo(texto: str) -> str:
    """Aceita minúsculas, espaços e hífens: ab3-k9z vira AB3K9Z."""
    return "".join(c for c in texto if c.isalnum()).upper()


def hash_codigo(codigo: str) -> str:
    """HMAC com a chave do sistema. O mesmo código sempre dá o mesmo hash, o que permite
    conferir se ele já está em uso, e quem lê só o banco não consegue testar códigos.
    """
    return hmac.new(segredo_jwt().encode("utf-8"), codigo.encode("utf-8"), hashlib.sha256).hexdigest()


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def montar_email_codigo(nome: str, codigo: str, validade_minutos: int) -> tuple[str, str]:
    primeiro_nome = nome.split()[0] if nome.split() else "usuário"
    unidade = "minuto" if validade_minutos == 1 else "minutos"
    assunto = "Simple Mark: código para redefinir sua senha"
    texto = (
        f"Olá, {primeiro_nome}!\n\n"
        "Seu código para redefinir a senha no Simple Mark é:\n\n"
        f"    {codigo}\n\n"
        f"Ele vale por {validade_minutos} {unidade} e só pode ser usado uma vez.\n"
        "Se você não pediu a redefinição, ignore este e-mail: sua senha continua a mesma.\n"
    )
    return assunto, texto


class ServicoRecuperacaoSenha:
    """Três etapas: pedir o código, conferir o código e definir a nova senha.

    Todas as respostas de erro são genéricas: não revelam se o e-mail tem conta.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.usuarios = RepositorioUsuario(db)
        self.credenciais = RepositorioCredencial(db)
        self.codigos = RepositorioCodigoRecuperacao(db)
        self.sessoes = RepositorioSessaoLogin(db)

    def solicitar(self, email: str) -> EnvioCodigo | None:
        """Cria um código novo e devolve o e-mail a enviar, ou None se não há o que enviar.

        None acontece com e-mail sem conta, conta inativa ou pedido antes do intervalo
        de reenvio. A rota responde igual nos três casos e no caso de sucesso.
        """
        usuario = self.usuarios.buscar_por_email(email)
        if usuario is None or not usuario.status:
            return None
        # Trava a conta: dois cliques ao mesmo tempo viram um código só.
        if self.credenciais.buscar_para_atualizar(usuario.id) is None:
            self.db.rollback()
            return None

        agora = agora_utc()
        ultimo = self.codigos.ultimo_do_usuario(usuario.id)
        if ultimo is not None:
            espera = timedelta(seconds=recuperacao_reenvio_segundos())
            if agora - como_utc(ultimo.criado_em) < espera:
                self.db.rollback()
                return None

        # O código novo substitui qualquer código ou token anterior da conta.
        self.codigos.encerrar_abertos_do_usuario(usuario.id, agora)
        codigo, codigo_hash = self._gerar_codigo_unico(agora)
        validade = recuperacao_codigo_minutos()
        self.codigos.criar(usuario.id, codigo_hash, agora, agora + timedelta(minutes=validade))
        self.db.commit()

        assunto, texto = montar_email_codigo(usuario.nome, codigo, validade)
        return EnvioCodigo(destinatario=usuario.email, assunto=assunto, texto=texto)

    def verificar(self, email: str, codigo: str) -> TokenRedefinicao:
        """Confere o código e devolve o token que libera a troca da senha."""
        usuario = self.usuarios.buscar_por_email(email)
        if usuario is None or not usuario.status:
            raise ErroNegocio(MENSAGEM_CODIGO_INVALIDO, 400)
        if self.credenciais.buscar_para_atualizar(usuario.id) is None:
            self.db.rollback()
            raise ErroNegocio(MENSAGEM_CODIGO_INVALIDO, 400)

        agora = agora_utc()
        registro = self.codigos.buscar_aguardando_codigo(usuario.id, agora)
        if registro is None:
            self.db.rollback()
            raise ErroNegocio(MENSAGEM_CODIGO_INVALIDO, 400)

        informado = hash_codigo(normalizar_codigo(codigo))
        if not hmac.compare_digest(registro.codigo_hash, informado):
            registro.tentativas += 1
            if registro.tentativas >= recuperacao_max_tentativas():
                registro.encerrado_em = agora
            # O commit vem antes do erro: sem ele a tentativa errada não ficaria gravada.
            self.db.commit()
            raise ErroNegocio(MENSAGEM_CODIGO_INVALIDO, 400)

        token = secrets.token_urlsafe(32)
        minutos = recuperacao_redefinicao_minutos()
        registro.verificado_em = agora
        registro.token_hash = hash_token(token)
        registro.redefinir_ate = agora + timedelta(minutes=minutos)
        self.db.commit()
        return TokenRedefinicao(token=token, expira_em_segundos=minutos * 60)

    def redefinir(self, token: str, nova_senha: str) -> None:
        """Troca a senha, zera o bloqueio de login e encerra todas as sessões da conta."""
        token_hash = hash_token(token)
        previa = self.codigos.buscar_por_token(token_hash)
        if previa is None:
            raise ErroNegocio(MENSAGEM_ETAPA_INVALIDA, 400)

        # Mesma ordem de trava das outras etapas (conta primeiro, código depois): sem impasse.
        credencial = self.credenciais.buscar_para_atualizar(previa.id_usuario)
        registro = self.codigos.buscar_por_token_para_atualizar(token_hash)
        usuario = self.usuarios.buscar_por_id(previa.id_usuario)
        agora = agora_utc()

        invalido = (
            credencial is None
            or registro is None
            or registro.encerrado_em is not None
            or registro.redefinir_ate is None
            or como_utc(registro.redefinir_ate) <= agora
            or usuario is None
            or not usuario.status
        )
        if invalido:
            self.db.rollback()
            raise ErroNegocio(MENSAGEM_ETAPA_INVALIDA, 400)

        credencial.senha_hash = gerar_hash_senha(nova_senha)
        credencial.tentativas_login_falhas = 0
        credencial.bloqueado_ate = None
        self.sessoes.encerrar_todas(usuario.id, agora)
        registro.encerrado_em = agora
        self.db.commit()

    def _gerar_codigo_unico(self, agora) -> tuple[str, str]:
        """Sorteia até achar um código que nenhum outro código válido esteja usando."""
        for _ in range(TENTATIVAS_DE_UNICIDADE):
            codigo = gerar_codigo()
            codigo_hash = hash_codigo(codigo)
            if not self.codigos.existe_aberto_com_hash(codigo_hash, agora):
                return codigo, codigo_hash
        raise ErroNegocio("Não foi possível gerar o código agora. Tente novamente.", 503)
