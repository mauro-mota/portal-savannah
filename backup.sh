#!/bin/sh
set -eu
cd "$(dirname "$0")"
umask 077
mkdir -p backups
backup_file="backups/portal-$(date +%Y%m%d-%H%M%S).dump"
docker compose -f compose.prod.yaml exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$backup_file.tmp"
mv "$backup_file.tmp" "$backup_file"
cp "$backup_file" backups/ultimo.dump
chmod 600 backups/ultimo.dump
echo "Backup criado: $backup_file"
echo 'Copie para fora da VPS. Esta versão mantém todas as cópias; acompanhe o espaço.'
