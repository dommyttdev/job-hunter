from datetime import UTC, datetime

from tests.fakes.repository import FakeRepository

from job_search_rss.domain.condition_values import Occupation, Region
from job_search_rss.domain.history import JobChange, JobChangeType
from job_search_rss.domain.subscription_condition import SubscriptionCondition
from job_search_rss.usecase.query_job_changes_for_rss import (
    QueryJobChangesForRss,
    RssChangeQuery,
)


def test_query_job_changes_for_rss_filters_by_subscription_condition() -> None:
    repository = FakeRepository()
    tokyo_change = create_change(
        job_id="atgp-001",
        collection_condition_key="collection:atgp:region:tokyo",
        change_type=JobChangeType.NEW,
    )
    osaka_change = create_change(
        job_id="atgp-002",
        collection_condition_key="collection:atgp:region:osaka",
        change_type=JobChangeType.NEW,
    )
    repository.save_job_change(tokyo_change)
    repository.save_job_change(osaka_change)

    changes = QueryJobChangesForRss(repository).execute(
        RssChangeQuery(
            subscription_condition=SubscriptionCondition(
                region=Region(prefecture="Tokyo")
            )
        )
    )

    assert changes == [tokyo_change]


def test_query_job_changes_for_rss_filters_by_change_type() -> None:
    repository = FakeRepository()
    new_change = create_change(
        job_id="atgp-001",
        collection_condition_key=(
            "collection:atgp:region:tokyo|occupation:it-web:backend-engineer"
        ),
        change_type=JobChangeType.NEW,
    )
    updated_change = create_change(
        job_id="atgp-001",
        collection_condition_key=(
            "collection:atgp:region:tokyo|occupation:it-web:backend-engineer"
        ),
        change_type=JobChangeType.UPDATED,
    )
    repository.save_job_change(new_change)
    repository.save_job_change(updated_change)

    changes = QueryJobChangesForRss(repository).execute(
        RssChangeQuery(
            subscription_condition=SubscriptionCondition(
                region=Region(prefecture="Tokyo"),
                occupation=Occupation(category="IT Web", detail="Backend Engineer"),
            ),
            change_types={JobChangeType.UPDATED},
        )
    )

    assert changes == [updated_change]


def create_change(
    *,
    job_id: str,
    collection_condition_key: str,
    change_type: JobChangeType,
) -> JobChange:
    return JobChange(
        job_id=job_id,
        collection_condition_key=collection_condition_key,
        change_type=change_type,
        content_hash="hash-001",
        occurred_at=datetime(2026, 5, 21, 12, 0, tzinfo=UTC),
    )
