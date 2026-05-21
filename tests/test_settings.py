from pathlib import Path

from job_search_rss.infrastructure.settings import Settings, load_settings


def test_load_settings_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("JOB_SEARCH_RSS_DB_PATH", "var/test.sqlite3")
    monkeypatch.setenv("JOB_SEARCH_RSS_COLLECTION_INTERVAL_MINUTES", "15")
    monkeypatch.setenv("JOB_SEARCH_RSS_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("JOB_SEARCH_RSS_ALLOW_EXTERNAL_ACCESS", "true")

    settings = load_settings()

    assert settings == Settings(
        db_path=Path("var/test.sqlite3"),
        collection_interval_minutes=15,
        log_level="DEBUG",
        allow_external_access=True,
    )


def test_load_settings_uses_safe_defaults(monkeypatch) -> None:
    monkeypatch.delenv("JOB_SEARCH_RSS_DB_PATH", raising=False)
    monkeypatch.delenv("JOB_SEARCH_RSS_COLLECTION_INTERVAL_MINUTES", raising=False)
    monkeypatch.delenv("JOB_SEARCH_RSS_LOG_LEVEL", raising=False)
    monkeypatch.delenv("JOB_SEARCH_RSS_ALLOW_EXTERNAL_ACCESS", raising=False)

    settings = load_settings()

    assert settings.db_path == Path("data/job_search_rss.sqlite3")
    assert settings.collection_interval_minutes == 60
    assert settings.log_level == "INFO"
    assert settings.allow_external_access is False
