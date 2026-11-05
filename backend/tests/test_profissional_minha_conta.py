# Testes de GET /profissionais/buscar-info-profissional/{id_usuario}.
"""A lista de especialidades do profissional traz o id do vínculo (id_esp_prof)."""
from fastapi import FastAPI
from fastapi.testclient import TestClient

from dependencies.database import get_db
from routers.porfissional_minha_conta import router as minha_conta_router


def test_especialidades_trazem_id_esp_prof(db, cenario):
    """A agenda do profissional usa o id_esp_prof para listar e criar horários."""
    app = FastAPI()
    app.include_router(minha_conta_router, prefix="/profissionais")
    app.dependency_overrides[get_db] = lambda: db
    profissional = cenario["profissionais"][1]
    [esp_prof] = profissional.especialidades

    resposta = TestClient(app).get(f"/profissionais/buscar-info-profissional/{profissional.id_usuario}")

    assert resposta.status_code == 200, resposta.text
    [especialidade] = resposta.json()["especialidade"]
    assert especialidade["nome"] == "Cardiologia"
    assert especialidade["id_esp_prof"] == esp_prof.id_esp_prof
