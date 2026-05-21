from datetime import UTC, datetime

from job_search_rss.domain.history import (
    CollectionRun,
    CollectionRunStatus,
    JobChange,
    JobChangeType,
)


def test_job_change_represents_new_update_and_deleted_states() -> None:
    occurred_at = datetime(2026, 5, 21, 12, 0, tzinfo=UTC)

    new_change = JobChange(
        job_id="atgp-001",
        collection_condition_key="collection:atgp:region:tokyo",
        change_type=JobChangeType.NEW,
        content_hash="hash-001",
        occurred_at=occurred_at,
    )
    updated_change = JobChange(
        job_id="atgp-001",
        collection_condition_key="collection:atgp:region:tokyo",
        change_type=JobChangeType.UPDATED,
        content_hash="hash-002",
        occurred_at=occurred_at,
    )
    deleted_change = JobChange(
        job_id="atgp-001",
        collection_condition_key="collection:atgp:region:tokyo",
        change_type=JobChangeType.DELETED,
        content_hash="hash-002",
        occurred_at=occurred_at,
    )

    assert new_change.change_type is JobChangeType.NEW
    assert updated_change.change_type is JobChangeType.UPDATED
    assert deleted_change.change_type is JobChangeType.DELETED


def test_collection_run_success_records_condition_and_time_range() -> None:
    started_at = datetime(2026, 5, 21, 12, 0, tzinfo=UTC)
    finished_at = datetime(2026, 5, 21, 12, 1, tzinfo=UTC)

    run = CollectionRun.succeeded(
        collection_condition_key="collection:atgp:region:tokyo",
        started_at=started_at,
        finished_at=finished_at,
        collected_job_count=3,
    )

    assert run.status is CollectionRunStatus.SUCCEEDED
    assert run.collection_condition_key == "collection:atgp:region:tokyo"
    assert run.started_at == started_at
    assert run.finished_at == finished_at
    assert run.collected_job_count == 3
    assert run.error_message is None


def test_collection_run_failure_records_reason_without_success_count() -> None:
    started_at = datetime(2026, 5, 21, 12, 0, tzinfo=UTC)
    finished_at = datetime(2026, 5, 21, 12, 1, tzinfo=UTC)

    run = CollectionRun.failed(
        collection_condition_key="collection:atgp:region:tokyo",
        started_at=started_at,
        finished_at=finished_at,
        error_message="parse error",
    )

    assert run.status is CollectionRunStatus.FAILED
    assert run.collected_job_count == 0
    assert run.error_message == "parse error"
