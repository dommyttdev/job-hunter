from datetime import UTC, datetime
from pathlib import Path
from xml.etree import ElementTree

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from job_search_rss.adapters.atgp import AtgpSiteAdapter
from job_search_rss.domain.condition_values import Region
from job_search_rss.domain.history import JobChangeType
from job_search_rss.domain.subscription_condition import SubscriptionCondition
from job_search_rss.infrastructure.database import SqlAlchemyRepository, create_schema
from job_search_rss.rss.renderer import XmlRssRenderer
from job_search_rss.usecase.generate_rss_feed import GenerateRssFeed
from job_search_rss.usecase.manage_collection_condition import ManageCollectionCondition
from job_search_rss.usecase.query_job_changes_for_rss import RssChangeQuery
from job_search_rss.usecase.register_subscription_condition import (
    RegisterSubscriptionCondition,
)
from job_search_rss.usecase.run_collection import RunCollection
from job_search_rss.usecase.sync_site_master import SyncSiteMaster

FIXTURE_DIR = Path(__file__).parents[1] / "fixtures" / "atgp"


class FixtureFetcher:
    def __init__(self, pages: dict[str, str]) -> None:
        self._pages = pages
        self.calls: list[str] = []

    def fetch_page(self, url: str) -> str:
        self.calls.append(url)
        return self._pages[url]


def fixed_clock() -> datetime:
    return datetime(2026, 5, 21, 12, 0, tzinfo=UTC)


def test_atgp_fixture_collection_persists_changes_and_generates_rss() -> None:
    repository = create_repository()
    search_url = "https://www.atgp.jp/search/top/search_result?prefectures=13"
    next_url = "https://www.atgp.jp/search/top/search_result?prefectures=13&page=2"
    fetcher = FixtureFetcher(
        {
            "https://www.atgp.jp/search/top/search_result": (
                FIXTURE_DIR / "region_master.html"
            ).read_text(encoding="utf-8"),
            "https://www.atgp.jp/search/top/search_result?masters=occupations": (
                FIXTURE_DIR / "occupation_master.html"
            ).read_text(encoding="utf-8"),
            search_url: (FIXTURE_DIR / "job_list_page_1.html").read_text(
                encoding="utf-8"
            ),
            next_url: (FIXTURE_DIR / "job_list_page_2.html").read_text(encoding="utf-8"),
        }
    )
    site_adapter = AtgpSiteAdapter(fetcher)
    subscription_condition = SubscriptionCondition(region=Region(prefecture="\u6771\u4eac\u90fd"))

    SyncSiteMaster(repository, site_adapter).execute()
    RegisterSubscriptionCondition(repository).execute(subscription_condition)
    ManageCollectionCondition(repository).execute()
    result = RunCollection(repository, site_adapter, clock=fixed_clock).execute()
    calls_after_collection = list(fetcher.calls)

    xml = GenerateRssFeed(
        repository,
        XmlRssRenderer(
            title="Job Search Changes",
            link="https://example.test/rss",
            description="Latest job changes",
        ),
    ).execute(RssChangeQuery(subscription_condition=subscription_condition))

    rss_items = ElementTree.fromstring(xml).findall("channel/item")
    assert [change.change_type for change in result.changes] == [
        JobChangeType.NEW,
        JobChangeType.NEW,
    ]
    assert [item.findtext("guid") for item in rss_items] == [
        "a076000000010skevs:"
        "8503989d2e3d7316fc0310974f4598902c7a238310c31588a016f214b6841310:new",
        "a076000000010scope:"
        "05d36f7a59fbac591ae16bed7bc8eee5db454aa5bb4d92bb514714c8df741b3c:new",
    ]
    assert fetcher.calls == calls_after_collection


def create_repository() -> SqlAlchemyRepository:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    create_schema(engine)
    return SqlAlchemyRepository(engine)
