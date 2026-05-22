from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Any, Protocol, cast
from urllib.parse import parse_qs, urlencode, urljoin, urlparse

from job_search_rss.domain.collection_condition import CollectionCondition
from job_search_rss.domain.condition_values import Occupation, Region
from job_search_rss.domain.job import Job
from job_search_rss.domain.site_master import SiteOccupationMaster, SiteRegionMaster

ATGP_SEARCH_URL = "https://www.atgp.jp/search/top/search_result"
ATGP_BASE_URL = "https://www.atgp.jp"
ATGP_OCCUPATION_MASTER_URL = f"{ATGP_SEARCH_URL}?masters=occupations"
ATGP_DETAIL_URL_TEMPLATE = f"{ATGP_BASE_URL}/search/top/search_result_detail/{{job_id}}"
_REGION_MASTER_EVALUATE_SCRIPT = """
(items) => items.map((item) => {
  const input = item.querySelector(
    'input[name="prefecture"], input[name="prefectures"], input[name="area"]'
  ) || item.querySelector('input[type="checkbox"]');
  const label = labelText(item, input);
  const cities = Array.from(item.querySelectorAll('.modal-select-grand-child-list__item'))
    .map((cityItem) => {
      const cityInput = cityItem.querySelector('input[name="city"]')
        || cityItem.querySelector('input[type="checkbox"]');
      return {
        code: cityInput ? cityInput.value : '',
        label: labelText(cityItem, cityInput),
      };
    })
    .filter((city) => city.code && city.label);
  return {
    code: input ? input.value : '',
    label,
    cities,
  };

  function labelText(root, checkbox) {
    const label = checkbox && checkbox.id
      ? root.querySelector(`label[for="${checkbox.id}"]`)
      : root.querySelector('label');
    return label ? label.textContent.trim() : '';
  }
}).filter((row) => row.code && row.label)
"""
_OCCUPATION_MASTER_EVALUATE_SCRIPT = """
(items) => items.map((item) => {
  const input = item.querySelector(
    'input[name="jobCategory"], input[name="job_categories"], input[name="job_categories[]"]'
  ) || Array.from(item.querySelectorAll('input[type="checkbox"]'))
    .find((checkbox) => checkbox.name !== 'jobType');
  const label = labelText(item, input);
  const children = Array.from(item.querySelectorAll('.modal-select-child-list__item'))
    .map((childItem) => {
      const childInput = childItem.querySelector('input[name="jobType"]')
        || childItem.querySelector('input[type="checkbox"]');
      return {
        code: childInput ? childInput.value : '',
        label: labelText(childItem, childInput),
      };
    })
    .filter((child) => child.code && child.label);
  return {
    code: input ? input.value : '',
    label,
    children,
  };

  function labelText(root, checkbox) {
    const label = checkbox && checkbox.id
      ? root.querySelector(`label[for="${checkbox.id}"]`)
      : root.querySelector('label');
    return label ? label.textContent.trim() : '';
  }
}).filter((row) => row.code && row.label)
"""


class PageClient(Protocol):
    def get_text(self, url: str, *, timeout_seconds: float) -> str: ...


class PageFetcher(Protocol):
    def fetch_page(self, url: str) -> str: ...


class PlaywrightPage(Protocol):
    def goto(self, url: str, *, wait_until: str) -> Any: ...

    def locator(self, selector: str) -> Any: ...


class PlaywrightMasterPageFactory(Protocol):
    def __call__(self) -> PlaywrightPage: ...


class AtgpMasterFetcher(Protocol):
    def fetch_region_masters(self) -> list[AtgpRegionMaster]: ...

    def fetch_occupation_masters(self) -> list[AtgpOccupationMaster]: ...


class AtgpFetchError(RuntimeError):
    pass


@dataclass(frozen=True)
class AtgpRegionMaster:
    prefecture_code: str | None
    city_code: str | None
    region: Region


@dataclass(frozen=True)
class AtgpOccupationMaster:
    job_category_code: str | None
    job_type_codes: tuple[str, ...]
    occupation: Occupation


