from dataclasses import dataclass

from job_search_rss.domain.condition_values import Occupation, Region


@dataclass(frozen=True)
class SubscriptionCondition:
    region: Region | None = None
    occupation: Occupation | None = None

    def __post_init__(self) -> None:
        if self.region is None and self.occupation is None:
            msg = "region or occupation is required"
            raise ValueError(msg)

    @property
    def normalized_key(self) -> str:
        condition_parts: list[str] = []
        if self.region is not None:
            condition_parts.append(self.region.normalized_key)
        if self.occupation is not None:
            condition_parts.append(self.occupation.normalized_key)
        return f"subscription:{'|'.join(condition_parts)}"

    @property
    def subscription_id(self) -> str:
        return self.normalized_key

    def has_same_conditions_as(self, other: "SubscriptionCondition") -> bool:
        return self.normalized_key == other.normalized_key
