from datetime import UTC, datetime

from tests.fakes.repository import FakeRepository
from tests.fakes.site_adapter import FakeSiteAdapter

from job_search_rss.domain.collection_condition import CollectionCondition
from job_search_rss.domain.history import (
    CollectionRunStatus,
    JobChangeType,
)
from job_search_rss.domain.job import Job
from job_search_rss.usecase.detect_job_changes import DetectJobChanges


def fixed_clock() -> datetime:
    return datetime(2026, 5, 21, 12, 0, tzinfo=UTC)


def test_detect_job_changes_records_new_job_change() -> None:
    repository = FakeRepository()
    site_adapter = FakeSiteAdapter()
    condition = CollectionCondition(site_id="atgp", condition_key="region:tokyo")
    job = create_job(job_id="atgp-001", content_hash="hash-001")
    site_adapter.add_job_for_condition(condition, job)

    changes = DetectJobChanges(
        repository,
        site_adapter,
        clock=fixed_clock,
    ).execute(condition)

    assert len(changes) == 1
    assert changes[0].job_id == "atgp-001"
    assert changes[0].collection_condition_key == condition.normalized_key
    assert changes[0].change_type is JobChangeType.NEW
    assert changes[0].content_hash == "hash-001"
    assert changes[0].occurred_at == fixed_clock()
    assert repository.list_jobs() == [job]
    assert repository.list_job_changes() == changes
    assert repository.list_collection_runs()[0].status is CollectionRunStatus.SUCCEEDED
    assert repository.list_collection_runs()[0].collected_job_count == 1


def test_detect_job_changes_records_updated_job_change_when_content_hash_changes() -> None:
    repository = FakeRepository()
    site_adapter = FakeSiteAdapter()
    condition = CollectionCondition(site_id="atgp", condition_key="region:tokyo")
    existing_job = create_job(job_id="atgp-001", content_hash="hash-001")
    updated_job = create_job(job_id="atgp-001", content_hash="hash-002")
    repository.save_job(existing_job)
    site_adapter.add_job_for_condition(condition, updated_job)

    changes = DetectJobChanges(
        repository,
        site_adapter,
        clock=fixed_clock,
    ).execute(condition)

    assert len(changes) == 1
    assert changes[0].job_id == "atgp-001"
    assert changes[0].change_type is JobChangeType.UPDATED
    assert changes[0].content_hash == "hash-002"
    assert repository.list_jobs() == [existing_job, updated_job]
    assert repository.list_job_changes() == changes


def test_detect_job_changes_does_not_record_change_when_content_hash_is_same() -> None:
    repository = FakeRepository()
    site_adapter = FakeSiteAdapter()
    condition = CollectionCondition(site_id="atgp", condition_key="region:tokyo")
    existing_job = create_job(job_id="atgp-001", content_hash="hash-001")
    same_job = create_job(job_id="atgp-001", content_hash="hash-001")
    repository.save_job(existing_job)
    site_adapter.add_job_for_condition(condition, same_job)

    changes = DetectJobChanges(
        repository,
        site_adapter,
        clock=fixed_clock,
    ).execute(condition)

    assert changes == []
    assert repository.list_jobs() == [existing_job]
    assert repository.list_job_changes() == []


def test_detect_job_changes_does_not_duplicate_update_change_on_rerun() -> None:
    repository = FakeRepository()
    site_adapter = FakeSiteAdapter()
    condition = CollectionCondition(site_id="atgp", condition_key="region:tokyo")
    existing_job = create_job(job_id="atgp-001", content_hash="hash-001")
    updated_job = create_job(job_id="atgp-001", content_hash="hash-002")
    repository.save_job(existing_job)
    site_adapter.add_job_for_condition(condition, updated_job)
    detect_changes = DetectJobChanges(repository, site_adapter, clock=fixed_clock)

    first_changes = detect_changes.execute(condition)
    second_changes = detect_changes.execute(condition)

    assert len(first_changes) == 1
    assert second_changes == []
    assert len(repository.list_job_changes()) == 1


def test_detect_job_changes_records_deleted_job_when_previous_snapshot_disappears() -> None:
    repository = FakeRepository()
    site_adapter = FakeSiteAdapter()
    condition = CollectionCondition(site_id="atgp", condition_key="region:tokyo")
    existing_job = create_job(job_id="atgp-001", content_hash="hash-001")
    repository.save_job(existing_job)
    repository.save_condition_snapshot(
        collection_condition_key=condition.normalized_key,
        job_ids=["atgp-001"],
    )

    changes = DetectJobChanges(
        repository,
        site_adapter,
        clock=fixed_clock,
    ).execute(condition)

    assert len(changes) == 1
    assert changes[0].job_id == "atgp-001"
    assert changes[0].change_type is JobChangeType.DELETED
    assert changes[0].content_hash == "hash-001"
    assert repository.list_job_changes() == changes
    assert repository.list_job_ids_for_condition(condition.normalized_key) == []


def test_detect_job_changes_records_failure_without_deleting_previous_snapshot() -> None:
    repository = FakeRepository()
    site_adapter = FakeSiteAdapter()
    condition = CollectionCondition(site_id="atgp", condition_key="region:tokyo")
    existing_job = create_job(job_id="atgp-001", content_hash="hash-001")
    repository.save_job(existing_job)
    repository.save_condition_snapshot(
        collection_condition_key=condition.normalized_key,
        job_ids=["atgp-001"],
    )
    site_adapter.raise_if_called = True

    changes = DetectJobChanges(
        repository,
        site_adapter,
        clock=fixed_clock,
    ).execute(condition)

    assert changes == []
    assert repository.list_job_changes() == []
    assert repository.list_job_ids_for_condition(condition.normalized_key) == [
        "atgp-001"
    ]
    assert repository.list_collection_runs()[0].status is CollectionRunStatus.FAILED
    assert repository.list_collection_runs()[0].error_message == "SiteAdapter must not be called"


def create_job(
    *,
    job_id: str,
    content_hash: str,
) -> Job:
    return Job(
        job_id=job_id,
        site_id="atgp",
        title="Backend Engineer",
        company_name="Example Inc.",
        detail_url=f"https://example.test/jobs/{job_id}",
        work_location="Tokyo",
        occupation="Web Engineer",
        salary="5,000,000 JPY",
        content_hash=content_hash,
    )
