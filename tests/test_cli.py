from tests.fakes.repository import FakeRepository

from job_search_rss.cli import RegisterSubscriptionInput, register_subscription_command


def test_register_subscription_command_registers_condition_without_http() -> None:
    repository = FakeRepository()

    result = register_subscription_command(
        RegisterSubscriptionInput(
            prefecture="Tokyo",
            city="Shibuya",
            occupation_category="Engineering",
            occupation_detail="Backend Engineer",
        ),
        repository=repository,
    )

    assert result.subscription_id == (
        "subscription:region:tokyo:shibuya|occupation:engineering:backend-engineer"
    )
    assert result.rss_path == (
        "/rss/subscription:region:tokyo:shibuya|occupation:engineering:backend-engineer"
    )
    assert [
        condition.normalized_key for condition in repository.list_subscription_conditions()
    ] == ["subscription:region:tokyo:shibuya|occupation:engineering:backend-engineer"]
