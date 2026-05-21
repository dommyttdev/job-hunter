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
