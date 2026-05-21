from urllib.parse import parse_qs, urlparse

import pytest

from job_search_rss.adapters.atgp import (
    AtgpOccupationMaster,
    AtgpRegionMaster,
    build_search_url,
)
from job_search_rss.domain.collection_condition import CollectionCondition
from job_search_rss.domain.condition_values import Occupation, Region

TOKYO = Region(prefecture="東京都")
ENGINEER = Occupation(category="IT・エンジニア", detail="IT・エンジニア")


def test_build_search_url_from_region_condition() -> None:
    url = build_search_url(
        CollectionCondition(site_id="atgp", condition_key=TOKYO.normalized_key),
        region_masters=[AtgpRegionMaster(code="13", region=TOKYO)],
        occupation_masters=[],
    )

    parsed = urlparse(url)

    assert parsed.scheme == "https"
    assert parsed.netloc == "www.atgp.jp"
    assert parsed.path == "/search/top/search_result"
    assert parse_qs(parsed.query) == {"prefectures": ["13"]}


def test_build_search_url_from_region_and_occupation_condition() -> None:
    url = build_search_url(
        CollectionCondition(
            site_id="atgp",
            condition_key=f"{TOKYO.normalized_key}|{ENGINEER.normalized_key}",
        ),
        region_masters=[AtgpRegionMaster(code="13", region=TOKYO)],
        occupation_masters=[
            AtgpOccupationMaster(
                category_code="b01001610000003000",
                type_codes=("b01001630000001000",),
                occupation=ENGINEER,
            )
        ],
    )

    assert parse_qs(urlparse(url).query) == {
        "prefectures": ["13"],
        "job_categories": ["b01001610000003000"],
        "job_types": ["b01001630000001000"],
    }


def test_build_search_url_rejects_unknown_master_mapping() -> None:
    with pytest.raises(ValueError, match="Unknown atGP region"):
        build_search_url(
            CollectionCondition(site_id="atgp", condition_key=TOKYO.normalized_key),
            region_masters=[],
            occupation_masters=[],
        )
