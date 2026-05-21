from job_search_rss.domain.collection_condition import CollectionCondition
from job_search_rss.ports.repository import Repository


class ManageCollectionCondition:
    def __init__(self, repository: Repository, *, site_id: str = "atgp") -> None:
        self._repository = repository
        self._site_id = site_id

    def execute(self) -> list[CollectionCondition]:
        collection_conditions = self._repository.list_collection_conditions()
        collection_condition_by_key = {
            condition.normalized_key: condition for condition in collection_conditions
        }

        for subscription_condition in self._repository.list_subscription_conditions():
            collection_condition = CollectionCondition.from_subscription_condition(
                site_id=self._site_id,
                subscription_condition=subscription_condition,
            )
            if collection_condition.normalized_key in collection_condition_by_key:
                continue
            self._repository.save_collection_condition(collection_condition)
            collection_condition_by_key[collection_condition.normalized_key] = (
                collection_condition
            )

        return list(collection_condition_by_key.values())
