# Testes da videochamada (Jitsi Meet) da consulta.
#
# O link é gerado no próprio backend, sem rede. O SMTP é trocado por um dublê:
# nenhum teste envia e-mail de verdade. As tarefas em segundo plano rodam na
# mesma sessão do teste, e o backoff não espera de verdade (as esperas ficam
# registradas).
"""Testes da videochamada (Jitsi Meet) da consulta."""
import logging
import re
from datetime import date, time, timedelta
from types import SimpleNamespace

import pytest
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from dependencies.autenticacao import usuario_atual
from models.models import Consulta, DataHorario, Usuario
from services import videochamada
from services.envio_email import ErroEnvioEmail

# "simplemark-" + token_urlsafe(16): 16 bytes viram 22 caracteres base64url.
LINK_JITSI = re.compile(r"^https://meet\.jit\.si/simplemark-[A-Za-z0-9_-]{22}$")


class _SessaoCompartilhada:
    """A sessão do teste, sem deixar a tarefa em segundo plano fechá-la."""

    def __init__(self, db):
        """Guarda a sessão real do teste."""
        self._db = db

    def __getattr__(self, nome):
        """Repassa qualquer atributo para a sessão real."""
        return getattr(self._db, nome)

    def close(self):
        """Ignora o fechamento para a sessão seguir aberta no teste."""
        pass


@pytest.fixture
def integracoes(monkeypatch, db):
    """Troca sessão, envio de e-mail e espera do backoff por dublês."""
    monkeypatch.delenv("JITSI_BASE_URL", raising=False)
    dubles = SimpleNamespace(emails=[], esperas=[])
    monkeypatch.setattr(videochamada, "fabrica_sessao", lambda: _SessaoCompartilhada(db))
    monkeypatch.setattr(videochamada, "remetente_email", dubles.emails.append)
    monkeypatch.setattr(videochamada, "esperar", dubles.esperas.append)
    return dubles


@pytest.fixture
def agenda(db, cenario):
    """Dois horários livres do profissional 1 daqui a 10 dias (14h e 16h)."""
    esp_prof = cenario["consultas"][1].id_esp_prof
    dia = date.today() + timedelta(days=10)
    for inicio, fim in ((time(14, 0), time(14, 45)), (time(16, 0), time(16, 45))):
        db.add(DataHorario(id_esp_prof=esp_prof, data_consulta=dia, hora_inicio=inicio, hora_fim=fim))
    db.commit()

    usuarios = {
        "paciente": db.get(Usuario, cenario["paciente"].id_usuario),
        "medico": db.get(Usuario, cenario["profissionais"][1].id_usuario),
        "outro_medico": db.get(Usuario, cenario["profissionais"][2].id_usuario),
    }
    return SimpleNamespace(
        esp_prof=esp_prof,
        dia=dia,
        id_paciente=cenario["paciente"].id_paciente,
        id_especialidade=cenario["profissionais"][1].especialidades[0].id_especialidade,
        **usuarios,
    )


@pytest.fixture
def nova_consulta(db, agenda):
    """Cria uma consulta sem link, como as que existiam antes da integração."""

    def _criar(hora=time(14, 0), status="agendada") -> int:
        """Grava a consulta no horário e status pedidos e devolve o id."""
        consulta = Consulta(
            id_paciente=agenda.id_paciente,
            id_esp_prof=agenda.esp_prof,
            data=agenda.dia,
            hora=hora,
            tipo="consulta",
            status=status,
            valor=200.00,
        )
        db.add(consulta)
        db.commit()
        return consulta.id_consulta

    return _criar


@pytest.fixture
def logar(app):
    """Fábrica que loga o usuário informado trocando a dependência de sessão."""
    def _logar(usuario):
        """Faz o usuário informado ser o usuário logado."""
        app.dependency_overrides[usuario_atual] = lambda: usuario

    yield _logar
    app.dependency_overrides.pop(usuario_atual, None)


def _texto(mensagem) -> str:
    """Extrai o corpo em texto puro do e-mail."""
    return mensagem.get_body(preferencelist=("plain",)).get_content()


def _consulta(db, id_consulta) -> Consulta:
    """Relê a consulta do banco, descartando o cache da sessão."""
    db.expire_all()
    return db.get(Consulta, id_consulta)


def _com_link(db, nova_consulta, **kwargs) -> tuple[int, str]:
    """Cria uma consulta, gera o link dela e devolve id e link."""
    id_consulta = nova_consulta(**kwargs)
    videochamada.garantir_link(db, id_consulta)
    return id_consulta, _consulta(db, id_consulta).meet_link


