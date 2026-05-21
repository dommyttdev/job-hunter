from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlencode, urljoin, urlparse

from job_search_rss.domain.collection_condition import CollectionCondition
from job_search_rss.domain.condition_values import Occupation, Region
from job_search_rss.domain.job import Job


ATGP_SEARCH_URL = "https://www.atgp.jp/search/top/search_result"
ATGP_BASE_URL = "https://www.atgp.jp"


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


def parse_job_list(html: str) -> list[Job]:
    cards = _JobCardParser.collect_cards(html)
    return [_job_from_card(card) for card in cards]


def parse_next_page_url(html: str) -> str | None:
    links = _ClassedLinkParser.collect_links(html)
    for link in links:
        if "next" in link.class_names:
            return urljoin(ATGP_BASE_URL, link.href)
    return None


def parse_job_detail(html: str, *, detail_url: str) -> Job:
    detail = _JobDetailParser.collect_detail(html)
    if detail is None:
        msg = "atGP job detail was not found"
        raise ValueError(msg)

    return Job(
        job_id=detail.job_id,
        site_id="atgp",
        title=detail.title,
        company_name=detail.company_name,
        detail_url=detail_url,
        work_location=detail.work_location,
        occupation=detail.occupation,
        salary=detail.salary,
        content_hash=Job.generate_content_hash(
            title=detail.title,
            company_name=detail.company_name,
            detail_url=detail_url,
            work_location=detail.work_location,
            occupation=detail.occupation,
            salary=detail.salary,
            description=detail.description,
        ),
    )


@dataclass(frozen=True)
class _Anchor:
    href: str
    text: str


@dataclass(frozen=True)
class _ClassedAnchor:
    href: str
    text: str
    class_names: frozenset[str]


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


class _ClassedLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._current_href: str | None = None
        self._current_class_names: frozenset[str] = frozenset()
        self._current_text_parts: list[str] = []
        self.links: list[_ClassedAnchor] = []

    @classmethod
    def collect_links(cls, html: str) -> list[_ClassedAnchor]:
        parser = cls()
        parser.feed(html)
        return parser.links

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return

        attr_map = dict(attrs)
        href = attr_map.get("href")
        if href is None:
            return

        self._current_href = href
        self._current_class_names = frozenset(_class_names(attr_map.get("class")))
        self._current_text_parts = []

    def handle_data(self, data: str) -> None:
        if self._current_href is not None:
            self._current_text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or self._current_href is None:
            return

        text = _normalize_text(" ".join(self._current_text_parts))
        self.links.append(
            _ClassedAnchor(
                href=self._current_href,
                text=text,
                class_names=self._current_class_names,
            )
        )
        self._current_href = None
        self._current_class_names = frozenset()
        self._current_text_parts = []


@dataclass(frozen=True)
class _JobCard:
    job_id: str
    title: str
    company_name: str
    detail_url: str
    work_location: str
    occupation: str
    salary: str


class _JobCardParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._current: dict[str, str] | None = None
        self._text_target: str | None = None
        self._text_parts: list[str] = []
        self._pending_definition_label: str | None = None
        self.cards: list[_JobCard] = []

    @classmethod
    def collect_cards(cls, html: str) -> list[_JobCard]:
        parser = cls()
        parser.feed(html)
        return parser.cards

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        class_names = _class_names(attr_map.get("class"))

        if tag == "article" and "job-card" in class_names:
            self._current = {"job_id": attr_map.get("data-job-id", "") or ""}
            return

        if self._current is None:
            return

        if tag == "a" and "job-title" in class_names:
            self._current["detail_url"] = urljoin(ATGP_BASE_URL, attr_map.get("href", "") or "")
            self._start_text("title")
            return

        if tag == "h2" and "company-name" in class_names:
            self._start_text("company_name")
            return

        if tag == "dt":
            self._start_text("_definition_label")
            return

        if tag == "dd":
            self._start_text("_definition_value")

    def handle_data(self, data: str) -> None:
        if self._text_target is not None:
            self._text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._current is None:
            return

        if tag == "article":
            self.cards.append(_card_from_values(self._current))
            self._current = None
            return

        if tag in {"a", "h2", "dt", "dd"} and self._text_target is not None:
            self._finish_text()

    def _start_text(self, target: str) -> None:
        self._text_target = target
        self._text_parts = []

    def _finish_text(self) -> None:
        if self._current is None or self._text_target is None:
            return

        text = _normalize_text(" ".join(self._text_parts))
        target = self._text_target
        self._text_target = None
        self._text_parts = []

        if target == "_definition_label":
            self._pending_definition_label = text
            return

        if target == "_definition_value":
            self._store_definition_value(text)
            return

        self._current[target] = text

    def _store_definition_value(self, text: str) -> None:
        if self._current is None:
            return

        match self._pending_definition_label:
            case "職種":
                self._current["occupation"] = text
            case "勤務地":
                self._current["work_location"] = text
            case "給与":
                self._current["salary"] = text
            case _:
                pass

        self._pending_definition_label = None


