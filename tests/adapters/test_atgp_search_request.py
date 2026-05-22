from urllib.parse import parse_qs, urlparse

import pytest

from job_search_rss.adapters.atgp import (
    AtgpOccupationMaster,
    AtgpRegionMaster,
    AtgpSearchParameters,
    build_search_url,
    build_search_url_from_parameters,
    build_search_url_from_site_masters,
)
from job_search_rss.domain.collection_condition import CollectionCondition
from job_search_rss.domain.condition_values import Occupation, Region
from job_search_rss.domain.site_master import SiteOccupationMaster, SiteRegionMaster

TOKYO = Region(prefecture="東京都")
ENGINEER = Occupation(category="IT・エンジニア", detail="IT・エンジニア")


def test_build_search_url_from_region_condition() -> None:
    url = build_search_url(
        CollectionCondition(site_id="atgp", condition_key=TOKYO.normalized_key),
        region_masters=[
            AtgpRegionMaster(
                prefecture_code="13",
                city_code=None,
                region=TOKYO,
            )
        ],
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
        region_masters=[
            AtgpRegionMaster(
                prefecture_code="13",
                city_code=None,
                region=TOKYO,
            )
        ],
        occupation_masters=[
            AtgpOccupationMaster(
                job_category_code="b01001610000003000",
                job_type_codes=("b01001630000001000",),
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


def test_build_search_url_from_city_condition_includes_city_and_parent_prefecture() -> None:
    city = Region(prefecture="北海道", city="札幌市中央区")

    url = build_search_url(
        CollectionCondition(site_id="atgp", condition_key=city.normalized_key),
        region_masters=[
            AtgpRegionMaster(
                prefecture_code="1",
                city_code="1101",
                region=city,
            )
        ],
        occupation_masters=[],
    )

    assert parse_qs(urlparse(url).query) == {
        "prefectures": ["1"],
        "cities": ["1101"],
    }


def test_build_search_url_from_collected_site_masters() -> None:
    occupation = Occupation(category="Engineering", detail="Backend")
    condition = CollectionCondition(
        site_id="atgp",
        condition_key=f"{TOKYO.normalized_key}|{occupation.normalized_key}",
    )

    url = build_search_url_from_site_masters(
        condition,
        region_masters=[
            SiteRegionMaster(
                site_id="atgp",
                prefecture_code="13",
                city_code=None,
                region=TOKYO,
            ),
            SiteRegionMaster(
                site_id="other",
                prefecture_code="999",
                city_code=None,
                region=TOKYO,
            ),
        ],
        occupation_masters=[
            SiteOccupationMaster(
                site_id="atgp",
                job_category_code="1",
                job_type_codes=("10", "11"),
                occupation=occupation,
            )
        ],
    )

    assert parse_qs(urlparse(url).query) == {
        "prefectures": ["13"],
        "job_categories": ["1"],
        "job_types": ["10,11"],
    }


def test_build_search_url_from_atgp_search_parameters_supports_multi_value_examples() -> None:
    url = build_search_url_from_parameters(
        AtgpSearchParameters(
            job_category_codes=("b01001610000002000",),
            job_type_codes=("b01001620000003000", "b01001620000004000"),
            city_codes=("3201",),
            prefecture_codes=("2", "3"),
        )
    )

    assert parse_qs(urlparse(url).query) == {
        "job_categories": ["b01001610000002000"],
        "job_types": ["b01001620000003000,b01001620000004000"],
        "cities": ["3201"],
        "prefectures": ["2,3"],
    }