# ---------------------------------------------------------------------------
# Geração do link
# ---------------------------------------------------------------------------


def test_confirmar_consulta_gera_link_e_envia_email_ao_paciente(client, db, agenda, integracoes):
    """Confirmar consulta gera link Jitsi e envia ao paciente e-mail sem excessos."""
    resposta = client.post(
        "/consulta/confirmar-consulta",
        json={
            "id_usuario_paciente": str(agenda.paciente.id),
            "id_usuario_profissional": str(agenda.medico.id),
            "id_especialidade": agenda.id_especialidade,
            "data": agenda.dia.isoformat(),
            "hora": "14:00:00",
            "tipo": "consulta",
            "status": "agendado",
            "valor": 200.0,
        },
    )

    assert resposta.status_code == 200
    assert set(resposta.json()) == {"mensagem", "id_consulta"}  # resposta não mudou
    id_consulta = resposta.json()["id_consulta"]
    consulta = _consulta(db, id_consulta)
    assert LINK_JITSI.match(consulta.meet_link)
    assert consulta.data_geracao_link is not None

    assert len(integracoes.emails) == 1
    email = integracoes.emails[0]
    texto = _texto(email)
    assert email["To"] == agenda.paciente.email
    assert email["Subject"] == "Sua teleconsulta está confirmada"
    assert "Profissional 1" in texto
    assert f"{agenda.dia:%d/%m/%Y} às 14:00 (horário de Brasília)" in texto
    assert consulta.meet_link in texto
    assert "câmera" in texto and "minutos antes" in texto
    assert "Google" not in email.as_string()
    assert "Cardiologia" not in email.as_string()  # LGPD: nada além do necessário


def test_nome_da_sala_e_so_prefixo_mais_aleatorio(db, nova_consulta, integracoes, monkeypatch):
    """O nome da sala é só o prefixo mais o token aleatório de 16 bytes."""
    pedidos = []

    def _aleatorio(nbytes):
        """Registra o tamanho pedido e devolve um token fixo."""
        pedidos.append(nbytes)
        return "TOKENALEATORIO"

    monkeypatch.setattr(videochamada.secrets, "token_urlsafe", _aleatorio)
    id_consulta = nova_consulta()

    videochamada.garantir_link(db, id_consulta)

    # Nada da consulta (id, nomes, e-mail) entra no nome: só o prefixo e o aleatório.
    assert _consulta(db, id_consulta).meet_link == "https://meet.jit.si/simplemark-TOKENALEATORIO"
    assert pedidos == [16]


def test_nome_da_sala_e_imprevisivel(integracoes):
    """500 links gerados são todos diferentes e no formato esperado."""
    links = {videochamada.gerar_link_sala() for _ in range(500)}

    assert len(links) == 500
    assert all(LINK_JITSI.match(link) for link in links)


def test_jitsi_base_url_configuravel(monkeypatch):
    """JITSI_BASE_URL muda o servidor usado no link."""
    monkeypatch.setenv("JITSI_BASE_URL", "https://jitsi.simplemark.test/")

    link = videochamada.gerar_link_sala()

    assert re.match(r"^https://jitsi\.simplemark\.test/simplemark-[A-Za-z0-9_-]{22}$", link)


def test_nunca_dois_links_para_a_mesma_consulta(db, nova_consulta, integracoes):
    """Consulta que já tem link não ganha outro, nem pela tarefa de e-mail."""
    id_consulta, link = _com_link(db, nova_consulta)

    assert videochamada.garantir_link(db, id_consulta) is False
    videochamada.enviar_email_confirmacao(id_consulta)

    assert _consulta(db, id_consulta).meet_link == link


def test_link_gravado_por_outra_requisicao_nao_e_trocado(db, nova_consulta, integracoes):
    """Link gravado por outra requisição é relido do banco e não é trocado."""
    id_consulta = nova_consulta()
    consulta = db.get(Consulta, id_consulta)
    assert consulta.meet_link is None  # a sessão "acha" que ainda não há link

    # Outra requisição grava o link sem passar pelo objeto desta sessão, que
    # continua em memória com meet_link vazio (caso do GET concorrente no PostgreSQL).
    db.execute(
        update(Consulta)
        .where(Consulta.id_consulta == id_consulta)
        .values(meet_link="https://meet.jit.si/simplemark-outrarequisicao000000")
        .execution_options(synchronize_session=False)
    )

    assert videochamada.garantir_link(db, id_consulta) is False  # releu a linha e viu o link


