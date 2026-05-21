import logging

from job_search_rss.infrastructure.logging import log_event


def test_log_event_records_structured_context(caplog) -> None:
    with caplog.at_level(logging.INFO):
        log_event(
            "collection_started",
            condition_id="condition-1",
            site="atgp",
        )

    assert caplog.messages == ["collection_started"]
    assert caplog.records[0].event == "collection_started"
    assert caplog.records[0].condition_id == "condition-1"
    assert caplog.records[0].site == "atgp"


def test_log_event_can_record_failure(caplog) -> None:
    with caplog.at_level(logging.ERROR):
        log_event(
            "collection_failed",
            level=logging.ERROR,
            condition_id="condition-1",
            reason="parse_error",
        )

    assert caplog.messages == ["collection_failed"]
    assert caplog.records[0].levelno == logging.ERROR
    assert caplog.records[0].reason == "parse_error"
