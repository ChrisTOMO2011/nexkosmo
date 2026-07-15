#!/usr/bin/env bash
set -euo pipefail
export PGPASSWORD=change_owner
STAMP="$(date +%s)"
BACKUP="/tmp/nexkosmo-${STAMP}.dump"
RESTORE_DB="nexkosmo_restore_${STAMP}"

pg_dump -h postgres -U nexkosmo_owner -d nexkosmo -Fc -f "$BACKUP"
createdb -h postgres -U nexkosmo_owner "$RESTORE_DB"
pg_restore -h postgres -U nexkosmo_owner -d "$RESTORE_DB" "$BACKUP"
psql -h postgres -U nexkosmo_owner -d "$RESTORE_DB" -v ON_ERROR_STOP=1 \
  -c "SELECT count(*) FROM alembic_version" \
  -c "SELECT count(*) FROM identities" \
  -c "SELECT count(*) FROM assertions" \
  -c "SELECT count(*) FROM audit_log"
dropdb -h postgres -U nexkosmo_owner "$RESTORE_DB"
sha256sum "$BACKUP"
