# Arquivo criado por Victor
from typing import Annotated, Any

from fastapi import APIRouter, Body, status

from app.api.deps import ServicoCadastroDep
from app.schemas.auth import UsuarioPublico, montar_usuario_publico
from app.schemas.cadastro import CadastroProfissionalEntrada, CadastroUsuarioEntrada
from app.schemas.comum import MensagemResposta

router = APIRouter(prefix="/cadastro", tags=["Cadastro"])

_RESPOSTAS: dict[int | str, dict[str, Any]] = {
    409: {"model": MensagemResposta},
    422: {"model": MensagemResposta},
}


@router.post(
    "/paciente",
    response_model=UsuarioPublico,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar paciente",
    description="Cria a conta de paciente com os dados do RF1. CPF e e-mail são únicos (RN1).",
    responses=_RESPOSTAS,
)
def cadastrar_paciente(
    servico: ServicoCadastroDep,
    dados: Annotated[
        CadastroUsuarioEntrada,
        Body(
            openapi_examples={
                "paciente": {
                    "summary": "Paciente novo",
                    "description": "CPF e e-mail ainda não usados. Execute uma vez. A segunda tentativa responde 409.",
                    "value": {
                        "nome": "Ana Beatriz Costa",
                        "cpf": "390.533.447-05",
                        "orgao_emissor": "SSP/PI",
                        "data_nascimento": "1996-08-14",
                        "genero": "feminino",
                        "telefone": "86911110001",
                        "email": "nordestino1971+paciente@gmail.com",
                        "senha": "Senha123",
                        "consentimento_lgpd": True,
                        "cep": "64000-000",
                        "endereco": "Rua das Laranjeiras, 100, Teresina",
                    },
                }
            }
        ),
    ],
) -> UsuarioPublico:
    """Recebe o JSON do paciente e devolve a conta criada, sem a senha.

    Passo a passo:
    1. O FastAPI valida o corpo com CadastroUsuarioEntrada antes de entrar aqui.
    2. O service grava usuário, endereço e perfil paciente.
    3. montar_usuario_publico tira a senha e informa o perfil e o id_paciente.
    """
    return montar_usuario_publico(servico.cadastrar_paciente(dados))


@router.post(
    "/profissional",
    response_model=UsuarioPublico,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar profissional",
    description=(
        "Cria a conta do profissional de saúde com ao menos uma especialidade. "
        "A conta fica inativa até o administrador validar o cadastro. "
        "CPF, e-mail e o par número + órgão do conselho são únicos."
    ),
    responses=_RESPOSTAS,
)
def cadastrar_profissional(
    servico: ServicoCadastroDep,
    dados: Annotated[
        CadastroProfissionalEntrada,
        Body(
            openapi_examples={
                "profissional": {
                    "summary": "Profissional novo",
                    "description": "A conta nasce inativa. O administrador libera em validar.",
                    "value": {
                        "nome": "Carlos Eduardo Lima",
                        "cpf": "111.444.777-35",
                        "orgao_emissor": "SSP/PI",
                        "data_nascimento": "1988-11-03",
                        "genero": "masculino",
                        "telefone": "86911110002",
                        "email": "nordestino1971+profissional@gmail.com",
                        "senha": "Senha123",
                        "consentimento_lgpd": True,
                        "cep": "64000-000",
                        "endereco": "Rua das Laranjeiras, 200, Teresina",
                        "numero_conselho": "240815",
                        "orgao_conselho": "CRM",
                        "info_profissional": "Clínico geral com atuação em telemedicina.",
                        "especialidades": ["Clínica médica"],
                    },
                }
            }
        ),
    ],
) -> UsuarioPublico:
    """Recebe o JSON do profissional de saúde e devolve a conta criada, sem a senha.

    Passo a passo:
    1. O schema exige conselho, informações profissionais e ao menos uma especialidade.
    2. O service grava a conta com status falso, até o administrador validar.
    3. A resposta mostra o perfil profissional e status falso.
    """
    return montar_usuario_publico(servico.cadastrar_profissional(dados))
