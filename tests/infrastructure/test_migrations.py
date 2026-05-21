from pathlib import Path
from uuid import uuid4

from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine, inspect


def test_alembic_upgrade_creates_required_tables() -> None:
    db_path = Path(".pytest_cache") / f"job_search_rss_{uuid4().hex}.sqlite3"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{db_path.as_posix()}")
    engine: Engine | None = None

    try:
        command.upgrade(config, "head")

        engine = create_engine(f"sqlite:///{db_path.as_posix()}")
        inspector = inspect(engine)

        assert set(inspector.get_table_names()) >= {
            "alembic_version",
            "jobs",
            "job_changes",
            "subscription_conditions",
            "collection_conditions",
            "collection_runs",
            "condition_snapshots",
        }
    finally:
        if engine is not None:
            engine.dispose()
        db_path.unlink(missing_ok=True)
