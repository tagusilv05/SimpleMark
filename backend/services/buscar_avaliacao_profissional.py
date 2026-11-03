"""Avaliações recebidas por um profissional em uma especialidade."""

# CRIADO: JOAO MARCOS 

from sqlalchemy.orm import Session

from models.models import Consulta, ProfissionalEspecialidade
from repositories.buscar_avaliacao_profissional import (
    buscar_consultas_do_profissional as repositories_buscar_consultas_do_profissional,
    buscar_profissional_especialidade as repositories_buscar_profissional_especialidade,
)
from services.porfissional_minha_conta import verificar_profissional_usuario as services_verificar_profissional_usuario


def buscar_avaliacoes_profissional(dados, db: Session):
    """Lista as avaliações do profissional na especialidade (ou em todas se não informada).

    Devolve a lista (paciente, data, nota e feedback), o total e a contagem por
    nota.
    """

    # 1. Verifica se o usuário é um profissional
    profissional = services_verificar_profissional_usuario(dados.id_usuario, db)

    # 2. Busca as consultas (por especialidade ou todas as especialidades do profissional)
    if dados.id_especialidade:
        prof_esp = repositories_buscar_profissional_especialidade(
            profissional.id_profissional, dados.id_especialidade, db
        )
        if prof_esp is None:
            raise ValueError("Especialidade não encontrada para este profissional")
        consultas = repositories_buscar_consultas_do_profissional(prof_esp.id_esp_prof, db)
    else:
        consultas = (
            db.query(Consulta)
            .join(
                ProfissionalEspecialidade,
                Consulta.id_esp_prof == ProfissionalEspecialidade.id_esp_prof,
            )
            .filter(
                ProfissionalEspecialidade.id_profissional == profissional.id_profissional
            )
            .all()
        )

    # 3. Lista que vai armazenar as avaliações
    avaliacao = []

    # 4. Contador das notas
    sub_total = {
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0,
        "5": 0,
    }

    # 5. Percorre as consultas
    for consulta in consultas:
        if consulta.avaliacao is None:
            continue

        paciente = consulta.paciente
        if paciente is None:
            continue

        usuario_paciente = paciente.usuario
        if usuario_paciente is None:
            continue

        avaliacao.append({
            "nome_paciente": usuario_paciente.nome,
            "data_consulta": consulta.data,
            "feedback": consulta.avaliacao.feedback,
            "avaliacao": consulta.avaliacao.avaliacao,
        })

        nota_str = str(consulta.avaliacao.avaliacao)
        if nota_str in sub_total:
            sub_total[nota_str] += 1

    # 6. Total de avaliações
    total = len(avaliacao)

    return avaliacao, total, sub_total
