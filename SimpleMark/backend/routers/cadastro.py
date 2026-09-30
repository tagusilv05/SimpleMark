from typing import Annotated, Any

from fastapi import APIRouter, Body, status

from dependencies.autenticacao import ServicoCadastroDep
from schemas.auth import UsuarioPublico, montar_usuario_publico
from schemas.cadastro import CadastroProfissionalEntrada, CadastroUsuarioEntrada
from schemas.comum import MensagemResposta

router = APIRouter(prefix="/cadastro", tags=["Cadastro"])

_RESPOSTAS: dict[int | str, dict[str, Any]] = {
    409: {"model": MensagemResposta},
    422: {"model": MensagemResposta},
}

_EXEMPLO_ENDERECO = {
    "cep": "64000-000",
    "cidade": "Teresina",
    "logradouro": "Rua das Laranjeiras",
    "numero": "100",
    "bairro": "Centro",
}


@router.post(
    "/paciente",
    response_model=UsuarioPublico,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar paciente",
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
                        **_EXEMPLO_ENDERECO,
                    },
                }
            }
        ),
    ],
) -> UsuarioPublico:
    return montar_usuario_publico(servico.cadastrar_paciente(dados))


@router.post(
    "/profissional",
    response_model=UsuarioPublico,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar profissional",
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
                        "cidade": "Teresina",
                        "logradouro": "Rua das Laranjeiras",
                        "numero": "200",
                        "bairro": "Centro",
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
    return montar_usuario_publico(servico.cadastrar_profissional(dados))
