# pyright: reportPrivateUsage=false

import pytest
from pytest import CaptureFixture, MonkeyPatch

from job_search_rss.adapters.atgp import AtgpPlaywrightMasterFetcher, AtgpSiteAdapter
from job_search_rss.cli import (
    RegisterSubscriptionInput,
    _create_site_adapter_from_settings,
    list_occupations_command,
    list_regions_command,
    list_sites_command,
    main,
    register_subscription_command,
    run_collection_command,
    sync_site_master_command,
)
from job_search_rss.domain.condition_values import Occupation, Region
from job_search_rss.domain.job import Job
from job_search_rss.domain.site_master import SiteOccupationMaster, SiteRegionMaster
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


def test_register_subscription_command_accepts_occupation_category_only() -> None:
    repository = FakeRepository()

    result = register_subscription_command(
        RegisterSubscriptionInput(
            prefecture="福岡県",
            occupation_category="IT・エンジニア関連",
        ),
        repository=repository,
    )

    assert result.subscription_id == (
        "subscription:region:福岡県|occupation:it・エンジニア関連:it・エンジニア関連"
    )
    assert [
        condition.normalized_key for condition in repository.list_subscription_conditions()
    ] == [
        "subscription:region:福岡県|occupation:it・エンジニア関連:it・エンジニア関連"
    ]


def test_register_subscription_command_rejects_occupation_detail_only() -> None:
    repository = FakeRepository()

    with pytest.raises(
        ValueError,
        match="--occupation-category is required",
    ):
        register_subscription_command(
            RegisterSubscriptionInput(
                prefecture="福岡県",
                occupation_detail="Webエンジニア",
            ),
            repository=repository,
        )


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


def test_list_sites_command_includes_supported_site_without_http() -> None:
    repository = FakeRepository()

    result = list_sites_command(repository=repository)

    assert result.items == ("atgp",)


def test_list_regions_command_lists_prefectures_or_cities() -> None:
    repository = FakeRepository()
    repository.save_site_region_master(
        SiteRegionMaster(
            site_id="atgp",
            prefecture_code="13",
            city_code=None,
            region=Region(prefecture="Tokyo"),
        )
    )
    repository.save_site_region_master(
        SiteRegionMaster(
            site_id="atgp",
            prefecture_code="13",
            city_code="13113",
            region=Region(prefecture="Tokyo", city="Shibuya"),
        )
    )

    assert list_regions_command(repository=repository, site_id="atgp").items == ("Tokyo",)
    assert list_regions_command(
        repository=repository,
        site_id="atgp",
        prefecture="Tokyo",
    ).items == ("Shibuya",)


def test_list_occupations_command_lists_categories_or_details() -> None:
    repository = FakeRepository()
    repository.save_site_occupation_master(
        SiteOccupationMaster(
            site_id="atgp",
            job_category_code="engineering",
            job_type_codes=("backend",),
            occupation=Occupation(category="Engineering", detail="Backend Engineer"),
        )
    )

    assert list_occupations_command(repository=repository, site_id="atgp").items == (
        "Engineering",
    )
    assert list_occupations_command(
        repository=repository,
        site_id="atgp",
        category="Engineering",
    ).items == ("Backend Engineer",)


def test_main_lists_master_values_from_argv(capsys: CaptureFixture[str]) -> None:
    repository = FakeRepository()
    repository.save_site_region_master(
        SiteRegionMaster(
            site_id="atgp",
            prefecture_code="13",
            city_code="13113",
            region=Region(prefecture="Tokyo", city="Shibuya"),
        )
    )

    exit_code = main(
        ["list-regions", "--site", "atgp", "--prefecture", "Tokyo"],
        repository=repository,
    )

    assert exit_code == 0
    assert capsys.readouterr().out == "Shibuya\n"


def test_create_site_adapter_from_settings_uses_playwright_master_fetcher(
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setenv("JOB_SEARCH_RSS_ALLOW_EXTERNAL_ACCESS", "true")

    site_adapter = _create_site_adapter_from_settings()

    assert isinstance(site_adapter, AtgpSiteAdapter)
    assert isinstance(site_adapter._master_fetcher, AtgpPlaywrightMasterFetcher)


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
