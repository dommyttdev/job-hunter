from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Subscription:
    id: str
    condition_key: str


class SubscriptionRepository(Protocol):
    def add_subscription(
        self,
        *,
        prefecture: str,
        occupation_category: str,
        occupation_detail: str,
    ) -> Subscription: ...


class RegisterSubscriptionCondition:
    def __init__(self, repository: SubscriptionRepository) -> None:
        self._repository = repository

    def execute(
        self,
        *,
        prefecture: str,
        occupation_category: str,
        occupation_detail: str,
    ) -> Subscription:
        return self._repository.add_subscription(
            prefecture=prefecture,
            occupation_category=occupation_category,
            occupation_detail=occupation_detail,
        )
