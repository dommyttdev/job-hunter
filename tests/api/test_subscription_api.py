from datetime import UTC, datetime
from xml.etree import ElementTree

from fastapi.testclient import TestClient
from tests.fakes.repository import FakeRepository

from job_search_rss.api import create_app
from job_search_rss.domain.condition_values import Occupation, Region
from job_search_rss.domain.history import JobChange, JobChangeType
from job_search_rss.domain.job import Job
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


def test_rss_api_returns_subscription_feed_from_saved_changes() -> None:
    repository = FakeRepository()
    subscription_condition = SubscriptionCondition(region=Region(prefecture="Tokyo"))
    repository.save_subscription_condition(subscription_condition)
    repository.save_job(
        Job(
            job_id="atgp-001",
            site_id="atgp",
            title="Backend Engineer",
            company_name="Example Inc.",
            detail_url="https://example.test/jobs/atgp-001",
            work_location="Tokyo",
            occupation="Web Engineer",
            salary="5,000,000 JPY",
            content_hash="hash-001",
        )
    )
    repository.save_job_change(
        JobChange(
            job_id="atgp-001",
            collection_condition_key="collection:atgp:region:tokyo",
            change_type=JobChangeType.NEW,
            content_hash="hash-001",
            occurred_at=datetime(2026, 5, 21, 12, 0, tzinfo=UTC),
        )
    )
    client = TestClient(create_app(repository=repository))

    response = client.get("/rss/subscription:region:tokyo")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/rss+xml")
    rss_item = ElementTree.fromstring(response.text).find("channel/item")
    assert rss_item is not None
    assert rss_item.findtext("title") == "[new] Backend Engineer - Example Inc."


def test_rss_api_maps_change_type_query_to_rss_filter() -> None:
    repository = FakeRepository()
    subscription_condition = SubscriptionCondition(region=Region(prefecture="Tokyo"))
    repository.save_subscription_condition(subscription_condition)
    repository.save_job(
        Job(
            job_id="atgp-001",
            site_id="atgp",
            title="Backend Engineer",
            company_name="Example Inc.",
            detail_url="https://example.test/jobs/atgp-001",
            work_location="Tokyo",
            occupation="Web Engineer",
            salary="5,000,000 JPY",
            content_hash="hash-002",
        )
    )
    for change_type, content_hash in [
        (JobChangeType.NEW, "hash-001"),
        (JobChangeType.UPDATED, "hash-002"),
    ]:
        repository.save_job_change(
            JobChange(
                job_id="atgp-001",
                collection_condition_key="collection:atgp:region:tokyo",
                change_type=change_type,
                content_hash=content_hash,
                occurred_at=datetime(2026, 5, 21, 12, 0, tzinfo=UTC),
            )
        )
    client = TestClient(create_app(repository=repository))

    response = client.get("/rss/subscription:region:tokyo?change_type=updated")

    rss_items = ElementTree.fromstring(response.text).findall("channel/item")
    assert response.status_code == 200
    assert [item.findtext("title") for item in rss_items] == [
        "[updated] Backend Engineer - Example Inc."
    ]


def test_subscription_api_returns_bad_request_for_empty_condition() -> None:
    repository = FakeRepository()
    client = TestClient(create_app(repository=repository))

    response = client.post("/subscriptions", json={})

    assert response.status_code == 400
    assert response.json() == {"detail": "region or occupation is required"}


def test_rss_api_returns_not_found_for_unknown_subscription() -> None:
    repository = FakeRepository()
    client = TestClient(create_app(repository=repository))

    response = client.get("/rss/subscription:region:tokyo")

    assert response.status_code == 404
    assert response.json() == {"detail": "subscription condition was not found"}
