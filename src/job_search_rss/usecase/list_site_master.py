from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

from job_search_rss.domain.site_master import SiteOccupationMaster, SiteRegionMaster

SUPPORTED_SITE_IDS = ("atgp",)


class SiteMasterRepository(Protocol):
    def list_site_region_masters(
        self,
        *,
        site_id: str | None = None,
    ) -> list[SiteRegionMaster]: ...

    def list_site_occupation_masters(
        self,
        *,
        site_id: str | None = None,
    ) -> list[SiteOccupationMaster]: ...


@dataclass(frozen=True)
class ListSiteMaster:
    repository: SiteMasterRepository

    def list_sites(self) -> list[str]:
        site_ids: list[str] = list(SUPPORTED_SITE_IDS)
        site_ids.extend(master.site_id for master in self.repository.list_site_region_masters())
        site_ids.extend(
            master.site_id for master in self.repository.list_site_occupation_masters()
        )
        return _deduplicate(site_ids)

    def list_prefectures(self, *, site_id: str) -> list[str]:
        return _deduplicate(
            master.region.prefecture
            for master in self.repository.list_site_region_masters(site_id=site_id)
        )

    def list_cities(self, *, site_id: str, prefecture: str) -> list[str]:
        return _deduplicate(
            master.region.city
            for master in self.repository.list_site_region_masters(site_id=site_id)
            if master.region.prefecture == prefecture and master.region.city is not None
        )

    def list_occupation_categories(self, *, site_id: str) -> list[str]:
        return _deduplicate(
            master.occupation.category
            for master in self.repository.list_site_occupation_masters(site_id=site_id)
        )

    def list_occupation_details(self, *, site_id: str, category: str) -> list[str]:
        return _deduplicate(
            master.occupation.detail
            for master in self.repository.list_site_occupation_masters(site_id=site_id)
            if master.occupation.category == category
        )


def _deduplicate(values: Iterable[str | None]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value is not None))
