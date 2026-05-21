from typing import Protocol

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel

from job_search_rss.domain.condition_values import Occupation, Region
from job_search_rss.domain.history import JobChange
from job_search_rss.domain.job import Job
from job_search_rss.domain.subscription_condition import SubscriptionCondition
from job_search_rss.rss.renderer import XmlRssRenderer
from job_search_rss.usecase.generate_rss_feed import GenerateRssFeed
from job_search_rss.usecase.query_job_changes_for_rss import RssChangeQuery
from job_search_rss.usecase.register_subscription_condition import (
    RegisterSubscriptionCondition,
)


class SubscriptionRepository(Protocol):
    def save_subscription_condition(self, condition: SubscriptionCondition) -> None: ...

    def list_subscription_conditions(self) -> list[SubscriptionCondition]: ...

    def list_job_changes(self) -> list[JobChange]: ...

    def list_jobs(self) -> list[Job]: ...


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
    rss_renderer = XmlRssRenderer(
        title="Job Search Changes",
        link="https://example.test/rss",
        description="Latest job changes",
    )

    def register_subscription(request: SubscriptionRequest) -> SubscriptionResponse:
        try:
            condition = _subscription_condition_from_request(request)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
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

    def get_rss(subscription_id: str) -> Response:
        subscription_condition = _find_subscription_condition(repository, subscription_id)
        xml = GenerateRssFeed(repository, rss_renderer).execute(
            RssChangeQuery(subscription_condition=subscription_condition)
        )
        return Response(content=xml, media_type="application/rss+xml")

    app.add_api_route(
        "/rss/{subscription_id}",
        get_rss,
        methods=["GET"],
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


def _find_subscription_condition(
    repository: SubscriptionRepository,
    subscription_id: str,
) -> SubscriptionCondition:
    for condition in repository.list_subscription_conditions():
        if condition.subscription_id == subscription_id:
            return condition

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="subscription condition was not found",
    )
