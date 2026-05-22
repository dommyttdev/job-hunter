from pytest import CaptureFixture
from tests.fakes.repository import FakeRepository

from job_search_rss.cli import RegisterSubscriptionInput, main, register_subscription_command


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


def test_main_registers_subscription_from_argv(
    capsys: CaptureFixture[str],
) -> None:
    repository = FakeRepository()

    exit_code = main(
        [
            "subscribe",
            "--prefecture",
            "Tokyo",
            "--occupation-category",
            "Engineering",
            "--occupation-detail",
            "Backend Engineer",
        ],
        repository=repository,
    )

    assert exit_code == 0
    assert "subscription:region:tokyo|occupation:engineering:backend-engineer" in (
        capsys.readouterr().out
    )
    assert [
        condition.normalized_key for condition in repository.list_subscription_conditions()
    ] == ["subscription:region:tokyo|occupation:engineering:backend-engineer"]
