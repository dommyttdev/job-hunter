from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from job_search_rss.domain.collection_condition import CollectionCondition
from job_search_rss.domain.history import CollectionRunStatus, JobChange
from job_search_rss.ports.repository import Repository
from job_search_rss.ports.site_adapter import SiteAdapter
from job_search_rss.usecase.detect_job_changes import DetectJobChanges


@dataclass(frozen=True)
class CollectionExecutionResult:
    changes: list[JobChange]
    succeeded_condition_keys: list[str]
    failed_condition_keys: list[str]

    @property
    def can_detect_deletions(self) -> bool:
        return not self.failed_condition_keys


class RunCollection:
    def __init__(
        self,
        repository: Repository,
        site_adapter: SiteAdapter,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._repository = repository
        self._site_adapter = site_adapter
        self._clock = clock

    def execute(self) -> CollectionExecutionResult:
        detector = DetectJobChanges(
            self._repository,
            self._site_adapter,
            clock=self._clock,
        )
        changes: list[JobChange] = []
        succeeded_condition_keys: list[str] = []
        failed_condition_keys: list[str] = []
        for condition in self._repository.list_collection_conditions():
            changes.extend(detector.execute(condition))
            if _latest_run_succeeded(self._repository, condition):
                succeeded_condition_keys.append(condition.normalized_key)
            else:
                failed_condition_keys.append(condition.normalized_key)
        return CollectionExecutionResult(
            changes=changes,
            succeeded_condition_keys=succeeded_condition_keys,
            failed_condition_keys=failed_condition_keys,
        )


def _latest_run_succeeded(
    repository: Repository,
    condition: CollectionCondition,
) -> bool:
    matching_runs = [
        run
        for run in repository.list_collection_runs()
        if run.collection_condition_key == condition.normalized_key
    ]
    if not matching_runs:
        return False
    return matching_runs[-1].status == CollectionRunStatus.SUCCEEDED
