from pytest import CaptureFixture

from job_search_rss.cli import (
    RegisterSubscriptionInput,
    main,
    register_subscription_command,
    run_collection_command,
    sync_site_master_command,
)
from job_search_rss.domain.condition_values import Occupation, Region
from job_search_rss.domain.job import Job
from job_search_rss.domain.subscription_condition import SubscriptionCondition
from job_search_rss.usecase.manage_collection_condition import ManageCollectionCondition
from job_search_rss.usecase.register_subscription_condition import (
    RegisterSubscriptionCondition,
)
from tests.fakes.repository import FakeRepository
from tests.fakes.site_adapter import FakeSiteAdapter


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


def test_run_collection_command_collects_registered_conditions() -> None:
    repository = FakeRepository()
    site_adapter = FakeSiteAdapter()
    RegisterSubscriptionCondition(repository).execute(
        SubscriptionCondition(region=Region(prefecture="Tokyo"))
    )
    collection_condition = ManageCollectionCondition(repository).execute()[0]
    site_adapter.add_job_for_condition(collection_condition, _create_job())

    result = run_collection_command(repository=repository, site_adapter=site_adapter)

    assert result.change_count == 1
    assert result.succeeded_condition_count == 1
    assert result.failed_condition_count == 0
    assert site_adapter.call_count == 1


def test_main_runs_collection_from_argv(capsys: CaptureFixture[str]) -> None:
    repository = FakeRepository()
    site_adapter = FakeSiteAdapter()
    RegisterSubscriptionCondition(repository).execute(
        SubscriptionCondition(region=Region(prefecture="Tokyo"))
    )
    collection_condition = ManageCollectionCondition(repository).execute()[0]
    site_adapter.add_job_for_condition(collection_condition, _create_job())

    exit_code = main(["collect"], repository=repository, site_adapter=site_adapter)

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "change_count=1" in output
    assert "succeeded_condition_count=1" in output


def test_sync_site_master_command_saves_regions_and_occupations() -> None:
    repository = FakeRepository()
    site_adapter = FakeSiteAdapter()
    site_adapter.add_region(Region(prefecture="Tokyo"))
    site_adapter.add_occupation(
        Occupation(category="Engineering", detail="Backend Engineer")
    )

    result = sync_site_master_command(repository=repository, site_adapter=site_adapter)

    assert result.region_count == 1
    assert result.occupation_count == 1
    assert repository.list_regions() == [Region(prefecture="Tokyo")]
    assert repository.list_occupations() == [
        Occupation(category="Engineering", detail="Backend Engineer")
    ]


def test_main_syncs_site_master_from_argv(capsys: CaptureFixture[str]) -> None:
    repository = FakeRepository()
    site_adapter = FakeSiteAdapter()
    site_adapter.add_region(Region(prefecture="Tokyo"))

    exit_code = main(["sync-master"], repository=repository, site_adapter=site_adapter)

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "region_count=1" in output
    assert "occupation_count=0" in output


def _create_job() -> Job:
    return Job(
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
