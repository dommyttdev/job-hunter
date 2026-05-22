from dataclasses import dataclass

from job_search_rss.domain.condition_values import Occupation, Region
from job_search_rss.domain.subscription_condition import SubscriptionCondition
from job_search_rss.usecase.register_subscription_condition import (
    RegisterSubscriptionCondition,
    SubscriptionConditionRepository,
)


@dataclass(frozen=True)
class RegisterSubscriptionInput:
    prefecture: str | None = None
    city: str | None = None
    occupation_category: str | None = None
    occupation_detail: str | None = None


@dataclass(frozen=True)
class RegisterSubscriptionCommandResult:
    subscription_id: str
    rss_path: str


def register_subscription_command(
    command_input: RegisterSubscriptionInput,
    *,
    repository: SubscriptionConditionRepository,
) -> RegisterSubscriptionCommandResult:
    condition = _subscription_condition_from_input(command_input)
    registered = RegisterSubscriptionCondition(repository).execute(condition)
    return RegisterSubscriptionCommandResult(
        subscription_id=registered.id,
        rss_path=f"/rss/{registered.id}",
    )


def _subscription_condition_from_input(
    command_input: RegisterSubscriptionInput,
) -> SubscriptionCondition:
    region = None
    if command_input.prefecture is not None:
        region = Region(prefecture=command_input.prefecture, city=command_input.city)

    occupation = None
    if (
        command_input.occupation_category is not None
        and command_input.occupation_detail is not None
    ):
        occupation = Occupation(
            category=command_input.occupation_category,
            detail=command_input.occupation_detail,
        )

    return SubscriptionCondition(region=region, occupation=occupation)
