# Testes da busca de profissionais por especialidade, data, horário e valor.
#
# A agenda é montada em cima de datas relativas a hoje: a busca recusa o
# passado de propósito, então data fixa no código quebraria com o tempo.
import uuid
from datetime import date, datetime, time, timedelta

import pytest

from models.models import (
    Consulta,
    DataHorario,
    Especialidade,
    InfoConselho,
    Paciente,
    Profissional,
    ProfissionalEspecialidade,
    Usuario,
)

ROTA = "/api/v1/profissionais/busca"

AMANHA = date.today() + timedelta(days=1)
DEPOIS = date.today() + timedelta(days=2)
ONTEM = date.today() - timedelta(days=1)


def _criar_profissional(db, nome: str, sufixo: int, ativo: bool = True) -> Profissional:
    usuario = Usuario(
        id=uuid.uuid4(),
        nome=nome,
        cpf=f"222.222.22{sufixo:02d}",
        orgao_emissor="SSP-PI",
        data_nascimento=date(1980, 1, 15),
        genero="Não informado",
        telefone=f"(89) 97777-{sufixo:04d}",
        email=f"busca{sufixo}@email.com",
        status=ativo,
    )
    db.add(usuario)
    db.flush()

    profissional = Profissional(
        id_usuario=usuario.id,
        info_profissional=f"Atende desde {1990 + sufixo}.",
    )
    db.add(profissional)
    db.flush()
    return profissional


def _obter_especialidade(db, nome: str) -> Especialidade:
    existente = db.query(Especialidade).filter(Especialidade.especialidade == nome).first()
    if existente is not None:
        return existente
    criada = Especialidade(especialidade=nome)
    db.add(criada)
    db.flush()
    return criada


def _criar_vinculo(
    db,
    profissional: Profissional,
    nome_especialidade: str,
    valor: float,
    avaliacao: float | None = None,
) -> ProfissionalEspecialidade:
    conselho = InfoConselho(numero_conselho="54321", orgao_conselho="CRM-PI")
    db.add(conselho)
    db.flush()

    vinculo = ProfissionalEspecialidade(
        id_profissional=profissional.id_profissional,
        id_especialidade=_obter_especialidade(db, nome_especialidade).id_especialidade,
        id_conselho=conselho.id_conselho,
        valor_consulta=valor,
        avaliacao=avaliacao,
    )
    db.add(vinculo)
    db.flush()
    return vinculo


def _criar_horario(
    db,
    vinculo: ProfissionalEspecialidade,
    dia: date,
    inicio: time,
    fim: time,
    ocupado: bool = False,
) -> DataHorario:
    horario = DataHorario(
        id_esp_prof=vinculo.id_esp_prof,
        data_consulta=dia,
        hora_inicio=inicio,
        hora_fim=fim,
        ocupado=ocupado,
    )
    db.add(horario)
    db.flush()
    return horario


@pytest.fixture
def agenda(db):
    """Três profissionais: cardiologista caro, cardiologista barato e pediatra."""
    ana = _criar_profissional(db, "Ana Cardio", 1)
    bruno = _criar_profissional(db, "Bruno Cardio", 2)
    carla = _criar_profissional(db, "Carla Pediatra", 3)

    vinculo_ana = _criar_vinculo(db, ana, "Cardiologia", 300.0, avaliacao=4.5)
    vinculo_bruno = _criar_vinculo(db, bruno, "Cardiologia", 150.0)
    vinculo_carla = _criar_vinculo(db, carla, "Pediatria", 200.0, avaliacao=5.0)

    _criar_horario(db, vinculo_ana, AMANHA, time(9, 0), time(9, 30))
    _criar_horario(db, vinculo_ana, DEPOIS, time(15, 0), time(15, 30))
    _criar_horario(db, vinculo_bruno, AMANHA, time(14, 0), time(14, 30))
    _criar_horario(db, vinculo_carla, AMANHA, time(8, 0), time(8, 30))

    db.commit()
    return {"ana": vinculo_ana, "bruno": vinculo_bruno, "carla": vinculo_carla}


