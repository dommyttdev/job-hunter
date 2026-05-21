from datetime import UTC, datetime
from xml.etree import ElementTree

from tests.fakes.repository import FakeRepository
from tests.fakes.site_adapter import FakeSiteAdapter

from job_search_rss.domain.condition_values import Region
from job_search_rss.domain.history import JobChange, JobChangeType
from job_search_rss.domain.job import Job
from job_search_rss.domain.subscription_condition import SubscriptionCondition
from job_search_rss.rss.renderer import XmlRssRenderer
from job_search_rss.usecase.generate_rss_feed import GenerateRssFeed
from job_search_rss.usecase.query_job_changes_for_rss import RssChangeQuery


def test_generate_rss_feed_uses_saved_changes_without_site_access() -> None:
    repository = FakeRepository()
    site_adapter = FakeSiteAdapter()
    site_adapter.raise_if_called = True
    job = create_job()
    repository.save_job(job)
    repository.save_job_change(
        JobChange(
            job_id=job.job_id,
            collection_condition_key="collection:atgp:region:tokyo",
            change_type=JobChangeType.NEW,
            content_hash=job.content_hash,
            occurred_at=datetime(2026, 5, 21, 12, 0, tzinfo=UTC),
        )
    )

    xml = GenerateRssFeed(
        repository,
        XmlRssRenderer(
            title="Job Search Changes",
            link="https://example.test/rss",
            description="Latest job changes",
        ),
    ).execute(
        RssChangeQuery(
            subscription_condition=SubscriptionCondition(
                region=Region(prefecture="Tokyo")
            )
        )
    )

    rss_item = ElementTree.fromstring(xml).find("channel/item")
    assert rss_item is not None
    assert rss_item.findtext("title") == "[new] Backend Engineer - Example Inc."
    assert rss_item.findtext("link") == "https://example.test/jobs/atgp-001"
    assert site_adapter.call_count == 0


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
