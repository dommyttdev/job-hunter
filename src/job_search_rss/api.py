from typing import Protocol

from fastapi import FastAPI, status
from pydantic import BaseModel

from job_search_rss.domain.condition_values import Occupation, Region
from job_search_rss.domain.subscription_condition import SubscriptionCondition
from job_search_rss.usecase.register_subscription_condition import (
    RegisterSubscriptionCondition,
)


class SubscriptionRepository(Protocol):
    def save_subscription_condition(self, condition: SubscriptionCondition) -> None: ...

    def list_subscription_conditions(self) -> list[SubscriptionCondition]: ...


class RegionRequest(BaseModel):
    prefecture: str
    city: str | None = None


class OccupationRequest(BaseModel):
    category: str
    detail: str


class SubscriptionRequest(BaseModel):
    region: RegionRequest | None = None
    occupation: OccupationRequest | None = None


class SubscriptionResponse(BaseModel):
    subscription_id: str
    rss_url: str


def create_app(*, repository: SubscriptionRepository) -> FastAPI:
    app = FastAPI(title="Job Search RSS")

    def register_subscription(request: SubscriptionRequest) -> SubscriptionResponse:
        condition = _subscription_condition_from_request(request)
        registered = RegisterSubscriptionCondition(repository).execute(condition)
        return SubscriptionResponse(
            subscription_id=registered.id,
            rss_url=f"/rss/{registered.id}",
        )

    app.add_api_route(
        "/subscriptions",
        register_subscription,
        methods=["POST"],
        response_model=SubscriptionResponse,
        status_code=status.HTTP_201_CREATED,
    )
    return app


def _subscription_condition_from_request(request: SubscriptionRequest) -> SubscriptionCondition:
    region = None
    if request.region is not None:
        region = Region(
            prefecture=request.region.prefecture,
            city=request.region.city,
        )

    occupation = None
    if request.occupation is not None:
        occupation = Occupation(
            category=request.occupation.category,
            detail=request.occupation.detail,
        )

    return SubscriptionCondition(region=region, occupation=occupation)
