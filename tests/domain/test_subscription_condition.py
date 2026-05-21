import pytest

from job_search_rss.domain.condition_values import Occupation, Region
from job_search_rss.domain.subscription_condition import SubscriptionCondition


def test_subscription_condition_can_use_region_only() -> None:
    condition = SubscriptionCondition(region=Region(prefecture="Tokyo"))

    assert condition.normalized_key == "subscription:region:tokyo"


def test_subscription_condition_can_use_occupation_only() -> None:
    condition = SubscriptionCondition(
        occupation=Occupation(category="IT Web", detail="Backend Engineer")
    )

    assert condition.normalized_key == "subscription:occupation:it-web:backend-engineer"


def test_subscription_condition_can_combine_region_and_occupation() -> None:
    condition = SubscriptionCondition(
        region=Region(prefecture="Tokyo", city="Shibuya"),
        occupation=Occupation(category="IT Web", detail="Backend Engineer"),
    )

    assert (
        condition.normalized_key
        == "subscription:region:tokyo:shibuya|occupation:it-web:backend-engineer"
    )


def test_subscription_condition_matches_by_normalized_key() -> None:
    first = SubscriptionCondition(
        region=Region(prefecture=" Tokyo "),
        occupation=Occupation(category="IT Web", detail="Backend Engineer"),
    )
    second = SubscriptionCondition(
        region=Region(prefecture="tokyo"),
        occupation=Occupation(category="it   web", detail="backend engineer"),
    )

    assert first.has_same_conditions_as(second)


def test_subscription_condition_requires_region_or_occupation() -> None:
    with pytest.raises(ValueError, match="region or occupation"):
        SubscriptionCondition()
