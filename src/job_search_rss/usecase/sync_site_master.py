from dataclasses import dataclass
from typing import Protocol

from job_search_rss.domain.condition_values import Occupation, Region


class MasterRepository(Protocol):
    def save_region(self, region: Region) -> None: ...

    def list_regions(self) -> list[Region]: ...

    def save_occupation(self, occupation: Occupation) -> None: ...

    def list_occupations(self) -> list[Occupation]: ...


class MasterSiteAdapter(Protocol):
    def list_regions(self) -> list[Region]: ...

    def list_occupations(self) -> list[Occupation]: ...


@dataclass(frozen=True)
class SyncSiteMasterResult:
    region_count: int
    occupation_count: int


class SyncSiteMaster:
    def __init__(self, repository: MasterRepository, site_adapter: MasterSiteAdapter) -> None:
        self._repository = repository
        self._site_adapter = site_adapter

    def execute(self) -> SyncSiteMasterResult:
        for region in self._deduplicate_regions(self._site_adapter.list_regions()):
            self._repository.save_region(region)

        for occupation in self._deduplicate_occupations(
            self._site_adapter.list_occupations()
        ):
            self._repository.save_occupation(occupation)

        return SyncSiteMasterResult(
            region_count=len(self._repository.list_regions()),
            occupation_count=len(self._repository.list_occupations()),
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
