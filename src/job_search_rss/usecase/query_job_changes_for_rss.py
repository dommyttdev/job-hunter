from dataclasses import dataclass, field

from job_search_rss.domain.collection_condition import CollectionCondition
from job_search_rss.domain.history import JobChange, JobChangeType
from job_search_rss.domain.subscription_condition import SubscriptionCondition
from job_search_rss.ports.repository import Repository


def _empty_change_types() -> set[JobChangeType]:
    return set()


@dataclass(frozen=True)
class RssChangeQuery:
    subscription_condition: SubscriptionCondition
    change_types: set[JobChangeType] = field(default_factory=_empty_change_types)
    site_id: str = "atgp"


class QueryJobChangesForRss:
    def __init__(self, repository: Repository) -> None:
        self._repository = repository

    def execute(self, query: RssChangeQuery) -> list[JobChange]:
        collection_condition = CollectionCondition.from_subscription_condition(
            site_id=query.site_id,
            subscription_condition=query.subscription_condition,
        )
        changes = [
            change
            for change in self._repository.list_job_changes()
            if change.collection_condition_key == collection_condition.normalized_key
        ]
        if query.change_types:
            changes = [
                change for change in changes if change.change_type in query.change_types
            ]
        return changes
