# CRIADO: JOAO MARCOS 

from sqlalchemy.orm import Session

from repositories.buscar_avaliacao_profissional import buscar_profissional_especialidade as repositories_buscar_profissional_especialidade
from repositories.confirmar_consulta import adicionar_consulta as repositories_adicionar_consulta

from services.porfissional_minha_conta import verificar_profissional_usuario as services_verificar_profissional_usuario
from services.usuario_minha_conta import verificar_paciente_usuario as servicer_verificar_paciente_usuario

# Recebe os dados da consulta para salvar no banco de dados.
def confirmar_consulta(dados, db: Session):

    try:

        profissional = services_verificar_profissional_usuario(dados.id_usuario_profissional, db)

        paciente = servicer_verificar_paciente_usuario(dados.id_usuario_paciente, db)

        prof_esp = repositories_buscar_profissional_especialidade(profissional.id_profissional, dados.id_especialidade, db)

        if prof_esp is None:
            raise ValueError("Especialidade não encontrada para este profissional")

        consulta = repositories_adicionar_consulta(dados, paciente.id_paciente, prof_esp.id_esp_prof, db)

        return consulta

    except ValueError:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise

    