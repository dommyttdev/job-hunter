from job_search_rss.domain.history import JobChange
from tests.fakes.types import JobChangeData


class FakeRssRenderer:
    def render(self, changes: list[JobChangeData]) -> str:
        items = [
            f"{change['change_type']}:{change['title']}:{change['company_name']}"
            for change in changes
        ]
        return "\n".join(items)

    def render_changes(self, changes: list[JobChange]) -> str:
        items = [
            (
                f"{change.change_type.value}:"
                f"{change.job_id}:"
                f"{change.collection_condition_key}:"
                f"{change.content_hash}"
            )
            for change in changes
        ]
        return "\n".join(items)
