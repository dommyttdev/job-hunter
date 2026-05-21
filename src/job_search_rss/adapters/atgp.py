from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlencode, urlparse

from job_search_rss.domain.collection_condition import CollectionCondition
from job_search_rss.domain.condition_values import Occupation, Region


ATGP_SEARCH_URL = "https://www.atgp.jp/search/top/search_result"


@dataclass(frozen=True)
class AtgpRegionMaster:
    code: str
    region: Region


@dataclass(frozen=True)
class AtgpOccupationMaster:
    category_code: str
    type_codes: tuple[str, ...]
    occupation: Occupation


def parse_region_master(html: str) -> list[AtgpRegionMaster]:
    anchors = _LinkParser.collect_links(html)
    regions: list[AtgpRegionMaster] = []

    for anchor in anchors:
        code = _first_query_value(anchor.href, "prefectures")
        if code is None:
            continue

        label = _clean_condition_label(anchor.text)
        if not label:
            continue

        regions.append(AtgpRegionMaster(code=code, region=Region(prefecture=label)))

    return regions


def parse_occupation_master(html: str) -> list[AtgpOccupationMaster]:
    anchors = _LinkParser.collect_links(html)
    occupations: list[AtgpOccupationMaster] = []

    for anchor in anchors:
        category_code = _first_query_value(anchor.href, "job_categories")
        if category_code is None:
            continue

        label = _clean_condition_label(anchor.text)
        if not label:
            continue

        occupations.append(
            AtgpOccupationMaster(
                category_code=category_code,
                type_codes=tuple(_split_query_values(anchor.href, "job_types")),
                occupation=Occupation(category=label, detail=label),
            )
        )

    return occupations


def build_search_url(
    condition: CollectionCondition,
    *,
    region_masters: list[AtgpRegionMaster],
    occupation_masters: list[AtgpOccupationMaster],
) -> str:
    query: dict[str, str] = {}
    condition_keys = _split_condition_key(condition.condition_key)

    region_key = _find_condition_key(condition_keys, "region:")
    if region_key is not None:
        query["prefectures"] = _region_code_for_key(region_key, region_masters)

    occupation_key = _find_condition_key(condition_keys, "occupation:")
    if occupation_key is not None:
        occupation = _occupation_for_key(occupation_key, occupation_masters)
        query["job_categories"] = occupation.category_code
        if occupation.type_codes:
            query["job_types"] = ",".join(occupation.type_codes)

    if not query:
        msg = "atGP search condition requires region or occupation"
        raise ValueError(msg)

    return f"{ATGP_SEARCH_URL}?{urlencode(query)}"


@dataclass(frozen=True)
class _Anchor:
    href: str
    text: str


class _LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._current_href: str | None = None
        self._current_text_parts: list[str] = []
        self.links: list[_Anchor] = []

    @classmethod
    def collect_links(cls, html: str) -> list[_Anchor]:
        parser = cls()
        parser.feed(html)
        return parser.links

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return

        href = dict(attrs).get("href")
        if href is None:
            return

        self._current_href = href
        self._current_text_parts = []

    def handle_data(self, data: str) -> None:
        if self._current_href is not None:
            self._current_text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or self._current_href is None:
            return

        text = " ".join(part.strip() for part in self._current_text_parts if part.strip())
        self.links.append(_Anchor(href=self._current_href, text=text))
        self._current_href = None
        self._current_text_parts = []


def _first_query_value(url: str, name: str) -> str | None:
    values = _query_values(url, name)
    if not values:
        return None
    return values[0]


def _query_values(url: str, name: str) -> list[str]:
    return parse_qs(urlparse(url).query).get(name, [])


def _split_query_values(url: str, name: str) -> list[str]:
    values: list[str] = []
    for value in _query_values(url, name):
        values.extend(part.strip() for part in value.split(",") if part.strip())
    return values


def _clean_condition_label(value: str) -> str:
    return value.strip().removesuffix("の求人").strip()


def _split_condition_key(condition_key: str) -> list[str]:
    return [part for part in condition_key.split("|") if part]


def _find_condition_key(condition_keys: list[str], prefix: str) -> str | None:
    return next((key for key in condition_keys if key.startswith(prefix)), None)


def _region_code_for_key(region_key: str, masters: list[AtgpRegionMaster]) -> str:
    for master in masters:
        if master.region.normalized_key == region_key:
            return master.code

    msg = f"Unknown atGP region: {region_key}"
    raise ValueError(msg)


def _occupation_for_key(
    occupation_key: str,
    masters: list[AtgpOccupationMaster],
) -> AtgpOccupationMaster:
    for master in masters:
        if master.occupation.normalized_key == occupation_key:
            return master

    msg = f"Unknown atGP occupation: {occupation_key}"
    raise ValueError(msg)
