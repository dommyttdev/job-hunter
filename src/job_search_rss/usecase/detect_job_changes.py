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
        try:
            fetched_jobs = self._site_adapter.fetch_jobs_for_condition(condition)
        except Exception as error:
            finished_at = self._clock()
            self._repository.save_collection_run(
                CollectionRun.failed(
                    collection_condition_key=condition.normalized_key,
                    started_at=started_at,
                    finished_at=finished_at,
                    error_message=str(error),
                )
            )
            return []
        existing_jobs_by_id = {job.job_id: job for job in self._repository.list_jobs()}
        fetched_job_ids = {job.job_id for job in fetched_jobs}
        previous_job_ids = set(
            self._repository.list_job_ids_for_condition(condition.normalized_key)
        )
        changes: list[JobChange] = []

        for job in fetched_jobs:
            existing_job = existing_jobs_by_id.get(job.job_id)
            if existing_job is None:
                change_type = JobChangeType.NEW
            elif existing_job.content_hash != job.content_hash:
                change_type = JobChangeType.UPDATED
            else:
                continue
            self._repository.save_job(job)
            change = JobChange(
                job_id=job.job_id,
                collection_condition_key=condition.normalized_key,
                change_type=change_type,
                content_hash=job.content_hash,
                occurred_at=started_at,
            )
            self._repository.save_job_change(change)
            changes.append(change)

        for deleted_job_id in sorted(previous_job_ids - fetched_job_ids):
            existing_job = existing_jobs_by_id[deleted_job_id]
            change = JobChange(
                job_id=deleted_job_id,
                collection_condition_key=condition.normalized_key,
                change_type=JobChangeType.DELETED,
                content_hash=existing_job.content_hash,
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
        self._repository.save_condition_snapshot(
            collection_condition_key=condition.normalized_key,
            job_ids=[job.job_id for job in fetched_jobs],
        )
        return changes


def _utc_now() -> datetime:
    return datetime.now(UTC)
