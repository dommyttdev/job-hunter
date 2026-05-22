from dataclasses import dataclass

from job_search_rss.domain.condition_values import Occupation, Region


@dataclass(frozen=True)
class SiteRegionMaster:
    site_id: str
    prefecture_code: str | None
    city_code: str | None
    region: Region

    @property
    def normalized_key(self) -> str:
        return f"site-region:{self.site_id}:{self.region.normalized_key}"


@dataclass(frozen=True)
class SiteOccupationMaster:
    site_id: str
    job_category_code: str | None
    job_type_codes: tuple[str, ...]
    occupation: Occupation

    @property
    def normalized_key(self) -> str:
        return f"site-occupation:{self.site_id}:{self.occupation.normalized_key}"
