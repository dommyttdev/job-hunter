from typing import Protocol, cast

from job_search_rss.domain.history import JobChange
from job_search_rss.domain.job import Job
from job_search_rss.rss.renderer import RssItem
from job_search_rss.usecase.query_job_changes_for_rss import (
    QueryJobChangesForRss,
    RssChangeQuery,
)

JobChangeData = dict[str, str]


class ChangeRepository(Protocol):
    def list_changes_for_subscription(self, subscription_id: str) -> list[JobChangeData]: ...


class RssRepository(Protocol):
    def list_job_changes(self) -> list[JobChange]: ...

    def list_jobs(self) -> list[Job]: ...


class RssRenderer(Protocol):
    def render(self, changes: list[JobChangeData]) -> str: ...


class RssItemRenderer(Protocol):
    def render_items(self, items: list[RssItem]) -> str: ...


class GenerateRssFeed:
    def __init__(self, repository: object, renderer: object) -> None:
        self._repository = repository
        self._renderer = renderer

    def execute(self, query_or_subscription_id: RssChangeQuery | str) -> str:
        if isinstance(query_or_subscription_id, str):
            repository = cast(ChangeRepository, self._repository)
            renderer = cast(RssRenderer, self._renderer)
            changes = repository.list_changes_for_subscription(query_or_subscription_id)
            return renderer.render(changes)

        repository = cast(RssRepository, self._repository)
        renderer = cast(RssItemRenderer, self._renderer)
        changes = QueryJobChangesForRss(repository).execute(query_or_subscription_id)
        jobs_by_id = {job.job_id: job for job in repository.list_jobs()}
        return renderer.render_items(
            [
                _create_rss_item(change=change, job=jobs_by_id[change.job_id])
                for change in changes
                if change.job_id in jobs_by_id
            ]
        )


def _create_rss_item(*, change: JobChange, job: Job) -> RssItem:
    region, occupation = _extract_condition_labels(change.collection_condition_key)
    change_type = change.change_type.value
    return RssItem(
        title=f"[{change_type}] {job.title} - {job.company_name}",
        link=job.detail_url,
        description=(
            f"{change_type} / {region} / {occupation} / {job.company_name}"
        ),
        guid=f"{job.job_id}:{change.content_hash}:{change_type}",
        pub_date=change.occurred_at,
        change_type=change.change_type,
        region=region,
        occupation=occupation,
    )


def _extract_condition_labels(collection_condition_key: str) -> tuple[str, str]:
    condition_key = collection_condition_key.removeprefix("collection:atgp:")
    labels: dict[str, str] = {}
    for part in condition_key.split("|"):
        label_type, _, value = part.partition(":")
        labels[label_type] = value.replace(":", "/")
    return labels.get("region", ""), labels.get("occupation", "")
