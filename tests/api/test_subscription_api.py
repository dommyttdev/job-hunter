from fastapi.testclient import TestClient
from tests.fakes.repository import FakeRepository

from job_search_rss.api import create_app
from job_search_rss.domain.condition_values import Occupation, Region
from job_search_rss.domain.subscription_condition import SubscriptionCondition


def test_subscription_api_registers_condition_and_returns_rss_url() -> None:
    repository = FakeRepository()
    client = TestClient(create_app(repository=repository))

    response = client.post(
        "/subscriptions",
        json={
            "region": {"prefecture": "Tokyo"},
            "occupation": {"category": "IT Web", "detail": "Backend Engineer"},
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "subscription_id": "subscription:region:tokyo|occupation:it-web:backend-engineer",
        "rss_url": "/rss/subscription:region:tokyo|occupation:it-web:backend-engineer",
    }
    assert repository.list_subscription_conditions() == [
        SubscriptionCondition(
            region=Region(prefecture="Tokyo"),
            occupation=Occupation(category="IT Web", detail="Backend Engineer"),
        )
    ]
