#!/usr/bin/env bash
# Aplica as correções de segurança num volume do PostgreSQL que JÁ EXISTE.
# (Num volume novo, o compose já faz tudo isso sozinho.)
#
# O que faz, nesta ordem:
#   1. sobe só o container "db";
#   2. faz um backup (scripts/banco/backup.sh) antes de mudar qualquer coisa;
#   3. troca a senha do dono do banco para o POSTGRES_PASSWORD atual do .env
#      (a variável só vale na criação do volume; depois precisa do ALTER ROLE);
#   4. cria/atualiza o usuário da API (APP_DB_USER) só com permissão de dados.
#
# Depois, rode "docker compose up --build": o serviço "migracoes" adota o banco
# no Alembic (versão 0001) e o backend sobe com o usuário restrito.
#
# Uso, na raiz do projeto:  bash scripts/banco/atualizar_banco_existente.sh
set -euo pipefail
cd "$(dirname "$0")/../.."

set -a; source .env; set +a
: "${POSTGRES_USER:?}" "${POSTGRES_PASSWORD:?}" "${POSTGRES_DB:?}"
: "${APP_DB_USER:?Defina APP_DB_USER no .env}" "${APP_DB_PASSWORD:?Defina APP_DB_PASSWORD no .env}"

echo "1/4 Subindo o banco..."
docker compose up -d db
for _ in $(seq 1 60); do
    docker compose exec -T db pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" >/dev/null 2>&1 && break
    sleep 1
done

echo "2/4 Backup antes das mudanças..."
bash scripts/banco/backup.sh

echo "3/4 Trocando a senha do dono do banco ($POSTGRES_USER)..."
# Conexão local pelo socket do container: não precisa da senha antiga.
docker compose exec -T db psql -q -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
    -v owner="$POSTGRES_USER" -v senha="$POSTGRES_PASSWORD" <<'SQL'
SELECT format('ALTER ROLE %I WITH PASSWORD %L', :'owner', :'senha') \gexec
SQL

echo "4/4 Criando o usuário restrito da API ($APP_DB_USER)..."
docker compose exec -T db psql -q -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
    -v app_user="$APP_DB_USER" -v app_password="$APP_DB_PASSWORD" \
    -v owner="$POSTGRES_USER" -v db="$POSTGRES_DB" -f /banco/sql/usuario_app.sql

echo "Pronto. Agora rode: docker compose up --build"