def _nomes(resposta) -> list[str]:
    return [ficha["nome"] for ficha in resposta.json()]


def test_sem_filtro_devolve_todos_os_profissionais_com_agenda(client, agenda):
    resposta = client.get(ROTA)

    assert resposta.status_code == 200
    assert _nomes(resposta) == ["Ana Cardio", "Bruno Cardio", "Carla Pediatra"]


def test_filtra_pelo_id_da_especialidade(client, agenda):
    resposta = client.get(
        ROTA, params={"id_especialidade": agenda["carla"].id_especialidade}
    )

    assert resposta.status_code == 200
    assert _nomes(resposta) == ["Carla Pediatra"]


def test_filtra_por_parte_do_nome_da_especialidade(client, agenda):
    resposta = client.get(ROTA, params={"especialidade": "cardio"})

    assert resposta.status_code == 200
    assert _nomes(resposta) == ["Ana Cardio", "Bruno Cardio"]


def test_filtra_pelo_periodo_de_datas(client, agenda):
    resposta = client.get(
        ROTA, params={"data_inicio": DEPOIS.isoformat(), "data_fim": DEPOIS.isoformat()}
    )

    assert resposta.status_code == 200
    assert _nomes(resposta) == ["Ana Cardio"]
    assert [h["data_consulta"] for h in resposta.json()[0]["horarios_disponiveis"]] == [
        DEPOIS.isoformat()
    ]


def test_filtra_pela_faixa_de_horario(client, agenda):
    resposta = client.get(ROTA, params={"hora_inicio": "13:00", "hora_fim": "18:00"})

    assert resposta.status_code == 200
    assert _nomes(resposta) == ["Ana Cardio", "Bruno Cardio"]
    assert [h["hora_inicio"] for h in resposta.json()[1]["horarios_disponiveis"]] == ["14:00:00"]


def test_filtra_pela_faixa_de_valor(client, agenda):
    resposta = client.get(ROTA, params={"valor_min": 160, "valor_max": 250})

    assert resposta.status_code == 200
    assert _nomes(resposta) == ["Carla Pediatra"]
    assert resposta.json()[0]["valor_consulta"] == 200.0


def test_ordena_do_mais_barato_para_o_mais_caro(client, agenda):
    resposta = client.get(ROTA, params={"ordenar_por": "valor"})

    assert resposta.status_code == 200
    assert _nomes(resposta) == ["Bruno Cardio", "Carla Pediatra", "Ana Cardio"]


def test_ordena_pela_avaliacao_e_deixa_sem_nota_no_fim(client, agenda):
    resposta = client.get(ROTA, params={"ordenar_por": "avaliacao"})

    assert resposta.status_code == 200
    assert _nomes(resposta) == ["Carla Pediatra", "Ana Cardio", "Bruno Cardio"]


def test_horario_marcado_como_ocupado_nao_aparece(client, db, agenda):
    _criar_horario(db, agenda["carla"], DEPOIS, time(10, 0), time(10, 30), ocupado=True)
    db.commit()

    resposta = client.get(ROTA, params={"especialidade": "Pediatria"})

    assert resposta.status_code == 200
    assert [h["data_consulta"] for h in resposta.json()[0]["horarios_disponiveis"]] == [
        AMANHA.isoformat()
    ]


def test_horario_com_consulta_agendada_nao_aparece_mesmo_sem_a_flag(client, db, agenda):
    """A flag `ocupado` pode não ter sido marcada; a consulta em si já basta."""
    usuario = Usuario(
        id=uuid.uuid4(),
        nome="Paciente da Busca",
        cpf="333.333.3301",
        orgao_emissor="SSP-PI",
        data_nascimento=date(1990, 1, 10),
        genero="Não informado",
        telefone="(89) 96666-0001",
        email="pacientebusca@email.com",
        status=True,
    )
    db.add(usuario)
    db.flush()
    paciente = Paciente(id_usuario=usuario.id)
    db.add(paciente)
    db.flush()

    db.add(
        Consulta(
            id_paciente=paciente.id_paciente,
            id_esp_prof=agenda["bruno"].id_esp_prof,
            data=AMANHA,
            hora=time(14, 0),
            tipo="online",
            status="agendada",
            valor=150.00,
        )
    )
    db.commit()

    resposta = client.get(ROTA, params={"especialidade": "cardio"})

    assert resposta.status_code == 200
    assert _nomes(resposta) == ["Ana Cardio"]


