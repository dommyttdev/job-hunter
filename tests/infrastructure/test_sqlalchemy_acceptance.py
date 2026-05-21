from datetime import UTC, datetime
from xml.etree import ElementTree

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from tests.fakes.site_adapter import FakeSiteAdapter

from job_search_rss.domain.condition_values import Region
from job_search_rss.domain.history import JobChangeType
from job_search_rss.domain.job import Job
from job_search_rss.domain.subscription_condition import SubscriptionCondition
from job_search_rss.infrastructure.database import SqlAlchemyRepository, create_schema
from job_search_rss.rss.renderer import XmlRssRenderer
from job_search_rss.usecase.detect_job_changes import DetectJobChanges
from job_search_rss.usecase.generate_rss_feed import GenerateRssFeed
from job_search_rss.usecase.manage_collection_condition import ManageCollectionCondition
from job_search_rss.usecase.query_job_changes_for_rss import RssChangeQuery
from job_search_rss.usecase.register_subscription_condition import (
    RegisterSubscriptionCondition,
)


def fixed_clock() -> datetime:
    return datetime(2026, 5, 21, 12, 0, tzinfo=UTC)


def test_sqlalchemy_repository_supports_subscription_to_rss_flow() -> None:
    repository = create_repository()
    site_adapter = FakeSiteAdapter()
    subscription_condition = SubscriptionCondition(region=Region(prefecture="Tokyo"))
    RegisterSubscriptionCondition(repository).execute(subscription_condition)
    collection_condition = ManageCollectionCondition(repository).execute()[0]
    site_adapter.add_job_for_condition(
        collection_condition,
        create_job(job_id="atgp-001", content_hash="hash-001"),
    )

    changes = DetectJobChanges(repository, site_adapter, clock=fixed_clock).execute(
        collection_condition
    )

    site_adapter.raise_if_called = True
    xml = GenerateRssFeed(
        repository,
        XmlRssRenderer(
            title="Job Search Changes",
            link="https://example.test/rss",
            description="Latest job changes",
        ),
    ).execute(RssChangeQuery(subscription_condition=subscription_condition))

    rss_item = ElementTree.fromstring(xml).find("channel/item")
    assert [change.change_type for change in changes] == [JobChangeType.NEW]
    assert rss_item is not None
    assert rss_item.findtext("title") == "[new] Backend Engineer - Example Inc."
    assert site_adapter.call_count == 1


def create_repository() -> SqlAlchemyRepository:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    create_schema(engine)
    return SqlAlchemyRepository(engine)


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