@dataclass(frozen=True)
class AtgpSearchParameters:
    job_category_codes: tuple[str, ...] = ()
    job_type_codes: tuple[str, ...] = ()
    city_codes: tuple[str, ...] = ()
    prefecture_codes: tuple[str, ...] = ()

    def to_query(self) -> dict[str, str]:
        query: dict[str, str] = {}
        if self.job_category_codes:
            query["job_categories"] = ",".join(self.job_category_codes)
        if self.job_type_codes:
            query["job_types"] = ",".join(self.job_type_codes)
        if self.city_codes:
            query["cities"] = ",".join(self.city_codes)
        if self.prefecture_codes:
            query["prefectures"] = ",".join(self.prefecture_codes)
        return query


class AtgpPageFetcher:
    def __init__(self, client: PageClient, *, timeout_seconds: float = 10.0) -> None:
        self._client = client
        self._timeout_seconds = timeout_seconds

    def fetch_page(self, url: str) -> str:
        try:
            return self._client.get_text(url, timeout_seconds=self._timeout_seconds)
        except Exception as exc:
            msg = f"Failed to fetch atGP page: {url}"
            raise AtgpFetchError(msg) from exc


class AtgpPlaywrightMasterFetcher:
    def __init__(
        self,
        page_factory: PlaywrightMasterPageFactory | None = None,
        *,
        search_url: str = ATGP_SEARCH_URL,
    ) -> None:
        self._page_factory = page_factory or _create_playwright_page
        self._search_url = search_url

    def fetch_region_masters(self) -> list[AtgpRegionMaster]:
        page = self._page_factory()
        try:
            self._open_detail_search(page)
            _click(page, _detail_list_link_selector("エリア・駅"))
            _click_all(page, ".modal-select-child-list__toggle")
            rows = page.locator(".modal-select-child-list__item").evaluate_all(
                _REGION_MASTER_EVALUATE_SCRIPT
            )
            return _region_masters_from_playwright_rows(rows)
        finally:
            _close_playwright_resources(page)

    def fetch_occupation_masters(self) -> list[AtgpOccupationMaster]:
        page = self._page_factory()
        try:
            self._open_detail_search(page)
            _click(page, _detail_list_link_selector("職種"))
            _click_all(page, ".modal-select-list__toggle")
            rows = page.locator(".modal-select-list__item").evaluate_all(
                _OCCUPATION_MASTER_EVALUATE_SCRIPT
            )
            return _occupation_masters_from_playwright_rows(rows)
        finally:
            _close_playwright_resources(page)

    def _open_detail_search(self, page: PlaywrightPage) -> None:
        page.goto(self._search_url, wait_until="domcontentloaded")
        _click(page, "button.c-button.c-button--white.is-change[type='button']")
        page.locator(".modal-box .modal-heading .title").wait_for()


class AtgpSiteAdapter:
    def __init__(
        self,
        fetcher: PageFetcher,
        *,
        master_fetcher: AtgpMasterFetcher | None = None,
        region_master_url: str = ATGP_SEARCH_URL,
        occupation_master_url: str = ATGP_OCCUPATION_MASTER_URL,
    ) -> None:
        self._fetcher = fetcher
        self._master_fetcher = master_fetcher
        self._region_master_url = region_master_url
        self._occupation_master_url = occupation_master_url
        self._region_masters: list[AtgpRegionMaster] | None = None
        self._occupation_masters: list[AtgpOccupationMaster] | None = None

    def add_region(self, region: Region) -> None:
        raise NotImplementedError("atGP adapter reads regions from atGP pages")

    def list_regions(self) -> list[Region]:
        return [master.region for master in self._load_region_masters()]

    def add_occupation(self, occupation: Occupation) -> None:
        raise NotImplementedError("atGP adapter reads occupations from atGP pages")

    def list_occupations(self) -> list[Occupation]:
        return [master.occupation for master in self._load_occupation_masters()]

    def list_site_region_masters(self) -> list[SiteRegionMaster]:
        return [
            SiteRegionMaster(
                site_id="atgp",
                prefecture_code=master.prefecture_code,
                city_code=master.city_code,
                region=master.region,
            )
            for master in self._load_region_masters()
        ]

    def list_site_occupation_masters(self) -> list[SiteOccupationMaster]:
        return [
            SiteOccupationMaster(
                site_id="atgp",
                job_category_code=master.job_category_code,
                job_type_codes=master.job_type_codes,
                occupation=master.occupation,
            )
            for master in self._load_occupation_masters()
        ]

    def add_job_for_condition(self, condition: CollectionCondition, job: Job) -> None:
        raise NotImplementedError("atGP adapter reads jobs from atGP pages")

    def fetch_jobs_for_condition(self, condition: CollectionCondition) -> list[Job]:
        url: str | None = build_search_url(
            condition,
            region_masters=self._load_region_masters(),
            occupation_masters=self._load_occupation_masters(),
        )
        jobs: list[Job] = []

        while url is not None:
            html = self._fetcher.fetch_page(url)
            jobs.extend(parse_job_list(html))
            url = parse_next_page_url(html)

        return jobs

    def fetch_job_detail(self, *, site_id: str, job_id: str) -> Job | None:
        if site_id != "atgp":
            return None

        detail_url = ATGP_DETAIL_URL_TEMPLATE.format(job_id=job_id)
        html = self._fetcher.fetch_page(detail_url)
        return parse_job_detail(html, detail_url=detail_url)

    def _load_region_masters(self) -> list[AtgpRegionMaster]:
        if self._region_masters is None:
            if self._master_fetcher is None:
                self._region_masters = parse_region_master(
                    self._fetcher.fetch_page(self._region_master_url)
                )
            else:
                self._region_masters = self._master_fetcher.fetch_region_masters()
        return self._region_masters

    def _load_occupation_masters(self) -> list[AtgpOccupationMaster]:
        if self._occupation_masters is None:
            if self._master_fetcher is None:
                self._occupation_masters = parse_occupation_master(
                    self._fetcher.fetch_page(self._occupation_master_url)
                )
            else:
                self._occupation_masters = self._master_fetcher.fetch_occupation_masters()
        return self._occupation_masters