def test_banco_impede_a_mesma_sala_em_duas_consultas(db, nova_consulta, integracoes):
    """O banco recusa o mesmo link em duas consultas com IntegrityError."""
    _, link = _com_link(db, nova_consulta)
    outra = db.get(Consulta, nova_consulta(hora=time(16, 0)))

    outra.meet_link = link
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_tarefa_de_email_gera_o_link_que_faltou(db, nova_consulta, integracoes):
    """A tarefa de e-mail gera o link que faltava e o envia ao paciente."""
    id_consulta = nova_consulta()

    videochamada.enviar_email_confirmacao(id_consulta)

    link = _consulta(db, id_consulta).meet_link
    assert LINK_JITSI.match(link)
    assert len(integracoes.emails) == 1
    assert link in _texto(integracoes.emails[0])


def test_falha_no_email_nao_afeta_o_link(db, nova_consulta, integracoes, monkeypatch):
    """Falha no e-mail após 3 tentativas com backoff mantém o link gravado."""
    def _smtp_fora(_mensagem):
        """Simula o servidor de e-mail fora do ar."""
        raise ErroEnvioEmail("Falha no servidor de e-mail (SMTPServerDisconnected).")

    monkeypatch.setattr(videochamada, "remetente_email", _smtp_fora)
    id_consulta, link = _com_link(db, nova_consulta)

    videochamada.enviar_email_confirmacao(id_consulta)

    assert _consulta(db, id_consulta).meet_link == link
    assert integracoes.esperas == [2.0, 4.0]  # 3 tentativas com backoff exponencial


def test_falha_temporaria_no_email_e_recuperada_na_retentativa(db, nova_consulta, integracoes, monkeypatch):
    """Falha temporária no e-mail é superada na segunda tentativa."""
    falhas = [ErroEnvioEmail("Falha no servidor de e-mail (SMTPServerDisconnected).")]

    def _smtp_instavel(mensagem):
        """Falha na primeira chamada e envia normalmente nas seguintes."""
        if falhas:
            raise falhas.pop()
        integracoes.emails.append(mensagem)

    monkeypatch.setattr(videochamada, "remetente_email", _smtp_instavel)
    id_consulta, _ = _com_link(db, nova_consulta)

    videochamada.enviar_email_confirmacao(id_consulta)

    assert integracoes.esperas == [2.0]
    assert len(integracoes.emails) == 1


@pytest.mark.parametrize("status", ["cancelado", "realizada"])
def test_consulta_inativa_nao_recebe_link_nem_email(db, nova_consulta, integracoes, status):
    """Consulta cancelada ou realizada não recebe link nem e-mail."""
    id_consulta = nova_consulta(status=status)

    assert videochamada.garantir_link(db, id_consulta) is False
    videochamada.enviar_email_confirmacao(id_consulta)

    assert _consulta(db, id_consulta).meet_link is None
    assert integracoes.emails == []


def test_logs_nao_trazem_link_nem_dado_pessoal(db, agenda, nova_consulta, integracoes, caplog):
    """Os logs não trazem a sala, o e-mail nem o nome do paciente."""
    caplog.set_level(logging.INFO, logger="simplemark.videochamada")
    id_consulta, link = _com_link(db, nova_consulta)
    videochamada.enviar_email_confirmacao(id_consulta)

    assert caplog.records
    sala = link.rsplit("/", 1)[1]
    for registro in caplog.messages:
        assert sala not in registro
        assert agenda.paciente.email not in registro
        assert agenda.paciente.nome not in registro


# ---------------------------------------------------------------------------
# Consulta do link (acesso e geração sob demanda) e reprocessamento
# ---------------------------------------------------------------------------


def test_link_visivel_para_o_medico_e_o_paciente_da_consulta(client, db, agenda, nova_consulta, integracoes, logar):
    """Médico e paciente da consulta veem o link, sem status interno."""
    id_consulta, link = _com_link(db, nova_consulta)

    for usuario in (agenda.medico, agenda.paciente):
        logar(usuario)
        resposta = client.get(f"/api/v1/consultas/{id_consulta}/videochamada")
        assert resposta.status_code == 200
        assert resposta.json()["meet_link"] == link
        assert "status_integracao_meet" not in resposta.json()


