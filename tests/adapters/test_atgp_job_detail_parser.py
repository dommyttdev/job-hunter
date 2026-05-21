from pathlib import Path

from job_search_rss.adapters.atgp import parse_job_detail
from job_search_rss.domain.job import Job


FIXTURE_DIR = Path(__file__).parents[1] / "fixtures" / "atgp"


def test_parse_job_detail_converts_detail_page_to_common_job() -> None:
    html = (FIXTURE_DIR / "job_detail.html").read_text(encoding="utf-8")

    job = parse_job_detail(
        html,
        detail_url="https://www.atgp.jp/search/top/search_result_detail/a076000000010skevs",
    )

    assert job == Job(
        job_id="a076000000010skevs",
        site_id="atgp",
        title="採用先：タイムズサービス株式会社【品質管理事務】",
        company_name="パーク２４グループ",
        detail_url="https://www.atgp.jp/search/top/search_result_detail/a076000000010skevs",
        work_location="東京都 品川区",
        occupation="品質管理事務",
        salary="月収： 230,000円 ~ 300,000円 (年収： 308万円 ~ 480万円)",
        content_hash=Job.generate_content_hash(
            title="採用先：タイムズサービス株式会社【品質管理事務】",
            company_name="パーク２４グループ",
            detail_url="https://www.atgp.jp/search/top/search_result_detail/a076000000010skevs",
            work_location="東京都 品川区",
            occupation="品質管理事務",
            salary="月収： 230,000円 ~ 300,000円 (年収： 308万円 ~ 480万円)",
            description="工事発注と品質管理に関する事務業務を担当します。",
        ),
    )
