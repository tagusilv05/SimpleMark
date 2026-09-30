"""Validação do cadastro do profissional de saúde pelo administrador."""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from core.excecoes import ErroNegocio
from models.models import Profissional, ProfissionalEspecialidade, Usuario


class ServicoValidacaoProfissional:
    def __init__(self, db: Session) -> None:
        self.db = db

    def listar_pendentes(self) -> list[Profissional]:
        consulta = (
            select(Profissional)
            .join(Profissional.usuario)
            .where(Usuario.status.is_(False))
            .options(
                selectinload(Profissional.usuario),
                selectinload(Profissional.especialidades).selectinload(ProfissionalEspecialidade.conselho),
                selectinload(Profissional.especialidades).selectinload(ProfissionalEspecialidade.especialidade),
            )
        )
        return list(self.db.scalars(consulta))

    def validar(self, id_profissional: int) -> Usuario:
        profissional = self.db.get(Profissional, id_profissional)
        if profissional is None:
            raise ErroNegocio("Não encontramos este profissional de saúde.", 404)
        if profissional.usuario.status:
            raise ErroNegocio("Este profissional de saúde já foi validado.", 409)
        profissional.usuario.status = True
        self.db.commit()
        return profissional.usuario
