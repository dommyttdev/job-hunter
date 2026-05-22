"""Scheduling components."""
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from job_search_rss.ports.repository import Repository
from job_search_rss.ports.site_adapter import SiteAdapter
from job_search_rss.usecase.manage_collection_condition import ManageCollectionCondition
from job_search_rss.usecase.run_collection import RunCollection


@dataclass(frozen=True)
class ScheduledJobResult:
    change_count: int
    succeeded_condition_count: int
    failed_condition_count: int


class IntervalScheduler(Protocol):
    def add_interval_job(
        self,
        func: Callable[[], ScheduledJobResult],
        *,
        minutes: int,
        job_id: str,
    ) -> None: ...


def register_periodic_collection_job(
    scheduler: IntervalScheduler,
    *,
    repository: Repository,
    site_adapter: SiteAdapter,
    interval_minutes: int,
) -> None:
    def collect() -> ScheduledJobResult:
        ManageCollectionCondition(repository).execute()
        result = RunCollection(repository, site_adapter).execute()
        return ScheduledJobResult(
            change_count=len(result.changes),
            succeeded_condition_count=len(result.succeeded_condition_keys),
            failed_condition_count=len(result.failed_condition_keys),
        )

    ManageCollectionCondition(repository).execute()
    scheduler.add_interval_job(
        collect,
        minutes=interval_minutes,
        job_id="job-search-rss-collection",
    )
