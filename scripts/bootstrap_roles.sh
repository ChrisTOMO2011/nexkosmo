#!/usr/bin/env bash
set -euo pipefail

: "${NEXKOSMO_APP_PASSWORD:?NEXKOSMO_APP_PASSWORD is required}"
: "${NEXKOSMO_AUDIT_PASSWORD:?NEXKOSMO_AUDIT_PASSWORD is required}"

psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
  --set=app_password="$NEXKOSMO_APP_PASSWORD" \
  --set=audit_password="$NEXKOSMO_AUDIT_PASSWORD" <<'SQL'
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'nexkosmo_app') THEN
    CREATE ROLE nexkosmo_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'nexkosmo_audit') THEN
    CREATE ROLE nexkosmo_audit LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
  END IF;
END $$;
ALTER ROLE nexkosmo_app PASSWORD :'app_password';
ALTER ROLE nexkosmo_audit PASSWORD :'audit_password';
GRANT CONNECT ON DATABASE nexkosmo TO nexkosmo_app, nexkosmo_audit;
SQL
