from job_search_rss.domain.collection_condition import CollectionCondition
from job_search_rss.domain.condition_values import Occupation, Region
from job_search_rss.domain.subscription_condition import SubscriptionCondition


def test_collection_condition_is_built_from_subscription_condition() -> None:
    subscription_condition = SubscriptionCondition(
        region=Region(prefecture="Tokyo"),
        occupation=Occupation(category="IT Web", detail="Backend Engineer"),
    )

    collection_condition = CollectionCondition.from_subscription_condition(
        site_id="atgp",
        subscription_condition=subscription_condition,
    )

    assert collection_condition.site_id == "atgp"
    assert (
        collection_condition.condition_key
        == "region:tokyo|occupation:it-web:backend-engineer"
    )
    assert (
        collection_condition.normalized_key
        == "collection:atgp:region:tokyo|occupation:it-web:backend-engineer"
    )


def test_collection_condition_matches_by_site_and_condition_key() -> None:
    first = CollectionCondition(site_id="atgp", condition_key="region:tokyo")
    second = CollectionCondition(site_id="atgp", condition_key="region:tokyo")
    other_site = CollectionCondition(site_id="other", condition_key="region:tokyo")

    assert first.has_same_conditions_as(second)
    assert not first.has_same_conditions_as(other_site)
