from datetime import UTC, datetime

from job_search_rss.domain.collection_condition import CollectionCondition
from job_search_rss.domain.condition_values import Region
from job_search_rss.domain.history import CollectionRun, JobChange, JobChangeType
from job_search_rss.domain.job import Job
from job_search_rss.domain.subscription_condition import SubscriptionCondition
from job_search_rss.ports.repository import Repository
from tests.fakes.repository import FakeRepository


def test_fake_repository_stores_domain_objects() -> None:
    repository: Repository = FakeRepository()
    occurred_at = datetime(2026, 5, 21, 12, 0, tzinfo=UTC)
    job = Job(
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
    change = JobChange(
        job_id=job.job_id,
        collection_condition_key="collection:atgp:region:tokyo",
        change_type=JobChangeType.NEW,
        content_hash=job.content_hash,
        occurred_at=occurred_at,
    )
    subscription_condition = SubscriptionCondition(region=Region(prefecture="Tokyo"))
    collection_condition = CollectionCondition.from_subscription_condition(
        site_id="atgp",
        subscription_condition=subscription_condition,
    )
    run = CollectionRun.succeeded(
        collection_condition_key=collection_condition.normalized_key,
        started_at=occurred_at,
        finished_at=occurred_at,
        collected_job_count=1,
    )

    repository.save_job(job)
    repository.save_job_change(change)
    repository.save_subscription_condition(subscription_condition)
    repository.save_collection_condition(collection_condition)
    repository.save_collection_run(run)
    repository.save_condition_snapshot(
        collection_condition_key=collection_condition.normalized_key,
        job_ids=[job.job_id],
    )

    assert repository.list_jobs() == [job]
    assert repository.list_job_changes() == [change]
    assert repository.list_subscription_conditions() == [subscription_condition]
    assert repository.list_collection_conditions() == [collection_condition]
    assert repository.list_collection_runs() == [run]
    assert repository.list_job_ids_for_condition(collection_condition.normalized_key) == [
        job.job_id
    ]
