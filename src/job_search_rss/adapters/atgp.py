from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlparse

from job_search_rss.domain.condition_values import Region


@dataclass(frozen=True)
class AtgpRegionMaster:
    code: str
    region: Region


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
    values = parse_qs(urlparse(url).query).get(name)
    if not values:
        return None
    return values[0]


def _clean_condition_label(value: str) -> str:
    return value.strip().removesuffix("の求人").strip()
