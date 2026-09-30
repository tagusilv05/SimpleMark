# Arquivo criado por Victor
"""Login por e-mail ou CPF e emissão do token de acesso."""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.exceptions import ErroNegocio
from app.core.security import gerar_token_acesso, verificar_senha
from app.core.validators import normalizar_cpf, normalizar_email
from app.models.usuario import Usuario
from app.repositories.usuario import RepositorioUsuario

MENSAGEM_CREDENCIAL_INVALIDA = (
    "E-mail, CPF ou senha incorretos. Verifique os dados e tente novamente."
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
        3. Compara a senha com o hash Argon2.
        4. Se não bater, responde a mesma frase, sem dizer qual campo errou.
        5. Se a senha bater e a conta estiver inativa, recusa o login.
           No profissional de saúde, a mensagem pede a validação do administrador.
        6. Se a conta estiver ativa, assina o JWT com o id do usuário e devolve a conta.
        """
        # Utiliza o método _localizar, que está própria classe para buscar o usuário.
        usuario = self._localizar(identificador)
        # Se o usuário não for encontrado, retorna um erro de credencial inválida.
        if usuario is None:
            raise ErroNegocio(MENSAGEM_CREDENCIAL_INVALIDA, 401)
        # Verifica se a senha é válida.
        valida, novo_hash = verificar_senha(senha, usuario.senha_hash)

        # Se a senha não for válida, retorna um erro de credencial inválida.
        if not valida:
            raise ErroNegocio(MENSAGEM_CREDENCIAL_INVALIDA, 401)
        
        # Se a senha for válida, atualiza o hash da senha.
        if novo_hash:
            usuario.senha_hash = novo_hash
            self.db.commit()
        
        # Se a conta não estiver ativa, retorna um erro de conta inativa.
        if not usuario.status:
            if usuario.profissional is not None:
                raise ErroNegocio(
                    "O cadastro do profissional de saúde ainda aguarda a validação do administrador.",
                    403,
                )
            raise ErroNegocio("Esta conta ainda não está ativa.", 403)
        
        # Se a conta estiver ativa, gera o token de acesso e devolve a conta.
        return ResultadoLogin(token=gerar_token_acesso(usuario.id), usuario=usuario)

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