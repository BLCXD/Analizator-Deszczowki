#!/usr/bin/env bash
set -Eeuo pipefail

compose=${COMPOSE_COMMAND:-docker-compose}
backup_dir=${BACKUP_DIR:-./backups}
mkdir -p "$backup_dir"
chmod 700 "$backup_dir"
backup_file="$backup_dir/ad-postgres-$(date -u +%Y%m%dT%H%M%SZ).dump"
trap 'rm -f "$backup_file"' ERR

$compose exec -T postgres sh -c \
  'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom --no-owner --no-acl' \
  > "$backup_file"
test -s "$backup_file"
$compose exec -T postgres pg_restore --list < "$backup_file" >/dev/null
chmod 600 "$backup_file"
trap - ERR
printf 'Backup verified: %s\n' "$backup_file"
