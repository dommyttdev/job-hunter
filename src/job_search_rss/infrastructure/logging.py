import logging
from typing import Any

LOGGER_NAME = "job_search_rss"


def log_event(event: str, *, level: int = logging.INFO, **context: Any) -> None:
    logging.getLogger(LOGGER_NAME).log(
        level,
        event,
        extra={"event": event, **context},
    )
