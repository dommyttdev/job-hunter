from pathlib import Path

from fastapi.testclient import TestClient

from job_search_rss.api import create_app_from_settings
from job_search_rss.infrastructure.database import SqlAlchemyRepository, create_sqlite_engine
from job_search_rss.infrastructure.settings import Settings


def test_create_app_from_settings_wires_sqlite_repository(tmp_path: Path) -> None:
    db_path = tmp_path / "job_search_rss.sqlite3"
    settings = Settings(
        db_path=db_path,
        collection_interval_minutes=60,
        log_level="INFO",
        allow_external_access=False,
    )

    client = TestClient(create_app_from_settings(settings))
    response = client.post(
        "/subscriptions",
        json={"region": {"prefecture": "Tokyo"}},
    )

    repository = SqlAlchemyRepository(create_sqlite_engine(f"sqlite:///{db_path.as_posix()}"))
    assert response.status_code == 201
    assert [
        condition.subscription_id for condition in repository.list_subscription_conditions()
    ] == ["subscription:region:tokyo"]
