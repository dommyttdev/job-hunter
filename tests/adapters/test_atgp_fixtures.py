from pathlib import Path

FIXTURE_DIR = Path(__file__).parents[1] / "fixtures" / "atgp"


def test_atgp_html_fixtures_exist_for_adapter_tasks() -> None:
    expected_files = {
        "region_master.html",
        "occupation_master.html",
        "job_list_page_1.html",
        "job_detail.html",
        "expected_jobs.json",
    }

    assert expected_files <= {path.name for path in FIXTURE_DIR.iterdir()}


def test_atgp_job_list_fixture_contains_required_common_fields() -> None:
    html = (FIXTURE_DIR / "job_list_page_1.html").read_text(encoding="utf-8")

    assert "data-job-id=\"a076000000010skevs\"" in html
    assert "search_result_detail/a076000000010skevs" in html
    assert "職種" in html
    assert "勤務地" in html
    assert "給与" in html
