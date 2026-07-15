# Repository Structure

- `app/domain`: dependency-free kernel concepts and rules.
- `app/application`: ports and orchestration.
- `app/infrastructure`: OIDC/JWKS adapter, database and UoW.
- `app/interfaces`: HTTP/operations.
- `migrations`: explicit forward-only Alembic migrations.
- `tests`: pure-domain and blocking PostgreSQL tests.
- `scripts`: role bootstrap and backup/restore rehearsal.
- `docs`: architecture and evidence.
