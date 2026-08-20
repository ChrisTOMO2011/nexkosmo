#!/usr/bin/env bash
set -euo pipefail
: "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD must be set}"
: "${PGHOST:=postgres}"
: "${PGUSER:=nexkosmo_owner}"
: "${PGDATABASE:=nexkosmo}"
export PGPASSWORD="$POSTGRES_PASSWORD"
STAMP="$(date +%s)"
BACKUP="/tmp/nexkosmo-${STAMP}.dump"
RESTORE_DB="nexkosmo_restore_${STAMP}"
cleanup() {
  dropdb -h "$PGHOST" -U "$PGUSER" --if-exists "$RESTORE_DB" >/dev/null 2>&1 || true
}
trap cleanup EXIT

pg_dump -h "$PGHOST" -U "$PGUSER" -d "$PGDATABASE" -Fc -f "$BACKUP"
createdb -h "$PGHOST" -U "$PGUSER" "$RESTORE_DB"
pg_restore -h "$PGHOST" -U "$PGUSER" -d "$RESTORE_DB" "$BACKUP"
psql -h "$PGHOST" -U "$PGUSER" -d "$RESTORE_DB" -v ON_ERROR_STOP=1 \
  -c "SELECT version_num FROM alembic_version" \
  -c "SELECT count(*) AS projects FROM projects" \
  -c "SELECT count(*) AS productions FROM productions" \
  -c "SELECT count(*) AS characters FROM characters" \
  -c "SELECT count(*) AS environments FROM environments" \
  -c "SELECT count(*) AS environment_asset_selections FROM environment_asset_selections" \
  -c "SELECT count(*) AS orphan_environments FROM environments e LEFT JOIN projects p ON p.project_id = e.project_id AND p.workspace_id = e.workspace_id LEFT JOIN productions pr ON pr.production_id = e.production_id AND pr.project_id = e.project_id AND pr.workspace_id = e.workspace_id WHERE p.project_id IS NULL OR pr.production_id IS NULL" \
  -c "SELECT count(*) AS orphan_environment_selections FROM environment_asset_selections s LEFT JOIN environments e ON e.environment_id = s.environment_id AND e.workspace_id = s.workspace_id LEFT JOIN character_asset_manifests m ON m.asset_id = s.asset_id WHERE e.environment_id IS NULL OR m.asset_id IS NULL" \
  -c "SELECT count(*) AS memberships FROM project_members" \
  -c "SELECT count(*) AS idempotency_records FROM idempotency_records" \
  -c "SELECT count(*) AS outbox_events FROM outbox_events" \
  -c "SELECT count(*) AS audit_delivery_queue FROM audit_delivery_queue" \
  -c "SELECT count(*) AS broken_audit_links FROM audit_log current_entry LEFT JOIN audit_log previous_entry ON previous_entry.stream_key = current_entry.stream_key AND previous_entry.sequence = current_entry.sequence - 1 WHERE current_entry.sequence > 1 AND previous_entry.entry_hash IS DISTINCT FROM current_entry.previous_hash" \
  -c "SELECT count(*) AS orphan_characters FROM characters c LEFT JOIN projects p ON p.project_id = c.project_id AND p.workspace_id = c.workspace_id LEFT JOIN productions pr ON pr.production_id = c.production_id AND pr.project_id = c.project_id AND pr.workspace_id = c.workspace_id WHERE p.project_id IS NULL OR pr.production_id IS NULL" \
  -c "SELECT relname, relrowsecurity, relforcerowsecurity FROM pg_class WHERE relname IN ('projects','productions','characters','environments','environment_asset_selections','project_members','idempotency_records','outbox_events','audit_delivery_queue') ORDER BY relname"
sha256sum "$BACKUP"
