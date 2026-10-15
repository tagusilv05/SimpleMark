"""Ajustes de tabelas que já existem no banco.

O Base.metadata.create_all cria tabelas novas, mas não acrescenta colunas em
tabelas que já foram criadas. Aqui entram esses acréscimos, sempre idempotentes
(podem rodar a cada inicialização sem efeito colateral).
"""

from sqlalchemy import text

from database.connection import engine


def aplicar_migracoes() -> None:
    """Acrescenta colunas que faltam em tabelas já existentes.

    Só roda no PostgreSQL; em outros bancos (ex.: SQLite dos testes) não faz nada.
    Hoje adiciona a coluna nota (1 a 5) em avaliacao e as colunas da
    videochamada (Jitsi Meet) em consulta, se ainda não existirem. Também
    remove o que sobrou da integração antiga com o Google Meet.
    """
    if engine.dialect.name != "postgresql":
        return
    with engine.begin() as conexao:
        # Nota de 1 a 5 estrelas na avaliação da consulta (NULL = sem estrelas).
        conexao.execute(
            text(
                "ALTER TABLE avaliacao "
                "ADD COLUMN IF NOT EXISTS nota SMALLINT "
                "CONSTRAINT ck_avaliacao_nota CHECK (nota BETWEEN 1 AND 5)"
            )
        )
        # Videochamada (Jitsi Meet) da consulta.
        conexao.execute(text("ALTER TABLE consulta ADD COLUMN IF NOT EXISTS meet_link VARCHAR(255)"))
        conexao.execute(
            text("ALTER TABLE consulta ADD COLUMN IF NOT EXISTS data_geracao_link TIMESTAMP WITH TIME ZONE")
        )
        # Restos da integração com o Google Meet, que deixou de existir. O id do
        # evento e o status da integração só faziam sentido com o Google.
        conexao.execute(text("DROP INDEX IF EXISTS ix_consulta_google_event_id"))
        conexao.execute(text("ALTER TABLE consulta DROP COLUMN IF EXISTS google_event_id"))
        conexao.execute(
            text("ALTER TABLE consulta DROP CONSTRAINT IF EXISTS ck_consulta_status_integracao_meet")
        )
        conexao.execute(text("ALTER TABLE consulta DROP COLUMN IF EXISTS status_integracao_meet"))
        # Links antigos do Google Meet não valem mais: a consulta ganha um link
        # do Jitsi sob demanda (ver services/videochamada.py).
        conexao.execute(
            text(
                "UPDATE consulta SET meet_link = NULL, data_geracao_link = NULL "
                "WHERE meet_link LIKE 'https://meet.google.com/%'"
            )
        )
        # Um link por consulta e nunca a mesma sala em duas consultas.
        conexao.execute(
            text("CREATE UNIQUE INDEX IF NOT EXISTS ix_consulta_meet_link ON consulta (meet_link)")
        )
