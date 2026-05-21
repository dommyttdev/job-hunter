from typing import Protocol

from job_search_rss.domain.history import JobChange


class RssRenderer(Protocol):
    def render_changes(self, changes: list[JobChange]) -> str: ...
