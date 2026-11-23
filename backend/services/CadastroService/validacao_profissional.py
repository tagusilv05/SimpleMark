"""Validação do cadastro do profissional de saúde pelo administrador."""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from core.excecoes import ErroNegocio
from models.models import Profissional, ProfissionalEspecialidade, Usuario


class ServicoValidacaoProfissional:
    """Lista e valida os profissionais que aguardam aprovação do administrador."""

    def __init__(self, db: Session) -> None:
        """Guarda a sessão do banco.

        Args:
            db (Session): Sessão do SQLAlchemy usada nas consultas e gravações.
        """
        self.db = db

    def listar_pendentes(self) -> list[Profissional]:
        """Profissionais com conta inativa, já carregando usuário, conselhos e especialidades.

        Returns:
            list[Profissional]: Os profissionais que aguardam validação.
        """
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
        """Ativa a conta do profissional e faz o commit.

        Responde 404 se ele não existir e 409 se já estiver validado.

        Args:
            id_profissional (int): ID do profissional a validar.

        Returns:
            Usuario: O usuário do profissional, agora ativo.

        Raises:
            ErroNegocio: Com status 404, quando o profissional não existe, ou 409,
                quando já foi validado.
        """
        profissional = self.db.get(Profissional, id_profissional)
        if profissional is None:
            raise ErroNegocio("Não encontramos este profissional de saúde.", 404)
        if profissional.usuario.status:
            raise ErroNegocio("Este profissional de saúde já foi validado.", 409)
        profissional.usuario.status = True
        self.db.commit()
        return profissional.usuario
