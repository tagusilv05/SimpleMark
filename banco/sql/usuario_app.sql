-- Usuário da API com o mínimo necessário: lê e grava dados, sem criar/alterar tabelas.
--
-- Rodar como o dono do banco (POSTGRES_USER), passando as variáveis do psql:
--   psql -v app_user=... -v app_password=... -v owner=... -v db=... -f usuario_app.sql
--
-- Idempotente: pode rodar de novo (atualiza a senha e as permissões).

\set ON_ERROR_STOP on

-- Cria o usuário se ainda não existir, e (re)define a senha e os limites.
SELECT format('CREATE ROLE %I LOGIN', :'app_user')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'app_user')
\gexec

SELECT format(
    'ALTER ROLE %I WITH LOGIN PASSWORD %L NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION',
    :'app_user', :'app_password'
)
\gexec

-- Ninguém além do dono cria objetos no schema public.
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON DATABASE :"db" FROM PUBLIC;

GRANT CONNECT, TEMPORARY ON DATABASE :"db" TO :"app_user";
GRANT USAGE ON SCHEMA public TO :"app_user";

-- Tabelas e sequências que já existem.
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO :"app_user";
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO :"app_user";

-- Tabelas e sequências que o dono criar depois (migrações do Alembic).
ALTER DEFAULT PRIVILEGES FOR ROLE :"owner" IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO :"app_user";
ALTER DEFAULT PRIVILEGES FOR ROLE :"owner" IN SCHEMA public
    GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO :"app_user";

-- A tabela de controle do Alembic é só do dono.
SELECT format('REVOKE ALL ON TABLE public.alembic_version FROM %I', :'app_user')
WHERE to_regclass('public.alembic_version') IS NOT NULL
\gexec