@dataclass(frozen=True)
class _JobDetail:
    job_id: str
    title: str
    company_name: str
    work_location: str
    occupation: str
    salary: str
    description: str


class _JobDetailParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._current: dict[str, str] | None = None
        self._text_target: str | None = None
        self._text_parts: list[str] = []
        self._pending_definition_label: str | None = None
        self.detail: _JobDetail | None = None

    @classmethod
    def collect_detail(cls, html: str) -> _JobDetail | None:
        parser = cls()
        parser.feed(html)
        return parser.detail

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        class_names = _class_names(attr_map.get("class"))

        if tag == "article" and "job-detail" in class_names:
            self._current = {"job_id": attr_map.get("data-job-id", "") or ""}
            return

        if self._current is None:
            return

        if tag == "h1":
            self._start_text("title")
            return

        if tag == "p" and "company-name" in class_names:
            self._start_text("company_name")
            return

        if tag == "dt":
            self._start_text("_definition_label")
            return

        if tag == "dd":
            self._start_text("_definition_value")

    def handle_data(self, data: str) -> None:
        if self._text_target is not None:
            self._text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._current is None:
            return

        if tag == "article":
            self.detail = _detail_from_values(self._current)
            self._current = None
            return

        if tag in {"h1", "p", "dt", "dd"} and self._text_target is not None:
            self._finish_text()

    def _start_text(self, target: str) -> None:
        self._text_target = target
        self._text_parts = []

    def _finish_text(self) -> None:
        if self._current is None or self._text_target is None:
            return

        text = _normalize_text(" ".join(self._text_parts))
        target = self._text_target
        self._text_target = None
        self._text_parts = []

        if target == "_definition_label":
            self._pending_definition_label = text
            return

        if target == "_definition_value":
            self._store_definition_value(text)
            return

        self._current[target] = text

    def _store_definition_value(self, text: str) -> None:
        if self._current is None:
            return

        match self._pending_definition_label:
            case "職種":
                self._current["occupation"] = text
            case "勤務地":
                self._current["work_location"] = text
            case "給与":
                self._current["salary"] = text
            case "仕事内容":
                self._current["description"] = text
            case _:
                pass

        self._pending_definition_label = None


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


def _normalize_text(value: str) -> str:
    return " ".join(value.split())


def _class_names(value: str | None) -> set[str]:
    if value is None:
        return set()
    return set(value.split())


def _card_from_values(values: dict[str, str]) -> _JobCard:
    required_fields = [
        "job_id",
        "title",
        "company_name",
        "detail_url",
        "work_location",
        "occupation",
        "salary",
    ]
    missing_fields = [field for field in required_fields if not values.get(field)]
    if missing_fields:
        msg = f"atGP job card is missing required fields: {', '.join(missing_fields)}"
        raise ValueError(msg)

    return _JobCard(
        job_id=values["job_id"],
        title=values["title"],
        company_name=values["company_name"],
        detail_url=values["detail_url"],
        work_location=values["work_location"],
        occupation=values["occupation"],
        salary=values["salary"],
    )


def _job_from_card(card: _JobCard) -> Job:
    return Job(
        job_id=card.job_id,
        site_id="atgp",
        title=card.title,
        company_name=card.company_name,
        detail_url=card.detail_url,
        work_location=card.work_location,
        occupation=card.occupation,
        salary=card.salary,
        content_hash=Job.generate_content_hash(
            title=card.title,
            company_name=card.company_name,
            detail_url=card.detail_url,
            work_location=card.work_location,
            occupation=card.occupation,
            salary=card.salary,
            description="",
        ),
    )


def _detail_from_values(values: dict[str, str]) -> _JobDetail:
    required_fields = [
        "job_id",
        "title",
        "company_name",
        "work_location",
        "occupation",
        "salary",
        "description",
    ]
    missing_fields = [field for field in required_fields if not values.get(field)]
    if missing_fields:
        msg = f"atGP job detail is missing required fields: {', '.join(missing_fields)}"
        raise ValueError(msg)

    return _JobDetail(
        job_id=values["job_id"],
        title=values["title"],
        company_name=values["company_name"],
        work_location=values["work_location"],
        occupation=values["occupation"],
        salary=values["salary"],
        description=values["description"],
    )


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
