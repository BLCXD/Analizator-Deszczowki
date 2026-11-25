#!/usr/bin/env bash
set -Eeuo pipefail

if [[ $# -ne 1 || ! -s "$1" ]]; then
  echo "Usage: CONFIRM_RESTORE=YES $0 path/to/backup.dump" >&2
  exit 2
fi
if [[ ${CONFIRM_RESTORE:-} != YES ]]; then
  echo "Restore replaces objects in the configured database. Set CONFIRM_RESTORE=YES to continue." >&2
  exit 2
fi

compose=${COMPOSE_COMMAND:-docker-compose}
restore_database=${RESTORE_DATABASE:-}
$compose exec -T -e RESTORE_DATABASE="$restore_database" postgres sh -c \
  'pg_restore --clean --if-exists --exit-on-error --no-owner --no-acl -U "$POSTGRES_USER" -d "${RESTORE_DATABASE:-$POSTGRES_DB}"' \
  < "$1"
echo "Restore completed. Confirm application health and expected data before returning to service."
