# CRIADO: JOAO MARCOS 

from sqlalchemy.orm import Session

from repositories.buscar_avaliacao_profissional import (
    buscar_consultas_do_profissional as repositories_buscar_consultas_do_profissional,
    buscar_profissional_especialidade as repositories_buscar_profissional_especialidade
)

# Busca as avaliações de um profissional por especialidade,
# organizando os dados das avaliações, o total e a quantidade por nota.
from services.porfissional_minha_conta import verificar_profissional_usuario as services_verificar_profissional_usuario


def buscar_avaliacoes_profissional(dados, db: Session):

    # 1. Verifica se o usuário é um profissional
    profissional = services_verificar_profissional_usuario(dados.id_usuario, db)

    # 2. Busca a relação profissional + especialidade
    prof_esp = repositories_buscar_profissional_especialidade(profissional.id_profissional, dados.id_especialidade, db)

    if prof_esp is None:
        raise ValueError("Especialidade não encontrada para este profissional")

    # 3. Busca todas as consultas dessa relação
    consultas = repositories_buscar_consultas_do_profissional(prof_esp.id_esp_prof, db)

    # 4. Lista que vai armazenar as avaliações
    avaliacao = []

    # 5. Contador das notas
    sub_total = {
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0,
        "5": 0
    }

    # 6. Percorre as consultas
    for consulta in consultas:

        # Consulta pode não ter avaliação
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
            "avaliacao": consulta.avaliacao.avaliacao
        })

        sub_total[str(consulta.avaliacao.avaliacao)] += 1

    # 7. Verifica se encontrou alguma avaliação
    if not avaliacao:
        raise ValueError("Nenhuma avaliação encontrada para este profissional")

    # 8. Total de avaliações
    total = len(avaliacao)

    return avaliacao, total, sub_total
























