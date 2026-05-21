from job_search_rss.domain.collection_condition import CollectionCondition
from job_search_rss.domain.condition_values import Occupation, Region
from job_search_rss.domain.job import Job
from tests.fakes.types import JobData


class FakeSiteAdapter:
    def __init__(self) -> None:
        self._jobs_by_condition: dict[str, list[JobData]] = {}
        self._domain_jobs_by_condition: dict[str, list[Job]] = {}
        self._domain_jobs_by_id: dict[tuple[str, str], Job] = {}
        self._regions: list[Region] = []
        self._occupations: list[Occupation] = []
        self.call_count = 0
        self.raise_if_called = False

    def add_job(
        self,
        *,
        condition_key: str,
        job_id: str,
        title: str,
        company_name: str,
    ) -> None:
        self._jobs_by_condition.setdefault(condition_key, []).append(
            {
                "job_id": job_id,
                "title": title,
                "company_name": company_name,
            }
        )

    def fetch_jobs(self, condition_key: str) -> list[JobData]:
        if self.raise_if_called:
            msg = "SiteAdapter must not be called"
            raise AssertionError(msg)

        self.call_count += 1
        return list(self._jobs_by_condition.get(condition_key, []))

    def add_region(self, region: Region) -> None:
        self._regions.append(region)

    def list_regions(self) -> list[Region]:
        return list(self._regions)

    def add_occupation(self, occupation: Occupation) -> None:
        self._occupations.append(occupation)

    def list_occupations(self) -> list[Occupation]:
        return list(self._occupations)

    def add_job_for_condition(self, condition: CollectionCondition, job: Job) -> None:
        self._domain_jobs_by_condition.setdefault(condition.normalized_key, []).append(job)
        self._domain_jobs_by_id[(job.site_id, job.job_id)] = job

    def replace_jobs_for_condition(
        self,
        condition: CollectionCondition,
        jobs: list[Job],
    ) -> None:
        self._domain_jobs_by_condition[condition.normalized_key] = list(jobs)
        for job in jobs:
            self._domain_jobs_by_id[(job.site_id, job.job_id)] = job

    def fetch_jobs_for_condition(self, condition: CollectionCondition) -> list[Job]:
        if self.raise_if_called:
            msg = "SiteAdapter must not be called"
            raise AssertionError(msg)

        self.call_count += 1
        return list(self._domain_jobs_by_condition.get(condition.normalized_key, []))

    def fetch_job_detail(self, *, site_id: str, job_id: str) -> Job | None:
        if self.raise_if_called:
            msg = "SiteAdapter must not be called"
            raise AssertionError(msg)

        self.call_count += 1
        return self._domain_jobs_by_id.get((site_id, job_id))
