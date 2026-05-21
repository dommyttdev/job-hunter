import logging
from typing import cast

from pytest import LogCaptureFixture

from job_search_rss.infrastructure.logging import log_event


def test_log_event_records_structured_context(caplog: LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO):
        log_event(
            "collection_started",
            condition_id="condition-1",
            site="atgp",
        )

    assert caplog.messages == ["collection_started"]
    record = caplog.records[0]
    assert cast(str, record.__dict__["event"]) == "collection_started"
    assert cast(str, record.__dict__["condition_id"]) == "condition-1"
    assert cast(str, record.__dict__["site"]) == "atgp"


def test_log_event_can_record_failure(caplog: LogCaptureFixture) -> None:
    with caplog.at_level(logging.ERROR):
        log_event(
            "collection_failed",
            level=logging.ERROR,
            condition_id="condition-1",
            reason="parse_error",
        )

    assert caplog.messages == ["collection_failed"]
    record = caplog.records[0]
    assert record.levelno == logging.ERROR
    assert cast(str, record.__dict__["reason"]) == "parse_error"
