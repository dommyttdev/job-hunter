from tests.fakes.repository import FakeRepository

from job_search_rss.domain.condition_values import Occupation, Region
from job_search_rss.domain.site_master import SiteOccupationMaster, SiteRegionMaster
from job_search_rss.usecase.list_site_master import ListSiteMaster


def test_list_site_master_lists_supported_and_synced_sites() -> None:
    repository = FakeRepository()
    repository.save_site_region_master(
        SiteRegionMaster(
            site_id="fake",
            prefecture_code="13",
            city_code=None,
            region=Region(prefecture="Tokyo"),
        )
    )

    assert ListSiteMaster(repository).list_sites() == ["atgp", "fake"]


def test_list_site_master_lists_prefectures_and_cities_for_site() -> None:
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
    repository.save_site_region_master(
        SiteRegionMaster(
            site_id="other",
            prefecture_code="27",
            city_code="27100",
            region=Region(prefecture="Osaka", city="Osaka"),
        )
    )

    usecase = ListSiteMaster(repository)

    assert usecase.list_prefectures(site_id="atgp") == ["Tokyo"]
    assert usecase.list_cities(site_id="atgp", prefecture="Tokyo") == ["Shibuya"]


def test_list_site_master_lists_occupation_categories_and_details_for_site() -> None:
    repository = FakeRepository()
    repository.save_site_occupation_master(
        SiteOccupationMaster(
            site_id="atgp",
            job_category_code="engineering",
            job_type_codes=("backend",),
            occupation=Occupation(category="Engineering", detail="Backend Engineer"),
        )
    )
    repository.save_site_occupation_master(
        SiteOccupationMaster(
            site_id="atgp",
            job_category_code="engineering",
            job_type_codes=("frontend",),
            occupation=Occupation(category="Engineering", detail="Frontend Engineer"),
        )
    )
    repository.save_site_occupation_master(
        SiteOccupationMaster(
            site_id="other",
            job_category_code="sales",
            job_type_codes=("account",),
            occupation=Occupation(category="Sales", detail="Account Executive"),
        )
    )

    usecase = ListSiteMaster(repository)

    assert usecase.list_occupation_categories(site_id="atgp") == ["Engineering"]
    assert usecase.list_occupation_details(site_id="atgp", category="Engineering") == [
        "Backend Engineer",
        "Frontend Engineer",
    ]
