"""Campos numéricos recusam letras e campos de texto recusam números/símbolos."""
import pytest
from pydantic import ValidationError

from schemas.cadastro import CadastroProfissionalEntrada, CadastroUsuarioEntrada
from schemas.usuario_minha_conta import AltereEnderecoInput, AltereInfoPessoalInput
import uuid

CPF_OK = "529.982.247-25"

PACIENTE = {
    "nome": "Maria D'Ávila-Silva",
    "cpf": CPF_OK,
    "orgao_emissor": "SSP-PI",
    "data_nascimento": "1990-05-10",
    "genero": "Feminino",
    "telefone": "(86) 99999-1234",
    "email": "maria@exemplo.com",
    "senha": "senha-forte-123",
    "consentimento_lgpd": True,
    "cep": "64000-000",
    "cidade": "São Luís do Piauí",
    "logradouro": "Av. Frei Serafim, nº 1.200",
    "numero": "120",
    "bairro": "Centro",
    "complemento": "Apto 12 (bloco B)",
}
PROFISSIONAL = {
    **PACIENTE,
    "numero_conselho": "123456",
    "orgao_conselho": "CRM-PI",
    "info_profissional": "Cardiologista com 10 anos de experiência.",
    "especialidades": ["Cardiologia", "Clínica Geral"],
}


def test_dados_validos_continuam_aceitos():
    p = CadastroUsuarioEntrada(**PACIENTE)
    assert p.cpf == CPF_OK and p.telefone == "86999991234" and p.cep == "64000-000"
    assert p.nome == "Maria D'Ávila-Silva"
    CadastroProfissionalEntrada(**PROFISSIONAL)
    # CPF e CEP sem máscara também valem.
    assert CadastroUsuarioEntrada(**{**PACIENTE, "cpf": "52998224725", "cep": "64000000"}).numero == "120"


@pytest.mark.parametrize(
    "campo,valor",
    [
        ("cpf", "abc529.982.247-25"),
        ("cpf", "529.982.247-25xyz"),
        ("cpf", "529982247-25; DROP TABLE usuario"),
        ("cpf", "٥٢٩٩٨٢٢٤٧٢٥"),  # dígitos de outro alfabeto
        ("cpf", "5299.822.4725"),
        ("telefone", "(86) 99999-12ab"),
        ("telefone", "86999991234'; --"),
        ("telefone", "abcdefghijk"),
        ("cep", "64000-00a"),
        ("cep", "abc64000000"),
        ("numero", "abc"),
        ("numero", "120-A"),
        ("numero", "S/N"),
        ("numero", "12 3"),
        ("numero", "12'; DROP TABLE x;--"),
        ("nome", "Maria 123"),
        ("nome", "Robert'); DROP TABLE usuario;--"),
        ("nome", "<script>alert(1)</script>"),
        ("genero", "F3minino"),
        ("cidade", "Teresina 2"),
        ("bairro", "Centro #1"),
        ("orgao_emissor", "SSP;PI"),
        ("logradouro", "Rua <b>X</b>"),
        ("complemento", "apto; DROP TABLE"),
    ],
)
def test_paciente_recusa_caracteres_indevidos(campo, valor):
    with pytest.raises(ValidationError):
        CadastroUsuarioEntrada(**{**PACIENTE, campo: valor})


@pytest.mark.parametrize(
    "campo,valor",
    [
        ("numero_conselho", "12ab56"),
        ("numero_conselho", "CRM123"),
        ("numero_conselho", "123-456"),
        ("numero_conselho", "123456-ENF"),
        ("numero_conselho", "1; DROP TABLE x"),
        ("orgao_conselho", "CRM;PI"),
        ("especialidades", ["Cardio123"]),
        ("especialidades", ["Cardiologia", "x'; DROP TABLE y;--"]),
    ],
)
def test_profissional_recusa_caracteres_indevidos(campo, valor):
    with pytest.raises(ValidationError):
        CadastroProfissionalEntrada(**{**PROFISSIONAL, campo: valor})


def test_minha_conta_tambem_valida():
    uid = uuid.uuid4()
    with pytest.raises(ValidationError):
        AltereInfoPessoalInput(id=uid, telefone="abc")
    with pytest.raises(ValidationError):
        AltereInfoPessoalInput(id=uid, nome="Ana 9")
    with pytest.raises(ValidationError):
        AltereEnderecoInput(id_usuario=uid, cep="6400a-000")
    with pytest.raises(ValidationError):
        AltereEnderecoInput(id_usuario=uid, numero="abc")
    with pytest.raises(ValidationError):
        AltereEnderecoInput(id_usuario=uid, numero="12'; DROP TABLE x")
    assert AltereEnderecoInput(id_usuario=uid, numero="120-a").numero == "120-a"  # caixa preservada
    ok = AltereEnderecoInput(id_usuario=uid, cep="64000000", numero=120, cidade="Teresina")
    assert ok.cep == "64000-000" and ok.numero == "120"


def test_apostrofo_tipografico_e_ponto_na_sigla():
    ok = CadastroUsuarioEntrada(**{**PACIENTE, "nome": "Ana D’Ávila", "orgao_emissor": "S.S.P/PI"})
    assert ok.nome == "Ana D’Ávila" and ok.orgao_emissor == "S.S.P/PI"


def test_maiusculas_e_minusculas_digitadas_sao_preservadas():
    p = CadastroProfissionalEntrada(**{**PROFISSIONAL, "nome": "joão da SILVA", "cidade": "são LUÍS", "orgao_conselho": "crm-Pi", "orgao_emissor": "ssp-PI"})
    assert (p.nome, p.cidade, p.orgao_conselho, p.orgao_emissor) == ("joão da SILVA", "são LUÍS", "crm-Pi", "ssp-PI")