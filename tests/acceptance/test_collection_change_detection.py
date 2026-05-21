from datetime import UTC, datetime

from job_search_rss.domain.condition_values import Region
from job_search_rss.domain.history import JobChangeType
from job_search_rss.domain.job import Job
from job_search_rss.domain.subscription_condition import SubscriptionCondition
from job_search_rss.usecase.detect_job_changes import DetectJobChanges
from job_search_rss.usecase.manage_collection_condition import ManageCollectionCondition
from job_search_rss.usecase.register_subscription_condition import (
    RegisterSubscriptionCondition,
)
from tests.fakes.repository import FakeRepository
from tests.fakes.site_adapter import FakeSiteAdapter


def fixed_clock() -> datetime:
    return datetime(2026, 5, 21, 12, 0, tzinfo=UTC)


def test_collection_flow_records_new_updated_and_deleted_changes() -> None:
    repository = FakeRepository()
    site_adapter = FakeSiteAdapter()
    subscription = RegisterSubscriptionCondition(repository).execute(
        SubscriptionCondition(region=Region(prefecture="Tokyo"))
    )
    condition = ManageCollectionCondition(repository).execute()[0]
    first_job = create_job(job_id="atgp-001", content_hash="hash-001")
    site_adapter.add_job_for_condition(condition, first_job)

    first_changes = DetectJobChanges(
        repository,
        site_adapter,
        clock=fixed_clock,
    ).execute(condition)

    updated_job = create_job(job_id="atgp-001", content_hash="hash-002")
    new_job = create_job(job_id="atgp-002", content_hash="hash-003")
    site_adapter.replace_jobs_for_condition(condition, [updated_job, new_job])
    second_changes = DetectJobChanges(
        repository,
        site_adapter,
        clock=fixed_clock,
    ).execute(condition)

    site_adapter.replace_jobs_for_condition(condition, [new_job])
    third_changes = DetectJobChanges(
        repository,
        site_adapter,
        clock=fixed_clock,
    ).execute(condition)

    assert subscription.id == "subscription:region:tokyo"
    assert [change.change_type for change in first_changes] == [JobChangeType.NEW]
    assert [change.change_type for change in second_changes] == [
        JobChangeType.UPDATED,
        JobChangeType.NEW,
    ]
    assert [change.change_type for change in third_changes] == [JobChangeType.DELETED]
    assert [change.change_type for change in repository.list_job_changes()] == [
        JobChangeType.NEW,
        JobChangeType.UPDATED,
        JobChangeType.NEW,
        JobChangeType.DELETED,
    ]


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
