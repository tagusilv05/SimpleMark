# Arquivo criado por Victor e Gustavo
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.usuario import Usuario


# Classe para representar o repositório de usuários.
class RepositorioUsuario:
    """Consultas da tabela usuario. Não aplica regra de negócio."""

    def __init__(self, db: Session) -> None:
        """Guarda a sessão aberta por get_db. Cada método usa essa mesma sessão."""
        self.db = db

    def buscar_por_id(self, id_usuario: int) -> Usuario | None:
           """Busca o usuário pela chave primária.
   
           Passo a passo:
           1. Pede ao SQLAlchemy o Usuario com esse id.
           2. Devolve o objeto ou None se a linha não existir.
           """
           return self.db.get(Usuario, id_usuario)

    def buscar_por_email(self, email: str) -> Usuario | None:
        """Busca o usuário pelo e-mail já normalizado em minúsculas.

        Passo a passo:
        1. Monta um SELECT em usuario filtrando a coluna email.
        2. scalar devolve a primeira linha ou None.
        """
        return self.db.scalar(select(Usuario).where(Usuario.email == email))

    def buscar_por_cpf(self, cpf: str) -> Usuario | None:
        """Busca o usuário pelos 11 dígitos do CPF.

        Passo a passo:
        1. Monta um SELECT em usuario filtrando a coluna cpf.
        2. scalar devolve a primeira linha ou None.
        """
        return self.db.scalar(select(Usuario).where(Usuario.cpf == cpf))

    def buscar_por_id_para_atualizar(self, id_usuario: int) -> Usuario:
        """Busca o usuário e trava a linha até o fim da transação.

        Passo a passo:
        1. SELECT ... FOR UPDATE pede ao PostgreSQL a trava da linha desse usuário.
        2. Outra requisição para a mesma conta espera aqui até esta terminar.
        3. populate_existing recarrega os campos do banco, para o service enxergar
           o contador de tentativas mais recente e não uma cópia velha da sessão.
        4. A trava cai no commit ou no rollback. No SQLite dos testes ela é ignorada.
        """
        comando = (
            select(Usuario)
            .where(Usuario.id == id_usuario)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return self.db.execute(comando).scalar_one()

    def adicionar(self, usuario: Usuario) -> Usuario:
        """Coloca o usuário na sessão para ser gravado no commit.

        Passo a passo:
        1. db.add marca o objeto como novo. Ainda não há INSERT.
        2. Devolve o mesmo objeto para o service continuar preenchendo relações.
        """
        # Assim como nos outros repositórios, aqui também não salvamos do banco de dados, apenas adicionamos na sessão. Pois quem decide se salva ou não, é o Service.
        self.db.add(usuario)

        # Devolve o mesmo objeto para o service continuar preenchendo relações
        return usuario