#!/bin/bash
# Roda uma única vez, quando o volume do PostgreSQL é criado (docker-entrypoint-initdb.d).
# Cria o usuário da API (APP_DB_USER) só com permissão de ler e gravar dados.
# Para um volume que já existe, use scripts/banco/atualizar_banco_existente.sh.
set -euo pipefail

: "${APP_DB_USER:?Defina APP_DB_USER no .env}"
: "${APP_DB_PASSWORD:?Defina APP_DB_PASSWORD no .env}"

psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
    -v app_user="$APP_DB_USER" \
    -v app_password="$APP_DB_PASSWORD" \
    -v owner="$POSTGRES_USER" \
    -v db="$POSTGRES_DB" \
    -f /banco/sql/usuario_app.sql
