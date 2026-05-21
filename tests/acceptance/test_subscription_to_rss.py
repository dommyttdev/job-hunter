from job_search_rss.usecase.generate_rss_feed import GenerateRssFeed
from job_search_rss.usecase.register_subscription_condition import (
    RegisterSubscriptionCondition,
)
from tests.fakes.repository import FakeRepository
from tests.fakes.rss_renderer import FakeRssRenderer
from tests.fakes.site_adapter import FakeSiteAdapter


def test_subscription_to_rss_flow_does_not_access_site_during_rss_generation() -> None:
    repository = FakeRepository()
    site_adapter = FakeSiteAdapter()
    rss_renderer = FakeRssRenderer()
    site_adapter.add_job(
        condition_key="region:tokyo|occupation:web-engineer",
        job_id="atgp-1",
        title="Webエンジニア",
        company_name="Example Inc.",
    )

    subscription = RegisterSubscriptionCondition(repository).execute(
        prefecture="東京都",
        occupation_category="IT・Web",
        occupation_detail="Webエンジニア",
    )
    repository.collect_jobs_for_subscription(subscription.id, site_adapter)

    site_adapter.raise_if_called = True
    rss = GenerateRssFeed(repository, rss_renderer).execute(subscription.id)

    assert "Webエンジニア" in rss
    assert "new" in rss
    assert site_adapter.call_count == 1
