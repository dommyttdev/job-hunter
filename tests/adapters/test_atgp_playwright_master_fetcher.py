from collections.abc import Callable

from job_search_rss.adapters.atgp import (
    ATGP_SEARCH_URL,
    AtgpOccupationMaster,
    AtgpPlaywrightMasterFetcher,
    AtgpRegionMaster,
)
from job_search_rss.domain.condition_values import Occupation, Region


def test_playwright_master_fetcher_collects_prefectures_and_cities_from_modal() -> None:
    page = FakePage(
        evaluate_results={
            ".modal-select-child-list__item": [
                {
                    "code": "1",
                    "label": "北海道",
                    "cities": [
                        {"code": "1101", "label": "札幌市中央区"},
                        {"code": "1102", "label": "札幌市北区"},
                    ],
                },
                {
                    "code": "13",
                    "label": "東京都",
                    "cities": [
                        {"code": "13101", "label": "千代田区"},
                    ],
                },
            ],
        },
        locator_counts={
            "button.c-button.c-button--white.is-change[type='button']": 1,
            ".modal-select-child-list__toggle": 2,
        },
    )
    fetcher = AtgpPlaywrightMasterFetcher(lambda: page)

    regions = fetcher.fetch_region_masters()

    assert page.goto_urls == [ATGP_SEARCH_URL]
    assert page.clicked_selectors == [
        "button.c-button.c-button--white.is-change[type='button']",
        ".detail-list__item:has(.detail-list__container__h:text('エリア・駅')) .detail-list__link",
        ".modal-select-child-list__toggle",
        ".modal-select-child-list__toggle",
    ]
    assert regions == [
        AtgpRegionMaster(code="1", region=Region(prefecture="北海道")),
        AtgpRegionMaster(code="1101", region=Region(prefecture="北海道", city="札幌市中央区")),
        AtgpRegionMaster(code="1102", region=Region(prefecture="北海道", city="札幌市北区")),
        AtgpRegionMaster(code="13", region=Region(prefecture="東京都")),
        AtgpRegionMaster(code="13101", region=Region(prefecture="東京都", city="千代田区")),
    ]


def test_playwright_master_fetcher_collects_occupation_categories_and_details_from_modal() -> None:
    page = FakePage(
        evaluate_results={
            ".modal-select-list__item": [
                {
                    "code": "b01001610000003000",
                    "label": "IT・エンジニア",
                    "children": [
                        {"code": "b01001630000001000", "label": "社内SE"},
                        {"code": "b01001630000002000", "label": "Webエンジニア"},
                    ],
                },
                {
                    "code": "b01001610000004000",
                    "label": "事務関連",
                    "children": [
                        {"code": "b01001640000001000", "label": "一般事務"},
                    ],
                },
            ],
        },
        locator_counts={
            "button.c-button.c-button--white.is-change[type='button']": 1,
            ".modal-select-list__toggle": 2,
        },
    )
    fetcher = AtgpPlaywrightMasterFetcher(lambda: page)

    occupations = fetcher.fetch_occupation_masters()

    assert page.goto_urls == [ATGP_SEARCH_URL]
    assert page.clicked_selectors == [
        "button.c-button.c-button--white.is-change[type='button']",
        ".detail-list__item:has(.detail-list__container__h:text('職種')) .detail-list__link",
        ".modal-select-list__toggle",
        ".modal-select-list__toggle",
    ]
    assert occupations == [
        AtgpOccupationMaster(
            category_code="b01001610000003000",
            type_codes=("b01001630000001000",),
            occupation=Occupation(category="IT・エンジニア", detail="社内SE"),
        ),
        AtgpOccupationMaster(
            category_code="b01001610000003000",
            type_codes=("b01001630000002000",),
            occupation=Occupation(category="IT・エンジニア", detail="Webエンジニア"),
        ),
        AtgpOccupationMaster(
            category_code="b01001610000004000",
            type_codes=("b01001640000001000",),
            occupation=Occupation(category="事務関連", detail="一般事務"),
        ),
    ]


class FakePage:
    def __init__(
        self,
        *,
        evaluate_results: dict[str, object],
        locator_counts: dict[str, int] | None = None,
    ) -> None:
        self.goto_urls: list[str] = []
        self.clicked_selectors: list[str] = []
        self._evaluate_results = evaluate_results
        self._locator_counts = locator_counts or {}

    def goto(self, url: str, *, wait_until: str) -> None:
        self.goto_urls.append(url)

    def locator(self, selector: str) -> "FakeLocator":
        return FakeLocator(
            selector=selector,
            on_click=self.clicked_selectors.append,
            evaluate_results=self._evaluate_results,
            count=self._locator_counts.get(selector),
        )


class FakeLocator:
    def __init__(
        self,
        *,
        selector: str,
        on_click: Callable[[str], None],
        evaluate_results: dict[str, object],
        count: int | None = None,
    ) -> None:
        self._selector = selector
        self._on_click = on_click
        self._evaluate_results = evaluate_results
        self._count = count

    def click(self) -> None:
        self._on_click(self._selector)

    def wait_for(self) -> None:
        return None

    def evaluate_all(self, expression: str) -> object:
        return self._evaluate_results[self._selector]

    def count(self) -> int:
        if self._count is None:
            raise AssertionError("count was not configured")
        return self._count

    def nth(self, index: int) -> "FakeLocator":
        return FakeLocator(
            selector=self._selector,
            on_click=self._on_click,
            evaluate_results=self._evaluate_results,
        )

    @property
    def first(self) -> "FakeLocator":
        return FakeLocator(
            selector=self._selector,
            on_click=self._on_click,
            evaluate_results=self._evaluate_results,
        )