def _create_playwright_page() -> PlaywrightPage:
    from playwright.sync_api import sync_playwright

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(locale="ja-JP")
    page = context.new_page()
    return _OwnedPlaywrightPage(
        page=page,
        close_callbacks=[context.close, browser.close, playwright.stop],
    )


class _OwnedPlaywrightPage:
    def __init__(self, *, page: Any, close_callbacks: list[Callable[[], None]]) -> None:
        self._page = page
        self._close_callbacks = close_callbacks

    def goto(self, url: str, *, wait_until: str) -> Any:
        return self._page.goto(url, wait_until=wait_until)

    def locator(self, selector: str) -> Any:
        return self._page.locator(selector)

    def close_resources(self) -> None:
        for close_callback in self._close_callbacks:
            close_callback()


def _click(page: PlaywrightPage, selector: str) -> None:
    locator = page.locator(selector)
    first = getattr(locator, "first", None)
    if callable(first):
        cast(Any, first()).click()
        return
    if first is not None:
        first.click()
        return

    locator.click()


def _click_all(page: PlaywrightPage, selector: str) -> None:
    locator = page.locator(selector)
    count = getattr(locator, "count", None)
    nth = getattr(locator, "nth", None)
    if not callable(count) or not callable(nth):
        locator.click()
        return

    for index in range(cast(int, count())):
        cast(Any, nth(index)).click()


def _close_playwright_resources(page: PlaywrightPage) -> None:
    close_resources = getattr(page, "close_resources", None)
    if callable(close_resources):
        close_resources()


def _detail_list_link_selector(label: str) -> str:
    return f".detail-list__item:has(.detail-list__container__h:text('{label}')) .detail-list__link"


def _region_masters_from_playwright_rows(rows: object) -> list[AtgpRegionMaster]:
    masters: list[AtgpRegionMaster] = []
    for row in _object_list(rows):
        code = _string_from_mapping(row, "code")
        label = _string_from_mapping(row, "label")
        if code and label:
            masters.append(
                AtgpRegionMaster(
                    prefecture_code=code,
                    city_code=None,
                    region=Region(prefecture=label),
                )
            )

        for city in _object_list(row.get("cities")):
            city_code = _string_from_mapping(city, "code")
            city_label = _string_from_mapping(city, "label")
            if city_code and label and city_label:
                masters.append(
                    AtgpRegionMaster(
                        prefecture_code=code,
                        city_code=city_code,
                        region=Region(prefecture=label, city=city_label),
                    )
                )
    return masters


