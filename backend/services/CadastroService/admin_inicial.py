"""Garante a administradora Helena na subida da API.

Não existe rota de cadastro de administrador. A conta entra direto no banco
para a apresentação e para o administrador conseguir validar profissionais.
"""

import logging
import os
from datetime import date

from core.seguranca import gerar_hash_senha
from models.acesso import Credencial
from models.models import Administrador, Endereco, Usuario

logger = logging.getLogger("simplemark.admin_inicial")

EMAIL_ADMIN = "nordestino1971@gmail.com"
SENHA_ADMIN = "Senha123"
CPF_ADMIN = "847.329.105-05"


def criar_admin_inicial() -> None:
    """Garante uma administradora no banco sempre que a API sobe.

    Em ambiente de teste não faz nada. Se o banco estiver fora, só registra o aviso
    para a API de horários continuar no ar.
    """
    if os.getenv("AMBIENTE") == "teste":
        return

    from database.connection import SessionLocal
    from repositories.usuario import RepositorioUsuario

    db = SessionLocal()
    try:
        usuarios = RepositorioUsuario(db)
        usuario = usuarios.buscar_por_email(EMAIL_ADMIN)
        if usuario is None:
            if usuarios.buscar_por_cpf(CPF_ADMIN) is not None:
                logger.warning(
                    "CPF da administradora inicial já pertence a outra conta. Nada foi alterado."
                )
                return
            usuario = Usuario(
                nome="Helena Duarte",
                cpf=CPF_ADMIN,
                orgao_emissor="SSP/PI",
                data_nascimento=date(1985, 4, 12),
                genero="feminino",
                telefone="86911110003",
                email=EMAIL_ADMIN,
                status=True,
            )
            usuario.endereco = Endereco(
                cep="64000-000",
                cidade="Teresina",
                logradouro="Rua das Laranjeiras",
                numero="100",
                bairro="Centro",
            )
            usuario.administrador = Administrador()
            db.add(usuario)
            db.flush()
        elif usuario.administrador is None:
            logger.warning(
                "E-mail da administradora inicial já pertence a outra conta. Nada foi alterado."
            )
            return

        if db.get(Credencial, usuario.id) is not None:
            return
        db.add(
            Credencial(
                id_usuario=usuario.id,
                senha_hash=gerar_hash_senha(SENHA_ADMIN),
                consentimento_lgpd=True,
                tentativas_login_falhas=0,
            )
        )
        db.commit()
        print(f"Administradora inicial pronta. E-mail: {EMAIL_ADMIN}")
        logger.info("Administradora inicial pronta. E-mail: %s", EMAIL_ADMIN)
    except Exception:
        db.rollback()
        logger.exception(
            "Não foi possível criar a administradora inicial. "
            "Confira se o PostgreSQL está no ar."
        )
    finally:
        db.close()
