from tests.fakes.repository import FakeRepository

from job_search_rss.domain.collection_condition import CollectionCondition
from job_search_rss.domain.condition_values import Occupation, Region
from job_search_rss.domain.subscription_condition import SubscriptionCondition
from job_search_rss.usecase.manage_collection_condition import ManageCollectionCondition


def test_manage_collection_condition_creates_condition_from_subscription() -> None:
    repository = FakeRepository()
    subscription_condition = SubscriptionCondition(
        region=Region(prefecture="Tokyo"),
        occupation=Occupation(category="IT Web", detail="Backend Engineer"),
    )
    repository.save_subscription_condition(subscription_condition)

    collection_conditions = ManageCollectionCondition(repository).execute()

    assert collection_conditions == [
        CollectionCondition(
            site_id="atgp",
            condition_key="region:tokyo|occupation:it-web:backend-engineer",
        )
    ]
    assert repository.list_collection_conditions() == collection_conditions


def test_manage_collection_condition_does_not_duplicate_same_collection_condition() -> None:
    repository = FakeRepository()
    first_subscription_condition = SubscriptionCondition(
        region=Region(prefecture=" Tokyo "),
        occupation=Occupation(category="IT Web", detail="Backend Engineer"),
    )
    same_subscription_condition = SubscriptionCondition(
        region=Region(prefecture="tokyo"),
        occupation=Occupation(category="it   web", detail="backend engineer"),
    )
    repository.save_subscription_condition(first_subscription_condition)
    repository.save_subscription_condition(same_subscription_condition)

    collection_conditions = ManageCollectionCondition(repository).execute()

    assert collection_conditions == [
        CollectionCondition(
            site_id="atgp",
            condition_key="region:tokyo|occupation:it-web:backend-engineer",
        )
    ]
    assert repository.list_collection_conditions() == collection_conditions
