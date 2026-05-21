from datetime import UTC, datetime
from xml.etree import ElementTree

from job_search_rss.domain.condition_values import Region
from job_search_rss.domain.job import Job
from job_search_rss.domain.subscription_condition import SubscriptionCondition
from job_search_rss.rss.renderer import XmlRssRenderer
from job_search_rss.usecase.detect_job_changes import DetectJobChanges
from job_search_rss.usecase.generate_rss_feed import GenerateRssFeed
from job_search_rss.usecase.manage_collection_condition import ManageCollectionCondition
from job_search_rss.usecase.query_job_changes_for_rss import RssChangeQuery
from job_search_rss.usecase.register_subscription_condition import (
    RegisterSubscriptionCondition,
)
from tests.fakes.repository import FakeRepository
from tests.fakes.site_adapter import FakeSiteAdapter


def fixed_clock() -> datetime:
    return datetime(2026, 5, 21, 12, 0, tzinfo=UTC)


def test_subscription_collection_and_rss_generation_flow_uses_saved_changes() -> None:
    repository = FakeRepository()
    site_adapter = FakeSiteAdapter()
    subscription_condition = SubscriptionCondition(region=Region(prefecture="Tokyo"))
    RegisterSubscriptionCondition(repository).execute(subscription_condition)
    collection_condition = ManageCollectionCondition(repository).execute()[0]
    site_adapter.add_job_for_condition(collection_condition, create_job())

    DetectJobChanges(repository, site_adapter, clock=fixed_clock).execute(
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
    assert rss_item is not None
    assert rss_item.findtext("title") == "[new] Backend Engineer - Example Inc."
    assert site_adapter.call_count == 1


def create_job() -> Job:
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
