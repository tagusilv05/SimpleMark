# Arquivo criado por Victor
from pydantic import Field, field_validator

from app.core.perfil import PerfilUsuario, perfil_de
from app.core.validators import validar_senha
from app.models.usuario import Usuario
from app.schemas.comum import Esquema


class LoginEntrada(Esquema):
    """Identificador por e-mail (RF2) ou CPF (RF3), mais a senha."""

    identificador: str = Field(
        description="E-mail ou CPF da conta.",
        examples=["nordestino1971@gmail.com", "nordestino1971+paciente@gmail.com"],
    )
    senha: str = Field(description="Senha da conta.", examples=["Senha123"])

    @field_validator("identificador")
    @classmethod
    def identificador_obrigatorio(cls, valor: str) -> str:
        """Exige e-mail ou CPF preenchido, sem decidir ainda qual dos dois é.

        Passo a passo:
        1. Tira espaços das pontas.
        2. Recusa vazio.
        3. Devolve o texto. O service vê o @ para escolher e-mail ou CPF.
        """
        texto = valor.strip()
        if not texto:
            raise ValueError("Informe o e-mail ou o CPF para entrar.")
        return texto

    @field_validator("senha")
    @classmethod
    def senha_informada(cls, valor: str) -> str:
        """Aplica o mesmo tamanho mínimo da senha de cadastro."""
        return validar_senha(valor)

# Classe para representar a conta autenticada, sem senha e sem dados clínicos.
class UsuarioPublico(Esquema):
    """Identidade da conta autenticada, sem senha e sem dados clínicos."""

    id: int = Field(title="Identificador", description="Número da conta na tabela usuário.")
    nome: str = Field(title="Nome")
    email: str = Field(title="E-mail")
    cpf: str = Field(title="CPF", description="Onze dígitos, sem pontuação.")
    perfil: PerfilUsuario = Field(title="Perfil", description="paciente, profissional ou administrador.")
    status: bool = Field(
        title="Conta ativa",
        description="Verdadeiro quando a conta pode acessar as rotas restritas do perfil.",
    )
    id_paciente: int | None = Field(default=None, title="Identificador do paciente")
    id_profissional: int | None = Field(default=None, title="Identificador do profissional")
    id_administrador: int | None = Field(default=None, title="Identificador do administrador")

# Classe para representar a resposta do login, com token e conta autenticada.
class TokenResposta(Esquema):
    """Resposta do login. O token vai no cadeado Authorize das rotas protegidas."""
    
    # Campo para o token de acesso.
    access_token: str = Field(
        title="Token de acesso",
        description="Cole este valor no cadeado Authorize, sem a palavra Bearer.",
    )
    # Campo para o tipo do token.
    token_type: str = Field(
        default="bearer",
        title="Tipo do token",
        description="A palavra bearer faz parte do padrão HTTP. No cabeçalho ela acompanha o token.",
    )
    # Campo para a conta autenticada.
    usuario: UsuarioPublico = Field(title="Usuário")

# Método para montar a conta autenticada.
def montar_usuario_publico(usuario: Usuario) -> UsuarioPublico:
    """Monta o JSON da conta sem senha.

    Passo a passo:
    1. Copia id, nome, e-mail, CPF e status.
    2. perfil_de olha a tabela filha e escolhe paciente, profissional ou administrador.
    3. Preenche só o id do perfil que existir. Os outros ficam nulos.
    """
    return UsuarioPublico(
        id=usuario.id,
        nome=usuario.nome,
        email=usuario.email,
        cpf=usuario.cpf,
        perfil=perfil_de(usuario),
        status=usuario.status,
        id_paciente=usuario.paciente.id_paciente if usuario.paciente else None,
        id_profissional=usuario.profissional.id_profissional if usuario.profissional else None,
        id_administrador=usuario.administrador.id_administrador if usuario.administrador else None,
    )
