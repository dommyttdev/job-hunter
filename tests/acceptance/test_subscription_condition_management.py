from job_search_rss.domain.collection_condition import CollectionCondition
from job_search_rss.domain.condition_values import Occupation, Region
from job_search_rss.domain.subscription_condition import SubscriptionCondition
from job_search_rss.usecase.manage_collection_condition import ManageCollectionCondition
from job_search_rss.usecase.register_subscription_condition import (
    RegisterSubscriptionCondition,
)
from tests.fakes.repository import FakeRepository


def test_subscription_registration_creates_unique_collection_condition() -> None:
    repository = FakeRepository()
    register_subscription = RegisterSubscriptionCondition(repository)

    first_subscription = register_subscription.execute(
        SubscriptionCondition(
            region=Region(prefecture=" Tokyo "),
            occupation=Occupation(category="IT Web", detail="Backend Engineer"),
        )
    )
    second_subscription = register_subscription.execute(
        SubscriptionCondition(
            region=Region(prefecture="tokyo"),
            occupation=Occupation(category="it   web", detail="backend engineer"),
        )
    )
    collection_conditions = ManageCollectionCondition(repository).execute()

    assert second_subscription.id == first_subscription.id
    assert repository.list_subscription_conditions() == [first_subscription.condition]
    assert collection_conditions == [
        CollectionCondition(
            site_id="atgp",
            condition_key="region:tokyo|occupation:it-web:backend-engineer",
        )
    ]
