from collections.abc import Callable
from datetime import datetime

from job_search_rss.domain.history import JobChange
from job_search_rss.ports.repository import Repository
from job_search_rss.ports.site_adapter import SiteAdapter
from job_search_rss.usecase.detect_job_changes import DetectJobChanges


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

    def execute(self) -> list[JobChange]:
        detector = DetectJobChanges(
            self._repository,
            self._site_adapter,
            clock=self._clock,
        )
        changes: list[JobChange] = []
        for condition in self._repository.list_collection_conditions():
            changes.extend(detector.execute(condition))
        return changes
