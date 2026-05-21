from collections.abc import Callable
from datetime import UTC, datetime

from job_search_rss.domain.collection_condition import CollectionCondition
from job_search_rss.domain.history import CollectionRun, JobChange, JobChangeType
from job_search_rss.ports.repository import Repository
from job_search_rss.ports.site_adapter import SiteAdapter


class DetectJobChanges:
    def __init__(
        self,
        repository: Repository,
        site_adapter: SiteAdapter,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._repository = repository
        self._site_adapter = site_adapter
        self._clock = clock or _utc_now

    def execute(self, condition: CollectionCondition) -> list[JobChange]:
        started_at = self._clock()
        fetched_jobs = self._site_adapter.fetch_jobs_for_condition(condition)
        existing_job_ids = {job.job_id for job in self._repository.list_jobs()}
        changes: list[JobChange] = []

        for job in fetched_jobs:
            self._repository.save_job(job)
            if job.job_id in existing_job_ids:
                continue
            change = JobChange(
                job_id=job.job_id,
                collection_condition_key=condition.normalized_key,
                change_type=JobChangeType.NEW,
                content_hash=job.content_hash,
                occurred_at=started_at,
            )
            self._repository.save_job_change(change)
            changes.append(change)

        finished_at = self._clock()
        self._repository.save_collection_run(
            CollectionRun.succeeded(
                collection_condition_key=condition.normalized_key,
                started_at=started_at,
                finished_at=finished_at,
                collected_job_count=len(fetched_jobs),
            )
        )
        return changes


def _utc_now() -> datetime:
    return datetime.now(UTC)
