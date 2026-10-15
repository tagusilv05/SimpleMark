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
    Hoje adiciona a coluna nota (1 a 5) em avaliacao, se ainda não existir.
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