def test_profissional_sem_horario_livre_fica_fora_da_lista(client, db):
    sem_agenda = _criar_profissional(db, "Davi Sem Agenda", 4)
    _criar_vinculo(db, sem_agenda, "Ortopedia", 100.0)
    db.commit()

    resposta = client.get(ROTA)

    assert resposta.status_code == 200
    assert resposta.json() == []


def test_profissional_inativo_nao_aparece(client, db):
    inativo = _criar_profissional(db, "Elisa Inativa", 5, ativo=False)
    vinculo = _criar_vinculo(db, inativo, "Neurologia", 100.0)
    _criar_horario(db, vinculo, AMANHA, time(9, 0), time(9, 30))
    db.commit()

    resposta = client.get(ROTA)

    assert resposta.status_code == 200
    assert resposta.json() == []


def test_data_passada_no_filtro_nao_traz_agenda_vencida(client, db, agenda):
    _criar_horario(db, agenda["carla"], ONTEM, time(9, 0), time(9, 30))
    db.commit()

    resposta = client.get(ROTA, params={"data_inicio": ONTEM.isoformat()})

    assert resposta.status_code == 200
    datas = [
        horario["data_consulta"]
        for ficha in resposta.json()
        for horario in ficha["horarios_disponiveis"]
    ]
    assert ONTEM.isoformat() not in datas


def test_horario_de_hoje_que_ja_passou_nao_aparece(client, db, agenda):
    agora = datetime.now()
    if agora.hour < 1:
        pytest.skip("Antes da 1h não existe horário de hoje já vencido para testar.")

    passado = (agora - timedelta(hours=1)).time().replace(second=0, microsecond=0)
    _criar_horario(db, agenda["carla"], date.today(), passado, agora.time())
    db.commit()

    resposta = client.get(ROTA, params={"especialidade": "Pediatria"})

    assert resposta.status_code == 200
    assert [h["data_consulta"] for h in resposta.json()[0]["horarios_disponiveis"]] == [
        AMANHA.isoformat()
    ]


def test_periodo_invertido_recusa_a_busca(client, agenda):
    resposta = client.get(
        ROTA, params={"data_inicio": DEPOIS.isoformat(), "data_fim": AMANHA.isoformat()}
    )

    assert resposta.status_code == 400
    assert resposta.json() == {
        "mensagem": "A data inicial não pode ser posterior à data final."
    }


def test_faixa_de_valor_invertida_recusa_a_busca(client, agenda):
    resposta = client.get(ROTA, params={"valor_min": 500, "valor_max": 100})

    assert resposta.status_code == 400
    assert resposta.json() == {
        "mensagem": "O valor mínimo não pode ser maior que o valor máximo."
    }


def test_valor_negativo_e_recusado_na_validacao_da_rota(client, agenda):
    resposta = client.get(ROTA, params={"valor_min": -10})

    assert resposta.status_code == 422


def test_ficha_traz_os_dados_que_o_paciente_usa_para_escolher(client, agenda):
    resposta = client.get(ROTA, params={"especialidade": "Pediatria"})

    assert resposta.status_code == 200
    ficha = resposta.json()[0]
    assert ficha["id_esp_prof"] == agenda["carla"].id_esp_prof
    assert ficha["especialidade"] == "Pediatria"
    assert ficha["valor_consulta"] == 200.0
    assert ficha["avaliacao"] == 5.0
    assert ficha["conselho"] == "CRM-PI 54321"
    assert ficha["info_profissional"] == "Atende desde 1993."
    assert ficha["horarios_disponiveis"] == [
        {
            "id_horario": ficha["horarios_disponiveis"][0]["id_horario"],
            "data_consulta": AMANHA.isoformat(),
            "hora_inicio": "08:00:00",
            "hora_fim": "08:30:00",
        }
    ]
