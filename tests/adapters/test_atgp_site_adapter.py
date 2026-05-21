from pathlib import Path

from job_search_rss.adapters.atgp import AtgpSiteAdapter
from job_search_rss.domain.collection_condition import CollectionCondition
from job_search_rss.domain.condition_values import Occupation, Region


FIXTURE_DIR = Path(__file__).parents[1] / "fixtures" / "atgp"


class FakeFetcher:
    def __init__(self, pages: dict[str, str]) -> None:
        self.pages = pages
        self.calls: list[str] = []

    def fetch_page(self, url: str) -> str:
        self.calls.append(url)
        return self.pages[url]


def test_atgp_site_adapter_lists_masters() -> None:
    adapter = AtgpSiteAdapter(
        FakeFetcher(
            {
                "https://www.atgp.jp/search/top/search_result": (
                    FIXTURE_DIR / "region_master.html"
                ).read_text(encoding="utf-8"),
                "https://www.atgp.jp/search/top/search_result?masters=occupations": (
                    FIXTURE_DIR / "occupation_master.html"
                ).read_text(encoding="utf-8"),
            }
        )
    )

    assert adapter.list_regions() == [
        Region(prefecture="東京都"),
        Region(prefecture="神奈川県"),
        Region(prefecture="大阪府"),
    ]
    assert adapter.list_occupations() == [
        Occupation(category="事務関連", detail="事務関連"),
        Occupation(category="IT・エンジニア", detail="IT・エンジニア"),
    ]


def test_atgp_site_adapter_fetches_jobs_for_condition_across_pages() -> None:
    search_url = "https://www.atgp.jp/search/top/search_result?prefectures=13"
    next_url = "https://www.atgp.jp/search/top/search_result?prefectures=13&page=2"
    adapter = AtgpSiteAdapter(
        FakeFetcher(
            {
                "https://www.atgp.jp/search/top/search_result": (
                    FIXTURE_DIR / "region_master.html"
                ).read_text(encoding="utf-8"),
                "https://www.atgp.jp/search/top/search_result?masters=occupations": (
                    FIXTURE_DIR / "occupation_master.html"
                ).read_text(encoding="utf-8"),
                search_url: (FIXTURE_DIR / "job_list_page_1.html").read_text(encoding="utf-8"),
                next_url: (FIXTURE_DIR / "job_list_page_2.html").read_text(encoding="utf-8"),
            }
        )
    )

    jobs = adapter.fetch_jobs_for_condition(
        CollectionCondition(site_id="atgp", condition_key=Region("東京都").normalized_key)
    )

    assert [job.job_id for job in jobs] == [
        "a076000000010skevs",
        "a076000000010scope",
    ]


def test_atgp_site_adapter_fetches_job_detail() -> None:
    adapter = AtgpSiteAdapter(
        FakeFetcher(
            {
                "https://www.atgp.jp/search/top/search_result_detail/a076000000010skevs": (
                    FIXTURE_DIR / "job_detail.html"
                ).read_text(encoding="utf-8")
            }
        )
    )

    job = adapter.fetch_job_detail(site_id="atgp", job_id="a076000000010skevs")

    assert job is not None
    assert job.job_id == "a076000000010skevs"
    assert job.occupation == "品質管理事務"
