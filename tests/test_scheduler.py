from collections.abc import Callable

from tests.fakes.repository import FakeRepository
from tests.fakes.site_adapter import FakeSiteAdapter

from job_search_rss.domain.condition_values import Region
from job_search_rss.domain.job import Job
from job_search_rss.domain.subscription_condition import SubscriptionCondition
from job_search_rss.scheduler import ScheduledJobResult, register_periodic_collection_job
from job_search_rss.usecase.register_subscription_condition import (
    RegisterSubscriptionCondition,
)


class FakeScheduler:
    def __init__(self) -> None:
        self.jobs: list[tuple[Callable[[], ScheduledJobResult], int, str]] = []

    def add_interval_job(
        self,
        func: Callable[[], ScheduledJobResult],
        *,
        minutes: int,
        job_id: str,
    ) -> None:
        self.jobs.append((func, minutes, job_id))


def test_register_periodic_collection_job_collects_registered_conditions() -> None:
    repository = FakeRepository()
    site_adapter = FakeSiteAdapter()
    scheduler = FakeScheduler()
    RegisterSubscriptionCondition(repository).execute(
        SubscriptionCondition(region=Region(prefecture="Tokyo"))
    )

    register_periodic_collection_job(
        scheduler,
        repository=repository,
        site_adapter=site_adapter,
        interval_minutes=15,
    )
    collection_condition = repository.list_collection_conditions()[0]
    site_adapter.add_job_for_condition(collection_condition, _create_job())

    job, minutes, job_id = scheduler.jobs[0]
    result = job()

    assert minutes == 15
    assert job_id == "job-search-rss-collection"
    assert result.change_count == 1
    assert result.failed_condition_count == 0


def _create_job() -> Job:
    return Job(
        job_id="atgp-001",
        site_id="atgp",
        title="Backend Engineer",
        company_name="Example Inc.",
        detail_url="https://example.test/jobs/atgp-001",
        work_location="Tokyo",
        occupation="Web Engineer",
        salary="5,000,000 JPY",
        content_hash="hash-001",
    )
