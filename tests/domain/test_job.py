import hashlib

from job_search_rss.domain.job import Job


def test_job_keeps_common_rss_and_change_detection_fields() -> None:
    job = Job(
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

    assert job.job_id == "atgp-001"
    assert job.site_id == "atgp"
    assert job.title == "Backend Engineer"
    assert job.company_name == "Example Inc."
    assert job.detail_url == "https://example.test/jobs/atgp-001"
    assert job.work_location == "Tokyo"
    assert job.occupation == "Web Engineer"
    assert job.salary == "5,000,000 JPY"
    assert job.content_hash == "hash-001"


def test_job_can_generate_stable_content_hash() -> None:
    content_hash = Job.generate_content_hash(
        title="Backend Engineer",
        company_name="Example Inc.",
        detail_url="https://example.test/jobs/atgp-001",
        work_location="Tokyo",
        occupation="Web Engineer",
        salary="5,000,000 JPY",
        description="Build APIs",
    )

    expected = hashlib.sha256(
        "\n".join(
            [
                "Backend Engineer",
                "Example Inc.",
                "https://example.test/jobs/atgp-001",
                "Tokyo",
                "Web Engineer",
                "5,000,000 JPY",
                "Build APIs",
            ]
        ).encode("utf-8")
    ).hexdigest()
    assert content_hash == expected
