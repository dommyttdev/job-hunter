from dataclasses import dataclass
from typing import Protocol

from job_search_rss.domain.condition_values import Occupation, Region
from job_search_rss.domain.site_master import SiteOccupationMaster, SiteRegionMaster


class MasterRepository(Protocol):
    def save_region(self, region: Region) -> None: ...

    def list_regions(self) -> list[Region]: ...

    def save_occupation(self, occupation: Occupation) -> None: ...

    def list_occupations(self) -> list[Occupation]: ...

    def save_site_region_master(self, master: SiteRegionMaster) -> None: ...

    def list_site_region_masters(self, *, site_id: str | None = None) -> list[SiteRegionMaster]: ...

    def save_site_occupation_master(self, master: SiteOccupationMaster) -> None: ...

    def list_site_occupation_masters(
        self,
        *,
        site_id: str | None = None,
    ) -> list[SiteOccupationMaster]: ...


class MasterSiteAdapter(Protocol):
    def list_regions(self) -> list[Region]: ...

    def list_occupations(self) -> list[Occupation]: ...

    def list_site_region_masters(self) -> list[SiteRegionMaster]: ...

    def list_site_occupation_masters(self) -> list[SiteOccupationMaster]: ...


@dataclass(frozen=True)
class SyncSiteMasterResult:
    region_count: int
    occupation_count: int
    site_region_count: int
    site_occupation_count: int


class SyncSiteMaster:
    def __init__(self, repository: MasterRepository, site_adapter: MasterSiteAdapter) -> None:
        self._repository = repository
        self._site_adapter = site_adapter

    def execute(self) -> SyncSiteMasterResult:
        site_region_masters = self._deduplicate_site_region_masters(
            self._site_adapter.list_site_region_masters()
        )
        site_occupation_masters = self._deduplicate_site_occupation_masters(
            self._site_adapter.list_site_occupation_masters()
        )

        for region in self._deduplicate_regions(
            [master.region for master in site_region_masters]
        ):
            self._repository.save_region(region)

        for occupation in self._deduplicate_occupations(
            [master.occupation for master in site_occupation_masters]
        ):
            self._repository.save_occupation(occupation)

        for master in site_region_masters:
            self._repository.save_site_region_master(master)

        for master in site_occupation_masters:
            self._repository.save_site_occupation_master(master)

        return SyncSiteMasterResult(
            region_count=len(self._repository.list_regions()),
            occupation_count=len(self._repository.list_occupations()),
            site_region_count=len(self._repository.list_site_region_masters()),
            site_occupation_count=len(self._repository.list_site_occupation_masters()),
        )

    @staticmethod
    def _deduplicate_regions(regions: list[Region]) -> list[Region]:
        region_by_key = {region.normalized_key: region for region in regions}
        return list(region_by_key.values())

    @staticmethod
    def _deduplicate_occupations(occupations: list[Occupation]) -> list[Occupation]:
        occupation_by_key = {
            occupation.normalized_key: occupation for occupation in occupations
        }
        return list(occupation_by_key.values())

    @staticmethod
    def _deduplicate_site_region_masters(
        masters: list[SiteRegionMaster],
    ) -> list[SiteRegionMaster]:
        master_by_key = {master.normalized_key: master for master in masters}
        return list(master_by_key.values())

    @staticmethod
    def _deduplicate_site_occupation_masters(
        masters: list[SiteOccupationMaster],
    ) -> list[SiteOccupationMaster]:
        master_by_key = {master.normalized_key: master for master in masters}
        return list(master_by_key.values())