def _occupation_masters_from_playwright_rows(rows: object) -> list[AtgpOccupationMaster]:
    masters: list[AtgpOccupationMaster] = []
    for row in _object_list(rows):
        category_code = _string_from_mapping(row, "code")
        category_label = _string_from_mapping(row, "label")
        for child in _object_list(row.get("children")):
            type_code = _string_from_mapping(child, "code")
            detail_label = _string_from_mapping(child, "label")
            if category_code and category_label and type_code and detail_label:
                masters.append(
                    AtgpOccupationMaster(
                        job_category_code=category_code,
                        job_type_codes=(type_code,),
                        occupation=Occupation(
                            category=category_label,
                            detail=detail_label,
                        ),
                    )
                )
    return masters


def _object_list(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    items: list[dict[str, Any]] = []
    for item in cast(list[object], value):
        if isinstance(item, dict):
            items.append(cast(dict[str, Any], item))
    return items


def _string_from_mapping(mapping: dict[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str):
        return ""
    return _normalize_text(value)


def parse_region_master(html: str) -> list[AtgpRegionMaster]:
    anchors = _LinkParser.collect_links(html)
    regions: list[AtgpRegionMaster] = []

    for anchor in anchors:
        prefecture_code = _first_query_value(anchor.href, "prefectures")
        if prefecture_code is None:
            continue

        label = _clean_condition_label(anchor.text)
        if not label:
            continue

        regions.append(
            AtgpRegionMaster(
                prefecture_code=prefecture_code,
                city_code=None,
                region=Region(prefecture=label),
            )
        )

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
                job_category_code=category_code,
                job_type_codes=tuple(_split_query_values(anchor.href, "job_types")),
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
    prefecture_codes: list[str] = []
    city_codes: list[str] = []
    job_category_codes: list[str] = []
    job_type_codes: list[str] = []
    condition_keys = _split_condition_key(condition.condition_key)

    region_key = _find_condition_key(condition_keys, "region:")
    if region_key is not None:
        region = _region_for_key(region_key, region_masters)
        if region.prefecture_code is not None:
            prefecture_codes.append(region.prefecture_code)
        if region.city_code is not None:
            city_codes.append(region.city_code)

    occupation_key = _find_condition_key(condition_keys, "occupation:")
    if occupation_key is not None:
        occupation = _occupation_for_key(occupation_key, occupation_masters)
        if occupation.job_category_code is not None:
            job_category_codes.append(occupation.job_category_code)
        if occupation.job_type_codes:
            job_type_codes.extend(occupation.job_type_codes)

    query = AtgpSearchParameters(
        job_category_codes=tuple(job_category_codes),
        job_type_codes=tuple(job_type_codes),
        city_codes=tuple(city_codes),
        prefecture_codes=tuple(prefecture_codes),
    ).to_query()
    if not query:
        msg = "atGP search condition requires region or occupation"
        raise ValueError(msg)

    return _build_search_url_from_query(query)


def build_search_url_from_parameters(parameters: AtgpSearchParameters) -> str:
    query = parameters.to_query()
    if not query:
        msg = "atGP search parameters require at least one code"
        raise ValueError(msg)
    return _build_search_url_from_query(query)


def _build_search_url_from_query(query: dict[str, str]) -> str:
    return f"{ATGP_SEARCH_URL}?{urlencode(query)}"


def build_search_url_from_site_masters(
    condition: CollectionCondition,
    *,
    region_masters: list[SiteRegionMaster],
    occupation_masters: list[SiteOccupationMaster],
) -> str:
    if condition.site_id != "atgp":
        msg = f"atGP search URL cannot be built for site: {condition.site_id}"
        raise ValueError(msg)

    atgp_regions = [
        AtgpRegionMaster(
            prefecture_code=master.prefecture_code,
            city_code=master.city_code,
            region=master.region,
        )
        for master in region_masters
        if master.site_id == "atgp"
    ]
    atgp_occupations = [
        AtgpOccupationMaster(
            job_category_code=master.job_category_code,
            job_type_codes=master.job_type_codes,
            occupation=master.occupation,
        )
        for master in occupation_masters
        if master.site_id == "atgp"
    ]
    return build_search_url(
        condition,
        region_masters=atgp_regions,
        occupation_masters=atgp_occupations,
    )


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


def _region_for_key(
    region_key: str,
    masters: list[AtgpRegionMaster],
) -> AtgpRegionMaster:
    for master in masters:
        if master.region.normalized_key == region_key:
            return master

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
