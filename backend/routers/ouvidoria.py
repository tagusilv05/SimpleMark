"""Rotas da Ouvidoria: abertura de manifestação (com anexos opcionais)."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from core.excecoes import ErroNegocio
from dependencies.autenticacao import esquema_bearer, sessao_atual, usuario_atual
from dependencies.database import get_db
from models.models import Usuario
from schemas.comum import MensagemResposta
from schemas.ouvidoria import ManifestacaoCriadaResposta
from services.OuvidoriaService.ouvidoria import (
    ANEXO_TAMANHO_MAX,
    ANEXOS_MAX,
    AnexoRecebido,
    NovaManifestacao,
    ServicoOuvidoria,
)

router = APIRouter(prefix="/ouvidoria", tags=["Ouvidoria"])

DbSession = Annotated[Session, Depends(get_db)]


def get_servico_ouvidoria(db: DbSession) -> ServicoOuvidoria:
    """Fornece o serviço da Ouvidoria ligado à sessão do banco."""
    return ServicoOuvidoria(db)


def usuario_opcional(
    db: DbSession,
    credenciais: Annotated[HTTPAuthorizationCredentials | None, Depends(esquema_bearer)],
) -> Usuario | None:
    """Devolve o usuário logado, se houver token válido; senão, None.

    A Ouvidoria é aberta a qualquer pessoa: token ausente ou inválido não
    bloqueia o envio, só deixa a manifestação sem vínculo com uma conta.
    """
    if credenciais is None:
        return None
    try:
        return usuario_atual(db, sessao_atual(db, credenciais))
    except ErroNegocio:
        return None


ServicoOuvidoriaDep = Annotated[ServicoOuvidoria, Depends(get_servico_ouvidoria)]
UsuarioOpcional = Annotated[Usuario | None, Depends(usuario_opcional)]


@router.post(
    "/manifestacoes",
    status_code=201,
    response_model=ManifestacaoCriadaResposta,
    summary="Abrir manifestação na Ouvidoria",
    description=(
        "Recebe o formulário da Ouvidoria em multipart/form-data e devolve o protocolo. "
        "Não exige login; com token válido, a manifestação fica vinculada à conta. "
        f"Aceita até {ANEXOS_MAX} anexos PDF, PNG ou JPEG de até 10 MB cada no campo `anexos`."
    ),
    responses={422: {"model": MensagemResposta}, 503: {"model": MensagemResposta}},
)
async def abrir_manifestacao(
    servico: ServicoOuvidoriaDep,
    usuario: UsuarioOpcional,
    solicitante: Annotated[str, Form(description="paciente ou profissional")],
    tipo: Annotated[str, Form(description="reclamacao, teleconsulta, sugestao, elogio ou duvida")],
    assunto: Annotated[str, Form()],
    descricao: Annotated[str, Form()],
    aceite_lgpd: Annotated[bool, Form()] = False,
    codigo_consulta: Annotated[str | None, Form()] = None,
    anexos: Annotated[list[UploadFile] | None, File()] = None,
) -> ManifestacaoCriadaResposta:
    """Abre a manifestação e devolve o protocolo. Responde 422 com dados ou anexos inválidos."""
    arquivos = [a for a in (anexos or []) if a.filename]
    if len(arquivos) > ANEXOS_MAX:
        raise ErroNegocio(f"Envie no máximo {ANEXOS_MAX} arquivos.", 422)

    recebidos = []
    for arquivo in arquivos:
        # Lê 1 byte além do limite: basta para saber se passou, sem carregar o resto
        conteudo = await arquivo.read(ANEXO_TAMANHO_MAX + 1)
        recebidos.append(AnexoRecebido(nome=arquivo.filename, conteudo=conteudo))

    manifestacao = servico.abrir(
        NovaManifestacao(
            solicitante=solicitante,
            tipo=tipo,
            assunto=assunto,
            descricao=descricao,
            aceite_lgpd=aceite_lgpd,
            codigo_consulta=codigo_consulta,
        ),
        recebidos,
        usuario,
    )
    return ManifestacaoCriadaResposta(
        mensagem=(
            f"Manifestação registrada com o protocolo {manifestacao.protocolo}. "
            "Nossa equipe fará a análise e retornará o mais breve possível."
        ),
        id=manifestacao.id,
        protocolo=manifestacao.protocolo,
        status=manifestacao.status,
        criada_em=manifestacao.criada_em,
        quantidade_anexos=len(manifestacao.anexos),
    )
