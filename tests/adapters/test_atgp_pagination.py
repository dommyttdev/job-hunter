from pathlib import Path

from job_search_rss.adapters.atgp import parse_next_page_url

FIXTURE_DIR = Path(__file__).parents[1] / "fixtures" / "atgp"


def test_parse_next_page_url_returns_absolute_next_page_url() -> None:
    html = (FIXTURE_DIR / "job_list_page_1.html").read_text(encoding="utf-8")

    next_url = parse_next_page_url(html)

    assert next_url == "https://www.atgp.jp/search/top/search_result?prefectures=13&page=2"


def test_parse_next_page_url_returns_none_on_last_page() -> None:
    html = (FIXTURE_DIR / "job_list_page_2.html").read_text(encoding="utf-8")

    assert parse_next_page_url(html) is None
