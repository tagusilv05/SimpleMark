"""Testes da listagem existente de consultas do profissional."""


def test_lista_consultas_inclui_vinculo_de_especialidade(client, cenario):
    profissional = cenario["profissionais"][1]
    consulta = cenario["consultas"][1]

    resposta = client.get(
        f"/api/v1/consultas_profissionais/{profissional.id_profissional}/consultas",
        params={
            "status": "",
            "data_inicio": "2026-01-20",
            "data_fim": "2026-01-20",
        },
    )

    assert resposta.status_code == 200
    consultas = resposta.json()
    assert len(consultas) == 1
    assert consultas[0]["id_consulta"] == consulta.id_consulta
    assert consultas[0]["id_esp_prof"] == consulta.id_esp_prof
