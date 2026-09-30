# Arquivo criado por Victor
"""Garante a administradora Helena na subida da API.

Não existe rota de cadastro de administrador. A conta entra direto no banco
para a apresentação e para quem clonar o projeto conseguir validar profissionais.
"""

import logging
from datetime import date

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import gerar_hash_senha
from app.models.administrador import Administrador
from app.models.endereco import Endereco
from app.models.usuario import Usuario
from app.repositories.usuario import RepositorioUsuario

logger = logging.getLogger("simplemark.admin_inicial")

# Conta padrão da apresentação. Só é criada se o e-mail ainda não existir.
EMAIL_ADMIN = "nordestino1971@gmail.com"
SENHA_ADMIN = "Senha123"
CPF_ADMIN = "84732910505"


def criar_admin_inicial() -> None:
    """Insere a administradora Helena se ela ainda não estiver no banco.

    Passo a passo:
    1. Em ambiente de teste, não faz nada. Os testes montam o admin sozinhos.
    2. Abre uma sessão do PostgreSQL.
    3. Se o e-mail novo já existir, termina.
    4. Se ainda existir a conta antiga com o mesmo CPF, só atualiza o e-mail.
    5. Se não existir, grava usuário, endereço e perfil administrador.
    6. Confirma a transação. Se o banco estiver desligado, só registra o aviso.
    """
    if settings.ambiente == "teste":
        return
    db = SessionLocal()
    try:
        usuarios = RepositorioUsuario(db)
        if usuarios.buscar_por_email(EMAIL_ADMIN) is not None:
            return
        antiga = usuarios.buscar_por_cpf(CPF_ADMIN)
        if antiga is not None:
            antiga.email = EMAIL_ADMIN
            db.commit()
            logger.info("E-mail da administradora atualizado para %s", EMAIL_ADMIN)
            return
        usuario = Usuario(
            nome="Helena Duarte",
            cpf=CPF_ADMIN,
            orgao_emissor="SSP/PI",
            data_nascimento=date(1985, 4, 12),
            genero="feminino",
            telefone="86911110003",
            email=EMAIL_ADMIN,
            senha_hash=gerar_hash_senha(SENHA_ADMIN),
            status=True,
            consentimento_lgpd=True,
        )
        usuario.endereco = Endereco(
            cep="64000000",
            endereco="Rua das Laranjeiras, 100, Teresina",
        )
        usuario.administrador = Administrador()
        db.add(usuario)
        db.commit()
        logger.info(
            "Administradora inicial criada. E-mail: %s. Senha: %s",
            EMAIL_ADMIN,
            SENHA_ADMIN,
        )
    except Exception:
        db.rollback()
        logger.exception(
            "Não foi possível criar a administradora inicial. "
            "Confira se o PostgreSQL está no ar e se as migrações rodaram."
        )
    finally:
        db.close()
