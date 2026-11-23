#!/usr/bin/env bash
# Backup do banco do Simple Mark (pg_dump em formato custom).
#
# Uso, na raiz do projeto, com o container "db" no ar:
#   bash scripts/banco/backup.sh
#
# Se BACKUP_SENHA estiver definida (no .env ou no ambiente), o arquivo sai
# criptografado com GPG (AES-256): backups/simplemark-AAAA-MM-DD_HHMMSS.dump.gpg
# Sem ela, sai sem criptografia e o script avisa.
#
# Os backups ficam em backups/ (ignorada pelo Git e pelo Docker). Copie-os para
# FORA desta máquina; um backup no mesmo disco não protege contra perda do disco.
set -euo pipefail
cd "$(dirname "$0")/../.."

set -a; source .env; set +a
: "${POSTGRES_USER:?}" "${POSTGRES_DB:?}"

mkdir -p backups
chmod 700 backups
destino="backups/simplemark-$(date +%F_%H%M%S).dump"

if [[ -n "${BACKUP_SENHA:-}" ]]; then
    docker compose exec -T db pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc \
        | gpg --batch --yes --symmetric --cipher-algo AES256 \
              --passphrase-fd 3 -o "$destino.gpg" 3<<<"$BACKUP_SENHA"
    destino="$destino.gpg"
else
    echo "AVISO: BACKUP_SENHA não definida; o backup sai SEM criptografia." >&2
    docker compose exec -T db pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc > "$destino"
fi

chmod 600 "$destino"
echo "Backup gravado em $destino ($(du -h "$destino" | cut -f1))"
