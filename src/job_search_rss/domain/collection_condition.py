from dataclasses import dataclass

from job_search_rss.domain.subscription_condition import SubscriptionCondition


@dataclass(frozen=True)
class CollectionCondition:
    site_id: str
    condition_key: str

    @classmethod
    def from_subscription_condition(
        cls,
        *,
        site_id: str,
        subscription_condition: SubscriptionCondition,
    ) -> "CollectionCondition":
        return cls(
            site_id=site_id,
            condition_key=subscription_condition.normalized_key.removeprefix(
                "subscription:"
            ),
        )

    @property
    def normalized_key(self) -> str:
        return f"collection:{self.site_id}:{self.condition_key}"

    def has_same_conditions_as(self, other: "CollectionCondition") -> bool:
        return self.normalized_key == other.normalized_key
