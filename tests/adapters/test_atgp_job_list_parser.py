import json
from pathlib import Path
from typing import Any

from job_search_rss.adapters.atgp import parse_job_list
from job_search_rss.domain.job import Job

FIXTURE_DIR = Path(__file__).parents[1] / "fixtures" / "atgp"


def test_parse_job_list_converts_cards_to_common_jobs() -> None:
    html = (FIXTURE_DIR / "job_list_page_1.html").read_text(encoding="utf-8")
    expected_data = json.loads(
        (FIXTURE_DIR / "expected_jobs.json").read_text(encoding="utf-8")
    )

    jobs = parse_job_list(html)

    assert jobs == [_job_from_expected(item) for item in expected_data]


def _job_from_expected(item: dict[str, Any]) -> Job:
    return Job(
        job_id=str(item["job_id"]),
        site_id=str(item["site_id"]),
        title=str(item["title"]),
        company_name=str(item["company_name"]),
        detail_url=str(item["detail_url"]),
        work_location=str(item["work_location"]),
        occupation=str(item["occupation"]),
        salary=str(item["salary"]),
        content_hash=Job.generate_content_hash(
            title=str(item["title"]),
            company_name=str(item["company_name"]),
            detail_url=str(item["detail_url"]),
            work_location=str(item["work_location"]),
            occupation=str(item["occupation"]),
            salary=str(item["salary"]),
            description="",
        ),
    )
