from job_search_rss.domain.collection_condition import CollectionCondition
from job_search_rss.domain.condition_values import Occupation, Region
from job_search_rss.domain.job import Job
from job_search_rss.ports.site_adapter import SiteAdapter
from tests.fakes.site_adapter import FakeSiteAdapter


def test_fake_site_adapter_returns_masters_jobs_and_details() -> None:
    adapter: SiteAdapter = FakeSiteAdapter()
    region = Region(prefecture="Tokyo")
    occupation = Occupation(category="IT Web", detail="Backend Engineer")
    condition = CollectionCondition(site_id="atgp", condition_key="region:tokyo")
    job = Job(
        job_id="atgp-001",
        site_id="atgp",
        title="Backend Engineer",
        company_name="Example Inc.",
        detail_url="https://example.test/jobs/atgp-001",
        work_location="Tokyo",
        occupation="Backend Engineer",
        salary="5,000,000 JPY",
        content_hash="hash-001",
    )

    adapter.add_region(region)
    adapter.add_occupation(occupation)
    adapter.add_job_for_condition(condition, job)

    assert adapter.list_regions() == [region]
    assert adapter.list_occupations() == [occupation]
    assert adapter.fetch_jobs_for_condition(condition) == [job]
    assert adapter.fetch_job_detail(site_id="atgp", job_id="atgp-001") == job
