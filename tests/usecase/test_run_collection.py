from datetime import UTC, datetime
from typing import override

from tests.fakes.repository import FakeRepository
from tests.fakes.site_adapter import FakeSiteAdapter

from job_search_rss.domain.collection_condition import CollectionCondition
from job_search_rss.domain.condition_values import Region
from job_search_rss.domain.history import JobChangeType
from job_search_rss.domain.job import Job
from job_search_rss.domain.subscription_condition import SubscriptionCondition
from job_search_rss.usecase.manage_collection_condition import ManageCollectionCondition
from job_search_rss.usecase.register_subscription_condition import (
    RegisterSubscriptionCondition,
)
from job_search_rss.usecase.run_collection import RunCollection


def fixed_clock() -> datetime:
    return datetime(2026, 5, 21, 12, 0, tzinfo=UTC)


def test_run_collection_executes_registered_collection_conditions() -> None:
    repository = FakeRepository()
    site_adapter = FakeSiteAdapter()
    RegisterSubscriptionCondition(repository).execute(
        SubscriptionCondition(region=Region(prefecture="Tokyo"))
    )
    collection_condition = ManageCollectionCondition(repository).execute()[0]
    site_adapter.add_job_for_condition(collection_condition, create_job())

    result = RunCollection(repository, site_adapter, clock=fixed_clock).execute()

    assert [change.change_type for change in result.changes] == [JobChangeType.NEW]
    assert result.succeeded_condition_keys == [collection_condition.normalized_key]
    assert result.failed_condition_keys == []
    assert result.can_detect_deletions is True
    assert repository.list_job_ids_for_condition(collection_condition.normalized_key) == [
        "atgp-001"
    ]
    assert site_adapter.call_count == 1


def test_run_collection_reports_failed_conditions_without_allowing_deletion_detection() -> None:
    repository = FakeRepository()
    site_adapter = FakeSiteAdapter()
    RegisterSubscriptionCondition(repository).execute(
        SubscriptionCondition(region=Region(prefecture="Tokyo"))
    )
    collection_condition = ManageCollectionCondition(repository).execute()[0]
    site_adapter.raise_if_called = True

    result = RunCollection(repository, site_adapter, clock=fixed_clock).execute()

    assert result.changes == []
    assert result.succeeded_condition_keys == []
    assert result.failed_condition_keys == [collection_condition.normalized_key]
    assert result.can_detect_deletions is False
    assert repository.list_job_ids_for_condition(collection_condition.normalized_key) == []


def test_run_collection_retries_failed_condition_before_reporting_result() -> None:
    repository = FakeRepository()
    site_adapter = FailsOnceSiteAdapter()
    RegisterSubscriptionCondition(repository).execute(
        SubscriptionCondition(region=Region(prefecture="Tokyo"))
    )
    collection_condition = ManageCollectionCondition(repository).execute()[0]
    site_adapter.add_job_for_condition(collection_condition, create_job())

    result = RunCollection(
        repository,
        site_adapter,
        clock=fixed_clock,
        max_attempts_per_condition=2,
    ).execute()

    assert [change.change_type for change in result.changes] == [JobChangeType.NEW]
    assert result.succeeded_condition_keys == [collection_condition.normalized_key]
    assert result.failed_condition_keys == []
    assert site_adapter.call_count == 2


def test_run_collection_throttles_between_conditions_without_parallel_execution() -> None:
    repository = FakeRepository()
    site_adapter = FakeSiteAdapter()
    sleeps: list[float] = []
    RegisterSubscriptionCondition(repository).execute(
        SubscriptionCondition(region=Region(prefecture="Tokyo"))
    )
    RegisterSubscriptionCondition(repository).execute(
        SubscriptionCondition(region=Region(prefecture="Osaka"))
    )
    collection_conditions = ManageCollectionCondition(repository).execute()
    for index, collection_condition in enumerate(collection_conditions, start=1):
        site_adapter.add_job_for_condition(
            collection_condition,
            create_job(job_id=f"atgp-00{index}", content_hash=f"hash-00{index}"),
        )

    result = RunCollection(
        repository,
        site_adapter,
        clock=fixed_clock,
        condition_delay_seconds=0.5,
        sleeper=sleeps.append,
    ).execute()

    assert len(result.changes) == 2
    assert sleeps == [0.5]
    assert site_adapter.call_count == 2


class FailsOnceSiteAdapter(FakeSiteAdapter):
    def __init__(self) -> None:
        super().__init__()
        self._failed = False

    @override
    def fetch_jobs_for_condition(self, condition: CollectionCondition) -> list[Job]:
        if not self._failed:
            self._failed = True
            self.call_count += 1
            raise RuntimeError("temporary failure")
        return super().fetch_jobs_for_condition(condition)


def create_job(
    *,
    job_id: str = "atgp-001",
    content_hash: str = "hash-001",
) -> Job:
    return Job(
        job_id=job_id,
        site_id="atgp",
        title="Backend Engineer",
        company_name="Example Inc.",
        detail_url="https://example.test/jobs/atgp-001",
        work_location="Tokyo",
        occupation="Web Engineer",
        salary="5,000,000 JPY",
        content_hash=content_hash,
    )
