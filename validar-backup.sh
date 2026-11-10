#!/bin/sh
set -eu
cd "$(dirname "$0")"
backup_path="${1:-backups/ultimo.dump}"
if [ ! -s "$backup_path" ]; then echo 'Backup não encontrado ou vazio.'; exit 1; fi
docker compose -f compose.prod.yaml exec -T db sh -c '
set -eu
testdb="portal_verificacao_$(date +%s)_$$"
createdb -U "$POSTGRES_USER" "$testdb"
trap '\''dropdb -U "$POSTGRES_USER" --if-exists "$testdb"'\'' 0
pg_restore -U "$POSTGRES_USER" -d "$testdb" --no-owner --no-acl --exit-on-error
psql -U "$POSTGRES_USER" -d "$testdb" -v ON_ERROR_STOP=1 -c "SELECT count(*) AS usuarios_restaurados FROM core_user;"
echo "Backup restaurado em banco temporário e validado. O banco original não foi alterado."
' < "$backup_path"
