from tests.fakes.repository import FakeRepository
from tests.fakes.site_adapter import FakeSiteAdapter

from job_search_rss.domain.condition_values import Occupation, Region
from job_search_rss.domain.site_master import SiteOccupationMaster, SiteRegionMaster
from job_search_rss.usecase.sync_site_master import SyncSiteMaster


def test_sync_site_master_saves_regions_and_occupations_from_site_adapter() -> None:
    repository = FakeRepository()
    site_adapter = FakeSiteAdapter()
    site_adapter.add_region(Region(prefecture="Tokyo"))
    site_adapter.add_occupation(Occupation(category="IT Web", detail="Backend Engineer"))

    result = SyncSiteMaster(repository, site_adapter).execute()

    assert result.region_count == 1
    assert result.occupation_count == 1
    assert result.site_region_count == 1
    assert result.site_occupation_count == 1
    assert repository.list_regions() == [Region(prefecture="Tokyo")]
    assert repository.list_occupations() == [
        Occupation(category="IT Web", detail="Backend Engineer")
    ]
    assert repository.list_site_region_masters() == [
        SiteRegionMaster(
            site_id="fake",
            prefecture_code="1",
            city_code=None,
            region=Region(prefecture="Tokyo"),
        )
    ]
    assert repository.list_site_occupation_masters() == [
        SiteOccupationMaster(
            site_id="fake",
            job_category_code="category-1",
            job_type_codes=("type-1",),
            occupation=Occupation(category="IT Web", detail="Backend Engineer"),
        )
    ]


def test_sync_site_master_deduplicates_normalized_master_values() -> None:
    repository = FakeRepository()
    site_adapter = FakeSiteAdapter()
    site_adapter.add_region(Region(prefecture=" Tokyo "))
    site_adapter.add_region(Region(prefecture="tokyo"))
    site_adapter.add_occupation(Occupation(category="IT Web", detail="Backend Engineer"))
    site_adapter.add_occupation(Occupation(category="it   web", detail="backend engineer"))

    result = SyncSiteMaster(repository, site_adapter).execute()

    assert result.region_count == 1
    assert result.occupation_count == 1
    assert result.site_region_count == 1
    assert result.site_occupation_count == 1
    assert repository.list_regions() == [Region(prefecture="tokyo")]
    assert repository.list_occupations() == [
        Occupation(category="it   web", detail="backend engineer")
    ]
