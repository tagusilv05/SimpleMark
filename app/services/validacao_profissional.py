# Arquivo criado por Victor
"""Validação do cadastro do profissional de saúde pelo administrador."""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import ErroNegocio
from app.models.profissional import Profissional
from app.models.profissional_especialidade import ProfissionalEspecialidade
from app.models.usuario import Usuario


class ServicoValidacaoProfissional:
    """Lista profissionais inativos e libera o cadastro depois da conferência."""

    def __init__(self, db: Session) -> None:
        """Guarda a sessão da requisição.

        Passo a passo:
        1. Recebe a sessão aberta por get_db.
        2. As consultas e o commit desta validação usam essa mesma sessão.
        """
        self.db = db

    # Método para listar os profissionais de saúde que ainda não foram validados.
    def listar_pendentes(self) -> list[Profissional]:
        """Devolve os profissionais de saúde que ainda não foram validados.

        Passo a passo:
        1. Junta profissional com usuario.
        2. Fica só com status falso.
        3. Carrega o usuário, os vínculos e o conselho de cada um.
        """
        # Faço uma consulta para buscar os profissionais de saúde que ainda não foram validados.
        consulta = (
            select(Profissional)
            .join(Usuario)
            .where(Usuario.status.is_(False))
            .options(
                selectinload(Profissional.usuario),
                selectinload(Profissional.vinculos).selectinload(ProfissionalEspecialidade.conselho),
            )
        )
        # Devolve a lista de profissionais de saúde que ainda não foram validados.
        return list(self.db.scalars(consulta))

    # Método para validar o profissional de saúde.
    def validar(self, id_profissional: int) -> Usuario:
        """Marca o profissional de saúde como ativo.

        Passo a passo:
        1. Busca o profissional pelo id.
        2. Se não existir, responde 404.
        3. Se o status já for verdadeiro, responde 409.
        4. Grava status verdadeiro e devolve a conta.
        """

        # Busco o profissional de saúde pelo id.
        profissional = self.db.get(Profissional, id_profissional)

        # Se o profissional de saúde não for encontrado, retorna um erro de profissional não encontrado.
        if profissional is None:
            raise ErroNegocio("Não encontramos este profissional de saúde.", 404)

        # Se o status do profissional de saúde já for verdadeiro, retorna um erro de profissional já validado.
        if profissional.usuario.status:
            raise ErroNegocio("Este profissional de saúde já foi validado.", 409)
        
        # Se o status do profissional de saúde não for verdadeiro, atualiza o status para verdadeiro.
        profissional.usuario.status = True

        # Commita a alteração no banco de dados.
        self.db.commit()

        # Devolve a conta do profissional de saúde validado.
        return profissional.usuario