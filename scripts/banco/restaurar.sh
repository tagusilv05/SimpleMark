#!/usr/bin/env bash
# Restaura um backup feito por scripts/banco/backup.sh.
#
# Uso, na raiz do projeto, com o container "db" no ar:
#   bash scripts/banco/restaurar.sh backups/simplemark-AAAA-MM-DD_HHMMSS.dump[.gpg]
#
# ATENÇÃO: substitui (--clean) as tabelas atuais pelas do backup.
# Teste a restauração de vez em quando: backup que nunca foi restaurado não é backup.
set -euo pipefail
cd "$(dirname "$0")/../.."

arquivo="${1:?Informe o arquivo do backup}"
[[ -f "$arquivo" ]] || { echo "Arquivo não encontrado: $arquivo" >&2; exit 1; }

set -a; source .env; set +a
: "${POSTGRES_USER:?}" "${POSTGRES_DB:?}"

read -r -p "Isto vai SUBSTITUIR os dados de '$POSTGRES_DB' pelos de $arquivo. Continuar? [s/N] " ok
[[ "$ok" == "s" || "$ok" == "S" ]] || { echo "Cancelado."; exit 1; }

if [[ "$arquivo" == *.gpg ]]; then
    : "${BACKUP_SENHA:?Defina BACKUP_SENHA para abrir o backup criptografado}"
    gpg --batch --quiet --decrypt --passphrase-fd 3 "$arquivo" 3<<<"$BACKUP_SENHA"
else
    cat "$arquivo"
fi | docker compose exec -T db pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
        --clean --if-exists --no-owner --role="$POSTGRES_USER"

# As tabelas recriadas precisam voltar a ser liberadas para o usuário da API.
docker compose exec -T db psql -q -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
    -v app_user="$APP_DB_USER" -v app_password="$APP_DB_PASSWORD" \
    -v owner="$POSTGRES_USER" -v db="$POSTGRES_DB" -f /banco/sql/usuario_app.sql

echo "Backup restaurado."
