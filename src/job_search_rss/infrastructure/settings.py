import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    db_path: Path
    collection_interval_minutes: int
    log_level: str
    allow_external_access: bool


def load_settings() -> Settings:
    return Settings(
        db_path=Path(os.getenv("JOB_SEARCH_RSS_DB_PATH", "data/job_search_rss.sqlite3")),
        collection_interval_minutes=int(
            os.getenv("JOB_SEARCH_RSS_COLLECTION_INTERVAL_MINUTES", "60")
        ),
        log_level=os.getenv("JOB_SEARCH_RSS_LOG_LEVEL", "INFO"),
        allow_external_access=_get_bool("JOB_SEARCH_RSS_ALLOW_EXTERNAL_ACCESS", default=False),
    )


def _get_bool(name: str, *, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}
