from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text

from app.infrastructure.config import settings


def main() -> None:
    configuration = settings()
    source_head = ScriptDirectory.from_config(Config("alembic.ini")).get_current_head()
    engine = create_engine(configuration.migration_database_url)
    try:
        with engine.connect() as connection:
            database_head = connection.scalar(text("SELECT version_num FROM alembic_version"))
    finally:
        engine.dispose()

    expected = configuration.migration_head
    if source_head != expected or database_head != expected:
        raise SystemExit(
            "Migration head mismatch: "
            f"source={source_head!r}, database={database_head!r}, configured={expected!r}."
        )
    print(f"Migration heads agree: {expected}")


if __name__ == "__main__":
    main()
