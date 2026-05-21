from dataclasses import dataclass
from typing import Protocol, cast, overload

from job_search_rss.domain.subscription_condition import SubscriptionCondition


@dataclass(frozen=True)
class Subscription:
    id: str
    condition_key: str


@dataclass(frozen=True)
class RegisteredSubscriptionCondition:
    id: str
    condition: SubscriptionCondition


class SubscriptionRepository(Protocol):
    def add_subscription(
        self,
        *,
        prefecture: str,
        occupation_category: str,
        occupation_detail: str,
    ) -> Subscription: ...


class SubscriptionConditionRepository(Protocol):
    def save_subscription_condition(self, condition: SubscriptionCondition) -> None: ...

    def list_subscription_conditions(self) -> list[SubscriptionCondition]: ...


class RegisterSubscriptionCondition:
    def __init__(self, repository: SubscriptionConditionRepository) -> None:
        self._repository = repository

    @overload
    def execute(
        self,
        condition: SubscriptionCondition,
        /,
    ) -> RegisteredSubscriptionCondition: ...

    @overload
    def execute(
        self,
        *,
        prefecture: str,
        occupation_category: str,
        occupation_detail: str,
    ) -> Subscription:
        ...

    def execute(
        self,
        condition: SubscriptionCondition | None = None,
        *,
        prefecture: str | None = None,
        occupation_category: str | None = None,
        occupation_detail: str | None = None,
    ) -> RegisteredSubscriptionCondition | Subscription:
        if condition is not None:
            for existing_condition in self._repository.list_subscription_conditions():
                if existing_condition.has_same_conditions_as(condition):
                    return RegisteredSubscriptionCondition(
                        id=existing_condition.subscription_id,
                        condition=existing_condition,
                    )
            self._repository.save_subscription_condition(condition)
            return RegisteredSubscriptionCondition(
                id=condition.subscription_id,
                condition=condition,
            )
        if (
            prefecture is None
            or occupation_category is None
            or occupation_detail is None
        ):
            msg = "condition or legacy subscription fields are required"
            raise ValueError(msg)
        legacy_repository = cast(SubscriptionRepository, self._repository)
        return legacy_repository.add_subscription(
            prefecture=prefecture,
            occupation_category=occupation_category,
            occupation_detail=occupation_detail,
        )
