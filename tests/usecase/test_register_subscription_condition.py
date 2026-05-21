from tests.fakes.repository import FakeRepository

from job_search_rss.domain.condition_values import Occupation, Region
from job_search_rss.domain.subscription_condition import SubscriptionCondition
from job_search_rss.usecase.register_subscription_condition import (
    RegisterSubscriptionCondition,
)


def test_register_subscription_condition_saves_region_and_occupation_condition() -> None:
    repository = FakeRepository()
    condition = SubscriptionCondition(
        region=Region(prefecture="Tokyo"),
        occupation=Occupation(category="IT Web", detail="Backend Engineer"),
    )

    registered = RegisterSubscriptionCondition(repository).execute(condition)

    assert registered.id == "subscription:region:tokyo|occupation:it-web:backend-engineer"
    assert registered.condition == condition
    assert repository.list_subscription_conditions() == [condition]


def test_register_subscription_condition_saves_region_only_condition() -> None:
    repository = FakeRepository()
    condition = SubscriptionCondition(region=Region(prefecture="Tokyo"))

    registered = RegisterSubscriptionCondition(repository).execute(condition)

    assert registered.id == "subscription:region:tokyo"
    assert registered.condition == condition
    assert repository.list_subscription_conditions() == [condition]


def test_register_subscription_condition_does_not_duplicate_same_condition() -> None:
    repository = FakeRepository()
    first_condition = SubscriptionCondition(
        region=Region(prefecture=" Tokyo "),
        occupation=Occupation(category="IT Web", detail="Backend Engineer"),
    )
    same_condition = SubscriptionCondition(
        region=Region(prefecture="tokyo"),
        occupation=Occupation(category="it   web", detail="backend engineer"),
    )

    first_registered = RegisterSubscriptionCondition(repository).execute(first_condition)
    second_registered = RegisterSubscriptionCondition(repository).execute(same_condition)

    assert second_registered.id == first_registered.id
    assert second_registered.condition == first_condition
    assert repository.list_subscription_conditions() == [first_condition]