def test_outro_medico_recebe_404_e_nao_gera_link(client, db, agenda, nova_consulta, integracoes, logar):
    """Médico alheio recebe 404 em ver, reprocessar e cancelar, sem gerar link."""
    id_consulta = nova_consulta()
    logar(agenda.outro_medico)

    ver = client.get(f"/api/v1/consultas/{id_consulta}/videochamada")
    reprocessar = client.post(f"/api/v1/consultas/{id_consulta}/videochamada/reprocessar")
    cancelar = client.patch(f"/api/v1/consultas/{id_consulta}/cancelar")

    assert ver.status_code == reprocessar.status_code == cancelar.status_code == 404
    assert "meet_link" not in ver.json()
    assert _consulta(db, id_consulta).meet_link is None
    assert integracoes.emails == []


def test_consulta_antiga_ganha_link_sob_demanda(client, db, agenda, nova_consulta, integracoes, logar):
    """Consulta sem link ganha um ao ser consultada, sempre o mesmo, e um e-mail."""
    id_consulta = nova_consulta()  # sem link, como as consultas anteriores à integração
    logar(agenda.medico)

    primeira = client.get(f"/api/v1/consultas/{id_consulta}/videochamada")
    segunda = client.get(f"/api/v1/consultas/{id_consulta}/videochamada")

    link = primeira.json()["meet_link"]
    assert LINK_JITSI.match(link)
    assert segunda.json()["meet_link"] == link
    assert _consulta(db, id_consulta).meet_link == link
    assert len(integracoes.emails) == 1  # o paciente recebe o link uma vez
    assert link in _texto(integracoes.emails[0])


def test_lista_de_consultas_do_paciente_traz_o_link(client, db, agenda, nova_consulta, integracoes, logar):
    """A lista de consultas do paciente traz o link, sem status interno."""
    id_consulta, link = _com_link(db, nova_consulta)
    logar(agenda.paciente)

    itens = client.get("/consultas/minhas").json()["itens"]

    item = next(i for i in itens if i["id_consulta"] == id_consulta)
    assert item["meet_link"] == link
    assert "status_integracao_meet" not in item


def test_reprocessar_gera_o_link_que_falta_e_envia_o_email(client, db, agenda, nova_consulta, integracoes, logar):
    """Reprocessar consulta sem link responde 202, gera o link e envia e-mail."""
    id_consulta = nova_consulta()
    logar(agenda.paciente)

    resposta = client.post(f"/api/v1/consultas/{id_consulta}/videochamada/reprocessar")

    assert resposta.status_code == 202
    link = resposta.json()["consulta"]["meet_link"]
    assert LINK_JITSI.match(link)
    assert _consulta(db, id_consulta).meet_link == link
    assert len(integracoes.emails) == 1


def test_reprocessar_mantem_o_link_e_reenvia_o_email(client, db, agenda, nova_consulta, integracoes, logar):
    """Reprocessar consulta com link responde 202, mantém o link e reenvia e-mail."""
    id_consulta, link = _com_link(db, nova_consulta)
    logar(agenda.medico)

    resposta = client.post(f"/api/v1/consultas/{id_consulta}/videochamada/reprocessar")

    assert resposta.status_code == 202
    assert resposta.json()["consulta"]["meet_link"] == link
    assert _consulta(db, id_consulta).meet_link == link
    assert len(integracoes.emails) == 1
    assert link in _texto(integracoes.emails[0])


def test_reprocessar_recusa_consulta_cancelada(client, db, agenda, nova_consulta, integracoes, logar):
    """Reprocessar consulta cancelada responde 400 sem gerar link nem e-mail."""
    id_consulta = nova_consulta(status="cancelada")
    logar(agenda.paciente)

    resposta = client.post(f"/api/v1/consultas/{id_consulta}/videochamada/reprocessar")

    assert resposta.status_code == 400
    assert _consulta(db, id_consulta).meet_link is None
    assert integracoes.emails == []


# ---------------------------------------------------------------------------
# Reagendamento
# ---------------------------------------------------------------------------


