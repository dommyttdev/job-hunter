from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from time import sleep

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
        max_attempts_per_condition: int = 1,
        condition_delay_seconds: float = 0.0,
        sleeper: Callable[[float], None] = sleep,
    ) -> None:
        self._repository = repository
        self._site_adapter = site_adapter
        self._clock = clock
        if max_attempts_per_condition < 1:
            msg = "max_attempts_per_condition must be at least 1"
            raise ValueError(msg)
        if condition_delay_seconds < 0:
            msg = "condition_delay_seconds must not be negative"
            raise ValueError(msg)
        self._max_attempts_per_condition = max_attempts_per_condition
        self._condition_delay_seconds = condition_delay_seconds
        self._sleeper = sleeper

    def execute(self) -> CollectionExecutionResult:
        detector = DetectJobChanges(
            self._repository,
            self._site_adapter,
            clock=self._clock,
        )
        changes: list[JobChange] = []
        succeeded_condition_keys: list[str] = []
        failed_condition_keys: list[str] = []
        collection_conditions = self._repository.list_collection_conditions()
        for index, condition in enumerate(collection_conditions):
            for _ in range(self._max_attempts_per_condition):
                changes.extend(detector.execute(condition))
                if _latest_run_succeeded(self._repository, condition):
                    break
            if _latest_run_succeeded(self._repository, condition):
                succeeded_condition_keys.append(condition.normalized_key)
            else:
                failed_condition_keys.append(condition.normalized_key)
            if (
                self._condition_delay_seconds > 0
                and index < len(collection_conditions) - 1
            ):
                self._sleeper(self._condition_delay_seconds)
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
