
from datetime import date, time
from decimal import Decimal

from database.connection import SessionLocal
from models.acesso import Credencial
from core.seguranca import gerar_hash_senha

from models.models import (
    Usuario,
    Paciente,
    Profissional,
    InfoConselho,
    Especialidade,
    ProfissionalEspecialidade,
    DataHorario,
    Consulta,
    Avaliacao,
)


def criar_seed():
    db = SessionLocal()

    try:
        # ==========================================
        # 1. CADASTRAR OU LOCALIZAR O PACIENTE
        # ==========================================

        usuario_paciente = (
            db.query(Usuario)
            .filter(Usuario.email == "joaomarcos0416@gmail.com")
            .first()
        )

        if usuario_paciente is None:
            usuario_paciente = Usuario(
                nome="Joao Silva",
                cpf="041.609.790-17",
                orgao_emissor="SSP",
                data_nascimento=date(1995, 5, 15),
                genero="Masculino",
                telefone="8932439212",
                email="joaomarcos0416@gmail.com",
                status=True,
            )

            db.add(usuario_paciente)
            db.flush()

        paciente = (
            db.query(Paciente)
            .filter(Paciente.id_usuario == usuario_paciente.id)
            .first()
        )

        if paciente is None:
            paciente = Paciente(id_usuario=usuario_paciente.id)
            db.add(paciente)
            db.flush()

        # Cadastrar credencial do paciente, se ainda não existir
        credencial_paciente = (
            db.query(Credencial)
            .filter(Credencial.id_usuario == usuario_paciente.id)
            .first()
        )

        if credencial_paciente is None:
            credencial_paciente = Credencial(
                id_usuario=usuario_paciente.id,
                senha_hash=gerar_hash_senha("minhasenha123"),
                consentimento_lgpd=True,
                tentativas_login_falhas=0,
                bloqueado_ate=None,
            )

            db.add(credencial_paciente)

        # ==========================================
        # 2. CADASTRAR OU LOCALIZAR O MÉDICO
        # ==========================================

        usuario_medico = (
            db.query(Usuario)
            .filter(Usuario.email == "joaomarcos0416@outlook.com")
            .first()
        )

        if usuario_medico is None:
            usuario_medico = Usuario(
                nome="Marcos Silva",
                cpf="920.285.800-46",
                orgao_emissor="SSP",
                data_nascimento=date(1980, 3, 10),
                genero="Masculino",
                telefone="8932254654",
                email="joaomarcos0416@outlook.com",
                status=True,
            )

            db.add(usuario_medico)
            db.flush()

        medico = (
            db.query(Profissional)
            .filter(Profissional.id_usuario == usuario_medico.id)
            .first()
        )

        if medico is None:
            medico = Profissional(
                id_usuario=usuario_medico.id,
                info_profissional="Médico especialista em Cardiologia.",
            )

            db.add(medico)
            db.flush()

        # Cadastrar credencial do médico, se ainda não existir
        credencial_medico = (
            db.query(Credencial)
            .filter(Credencial.id_usuario == usuario_medico.id)
            .first()
        )

        if credencial_medico is None:
            credencial_medico = Credencial(
                id_usuario=usuario_medico.id,
                senha_hash=gerar_hash_senha("minhasenha123"),
                consentimento_lgpd=True,
                tentativas_login_falhas=0,
                bloqueado_ate=None,
            )

            db.add(credencial_medico)

        # ==========================================
        # 3. CADASTRAR OU LOCALIZAR A ESPECIALIDADE
        # ==========================================

        especialidade = (
            db.query(Especialidade)
            .filter(Especialidade.especialidade == "Cardiologia")
            .first()
        )

        if especialidade is None:
            especialidade = Especialidade(
                especialidade="Cardiologia"
            )

            db.add(especialidade)
            db.flush()

        # ==========================================
        # 4. CADASTRAR OU LOCALIZAR O CONSELHO
        # ==========================================

        conselho = (
            db.query(InfoConselho)
            .filter(
                InfoConselho.numero_conselho == "123456",
                InfoConselho.orgao_conselho == "CRM-PI",
            )
            .first()
        )

        if conselho is None:
            conselho = InfoConselho(
                numero_conselho="123456",
                orgao_conselho="CRM-PI",
            )

            db.add(conselho)
            db.flush()

        # ==========================================
        # 5. CADASTRAR OU LOCALIZAR O VÍNCULO
        # MÉDICO / ESPECIALIDADE
        # ==========================================

        medico_especialidade = (
            db.query(ProfissionalEspecialidade)
            .filter(
                ProfissionalEspecialidade.id_profissional
                == medico.id_profissional,
                ProfissionalEspecialidade.id_especialidade
                == especialidade.id_especialidade,
            )
            .first()
        )

        if medico_especialidade is None:
            medico_especialidade = ProfissionalEspecialidade(
                profissional=medico,
                especialidade=especialidade,
                conselho=conselho,
                valor_consulta=250.00,
            )

            db.add(medico_especialidade)
            db.flush()

        # ==========================================
        # 6. CADASTRAR HORÁRIOS DISPONÍVEIS
        # ==========================================

        horarios_disponiveis = [
            (date(2026, 11, 5), time(8, 0), time(9, 0)),
            (date(2026, 11, 5), time(9, 0), time(10, 0)),
            (date(2026, 11, 5), time(10, 0), time(11, 0)),
            (date(2026, 11, 5), time(14, 0), time(15, 0)),
            (date(2026, 11, 6), time(9, 0), time(10, 0)),
            (date(2026, 11, 6), time(14, 0), time(15, 0)),
        ]

        for data_consulta, hora_inicio, hora_fim in horarios_disponiveis:

            horario = (
                db.query(DataHorario)
                .filter(
                    DataHorario.id_esp_prof
                    == medico_especialidade.id_esp_prof,
                    DataHorario.data_consulta == data_consulta,
                    DataHorario.hora_inicio == hora_inicio,
                    DataHorario.hora_fim == hora_fim,
                )
                .first()
            )

            if horario is None:
                horario = DataHorario(
                    profissional_especialidade=medico_especialidade,
                    data_consulta=data_consulta,
                    hora_inicio=hora_inicio,
                    hora_fim=hora_fim,
                    ocupado=False,
                )

                db.add(horario)

        # ==========================================
        # 7. CADASTRAR OU LOCALIZAR A CONSULTA
        # ==========================================

        consulta = (
            db.query(Consulta)
            .filter(
                Consulta.id_paciente == paciente.id_paciente,
                Consulta.id_esp_prof
                == medico_especialidade.id_esp_prof,
                Consulta.data == date(2026, 10, 20),
                Consulta.hora == time(14, 0),
            )
            .first()
        )

        if consulta is None:
            consulta = Consulta(
                paciente=paciente,
                profissional_especialidade=medico_especialidade,
                data=date(2026, 10, 20),
                hora=time(14, 0),
                tipo="teleconsulta",
                status="realizada",
                valor=Decimal("250.00"),
            )

            db.add(consulta)
            db.flush()

        # ==========================================
        # 8. CADASTRAR OU LOCALIZAR A AVALIAÇÃO
        # ==========================================

        avaliacao = (
            db.query(Avaliacao)
            .filter(Avaliacao.id_consulta == consulta.id_consulta)
            .first()
        )

        if avaliacao is None:
            avaliacao = Avaliacao(
                consulta=consulta,
                nota=5,
                feedback=(
                    "Excelente atendimento! "
                    "O médico foi atencioso e explicou "
                    "todas as minhas dúvidas."
                ),
                avaliacao=5,
                data=date(2026, 10, 20),
                hora=time(15, 0),
            )

            db.add(avaliacao)

        # ==========================================
        # 9. SALVAR TUDO NO BANCO
        # ==========================================

        db.commit()

        # ==========================================
        # 10. EXIBIR RESULTADO NO TERMINAL
        # ==========================================

        print("\n========== SEED EXECUTADO ==========")
        print("Mensagem: Seed executado com sucesso!")
        print(f"ID do paciente: {paciente.id_paciente}")
        print(f"ID do médico: {medico.id_profissional}")
        print(
            "ID do vínculo médico/especialidade: "
            f"{medico_especialidade.id_esp_prof}"
        )
        print(f"ID da consulta: {consulta.id_consulta}")
        print(f"Nota da avaliação: {avaliacao.nota}/5")
        print(f"Feedback: {avaliacao.feedback}")
        print(f"Horários verificados: {len(horarios_disponiveis)}")

        print("\n========== AGENDA DO CARDIOLOGISTA ==========")

        for data_consulta, hora_inicio, hora_fim in horarios_disponiveis:
            print(
                f"Data: {data_consulta.strftime('%d/%m/%Y')} | "
                f"Início: {hora_inicio.strftime('%H:%M')} | "
                f"Fim: {hora_fim.strftime('%H:%M')}"
            )

        print("=============================================\n")

    except Exception as erro:
        db.rollback()
        print(f"\nERRO AO REALIZAR CADASTRO: {erro}")
        raise

    finally:
        db.close()
