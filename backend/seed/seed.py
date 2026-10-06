# CRIADO: JOAO MARCOS 

"""
Este arquivo é responsável por criar e inserir dados no banco de dados,

As tabelas preenchidas pelo seed são:
- Usuario
- Paciente
- Profissional
- Endereco
- Especialidade
- InfoConselho
- ProfissionalEspecialidade
-  especialidades 

As tabelas de consulta, horário, pagamento, avaliação e documento clínico e data_horario
não são preenchidas por este seed.
"""
import uuid
from datetime import date
import random
from database.connection import SessionLocal

from models.models import (
    Usuario,
    Paciente,
    Profissional,
    Endereco,
    Especialidade,
    InfoConselho,
    ProfissionalEspecialidade,
)

def criar_seed():
    db = SessionLocal()
    try:
        especialidades = [
            Especialidade(especialidade="Cardiologia"),
            Especialidade(especialidade="Dermatologia"),
            Especialidade(especialidade="Pediatria"),
            Especialidade(especialidade="Ortopedia"),
            Especialidade(especialidade="Neurologia"),
        ]

        db.add_all(especialidades)
        db.flush()

        for i in range(1, 11):

            usuario = Usuario(
                id=uuid.uuid4(),
                nome=f"Paciente {i}",
                cpf=f"000.000.00{i:02d}",
                orgao_emissor="SSP-PI",
                data_nascimento=date(1990, i if i <= 12 else 1, 10),
                genero="Não informado",
                telefone=f"(89) 99999-{i:04d}",
                email=f"paciente{i}@email.com",
                status=True
            )

            db.add(usuario)
            db.flush()

            paciente = Paciente(
                id_usuario=usuario.id
            )

            db.add(paciente)

            endereco = Endereco(
                id_usuario=usuario.id,
                cep="64600-000",
                cidade="Picos",
                logradouro=f"Rua dos Pacientes, {i}",
                numero=str(100 + i),
                bairro="Centro",
                complemento=None
            )

            db.add(endereco)

        for i in range(1, 6):

            usuario = Usuario(
                id=uuid.uuid4(),
                nome=f"Profissional {i}",
                cpf=f"111.111.11{i:02d}",
                orgao_emissor="SSP-PI",
                data_nascimento=date(1980, i, 15),
                genero="Não informado",
                telefone=f"(89) 98888-{i:04d}",
                email=f"profissional{i}@email.com",
                status=True
            )

            db.add(usuario)
            db.flush()

            profissional = Profissional(
                id_usuario=usuario.id,
                path_imagem=None,
                info_profissional=f"Informações profissionais do profissional {i}"
            )

            db.add(profissional)
            db.flush()

            endereco = Endereco(
                id_usuario=usuario.id,
                cep="64600-000",
                cidade="Picos",
                logradouro=f"Rua dos Profissionais, {i}",
                numero=str(200 + i),
                bairro="Centro",
                complemento=f"Sala {i}"
            )

            db.add(endereco)

            conselho = InfoConselho(
                numero_conselho=f"CRM-PI {10000 + i}",
                orgao_conselho="CRM-PI"
            )

            db.add(conselho)
            db.flush()

            especialidade = random.choice(especialidades)

            profissional_especialidade = ProfissionalEspecialidade(
                id_profissional=profissional.id_profissional,
                id_especialidade=especialidade.id_especialidade,
                id_conselho=conselho.id_conselho,
                valor_consulta=200.00 + (i * 20),
                avaliacao=None
            )

            db.add(profissional_especialidade)  

        db.commit()

        print("SEED EXECUTADO COM SUCESSO")

    except Exception as e:

        db.rollback()

        print("Erro ao executar seed:")
        print(e)
    finally:
        db.close()