def test_medico_reagenda_mantendo_o_link_e_avisa_o_paciente(client, db, agenda, nova_consulta, integracoes, logar):
    """Médico reagenda, o link é mantido e o paciente recebe o novo horário."""
    id_consulta, link = _com_link(db, nova_consulta)
    logar(agenda.medico)

    resposta = client.patch(
        f"/api/v1/consultas/{id_consulta}/reagendar",
        json={"data": agenda.dia.isoformat(), "hora": "16:00:00"},
    )

    assert resposta.status_code == 200
    assert resposta.json()["consulta"]["hora"] == "16:00:00"
    assert resposta.json()["consulta"]["meet_link"] == link
    consulta = _consulta(db, id_consulta)
    assert consulta.hora == time(16, 0)
    assert consulta.meet_link == link

    email = integracoes.emails[-1]
    assert email["Subject"] == "Sua teleconsulta foi reagendada"
    texto = _texto(email)
    assert "às 14:00" in texto and "às 16:00" in texto
    assert link in texto
    assert "continua o mesmo" in texto


def test_reagendar_consulta_sem_link_gera_o_link(client, db, agenda, nova_consulta, integracoes, logar):
    """Reagendar consulta sem link gera o link e o envia no e-mail."""
    id_consulta = nova_consulta()
    logar(agenda.medico)

    resposta = client.patch(
        f"/api/v1/consultas/{id_consulta}/reagendar",
        json={"data": agenda.dia.isoformat(), "hora": "16:00:00"},
    )

    link = resposta.json()["consulta"]["meet_link"]
    assert LINK_JITSI.match(link)
    assert link in _texto(integracoes.emails[-1])


def test_paciente_nao_pode_reagendar(client, agenda, nova_consulta, integracoes, logar):
    """Paciente que tenta reagendar recebe 403 com mensagem clara."""
    id_consulta = nova_consulta()
    logar(agenda.paciente)

    resposta = client.patch(
        f"/api/v1/consultas/{id_consulta}/reagendar",
        json={"data": agenda.dia.isoformat(), "hora": "16:00:00"},
    )

    assert resposta.status_code == 403
    assert resposta.json()["mensagem"] == "Somente o profissional responsável pode reagendar a consulta."


def test_reagendar_exige_horario_existente_e_livre(client, agenda, nova_consulta, integracoes, logar):
    """Horário fora da agenda dá 400, ocupado dá 409, e nenhum e-mail sai."""
    id_consulta = nova_consulta()
    nova_consulta(hora=time(16, 0))  # outra consulta já ocupa as 16h
    logar(agenda.medico)
    url = f"/api/v1/consultas/{id_consulta}/reagendar"

    fora_da_agenda = client.patch(url, json={"data": agenda.dia.isoformat(), "hora": "09:00:00"})
    ocupado = client.patch(url, json={"data": agenda.dia.isoformat(), "hora": "16:00:00"})

    assert fora_da_agenda.status_code == 400
    assert ocupado.status_code == 409
    assert integracoes.emails == []


# ---------------------------------------------------------------------------
# Cancelamento
# ---------------------------------------------------------------------------


def test_cancelar_esconde_o_link_e_avisa_o_paciente(client, db, agenda, nova_consulta, integracoes, logar):
    """Cancelar oculta o link, avisa o paciente sem link e recusa 2º cancelamento."""
    id_consulta, link = _com_link(db, nova_consulta)
    logar(agenda.paciente)

    resposta = client.patch(f"/api/v1/consultas/{id_consulta}/cancelar")

    assert resposta.status_code == 200
    assert resposta.json()["consulta"]["status_consulta"] == "cancelada"
    assert resposta.json()["consulta"]["meet_link"] is None
    consulta = _consulta(db, id_consulta)
    assert consulta.status == "cancelada"
    assert consulta.meet_link == link  # fica gravado, mas não é mais exibido

    email = integracoes.emails[-1]
    assert email["Subject"] == "Sua teleconsulta foi cancelada"
    assert link.rsplit("/", 1)[1] not in email.as_string()
    assert "meet.jit.si" not in email.as_string()

    segunda_vez = client.patch(f"/api/v1/consultas/{id_consulta}/cancelar")
    assert segunda_vez.status_code == 400


def test_consulta_cancelada_nao_devolve_link_em_nenhuma_rota(client, db, agenda, nova_consulta, integracoes, logar):
    """Consulta cancelada não devolve o link nem na rota nem na lista."""
    id_consulta, _ = _com_link(db, nova_consulta)
    logar(agenda.medico)
    client.patch(f"/api/v1/consultas/{id_consulta}/cancelar")

    ver = client.get(f"/api/v1/consultas/{id_consulta}/videochamada")
    logar(agenda.paciente)
    itens = client.get("/consultas/minhas").json()["itens"]

    assert ver.status_code == 200
    assert ver.json()["meet_link"] is None
    assert next(i for i in itens if i["id_consulta"] == id_consulta)["meet_link"] is None
