#!/usr/bin/env bash
set -euo pipefail
: "${BACKUP_DATABASE_PASSWORD:?BACKUP_DATABASE_PASSWORD must be injected}"
: "${EXPECTED_MIGRATION_HEAD:?EXPECTED_MIGRATION_HEAD must be injected}"
export PGPASSWORD="$BACKUP_DATABASE_PASSWORD"
DB_HOST="${BACKUP_DATABASE_HOST:-postgres}"
DB_PORT="${BACKUP_DATABASE_PORT:-5432}"
DB_USER="${BACKUP_DATABASE_USER:-nexkosmo_owner}"
DB_NAME="${BACKUP_DATABASE_NAME:-nexkosmo}"
STAMP="$(date +%s)"
BACKUP="/tmp/nexkosmo-${STAMP}.dump"
RESTORE_DB="nexkosmo_restore_${STAMP}"

pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -Fc -f "$BACKUP"
createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$RESTORE_DB"
pg_restore -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$RESTORE_DB" "$BACKUP"
RESTORED_HEAD="$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$RESTORE_DB" -Atc \
  "SELECT version_num FROM alembic_version")"
test "$RESTORED_HEAD" = "$EXPECTED_MIGRATION_HEAD"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$RESTORE_DB" -v ON_ERROR_STOP=1 \
  -c "SELECT count(*) FROM identities" \
  -c "SELECT count(*) FROM assertions" \
  -c "SELECT count(*) FROM projects" \
  -c "SELECT count(*) FROM characters" \
  -c "SELECT count(*) FROM outbox_events" \
  -c "SELECT count(*) FROM audit_delivery_queue" \
  -c "SELECT count(*) FROM audit_log"
dropdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$RESTORE_DB"
sha256sum "$BACKUP"
