from pathlib import Path

from job_search_rss.adapters.atgp import AtgpRegionMaster, parse_region_master
from job_search_rss.domain.condition_values import Region

FIXTURE_DIR = Path(__file__).parents[1] / "fixtures" / "atgp"


def test_parse_region_master_converts_atgp_links_to_regions() -> None:
    html = (FIXTURE_DIR / "region_master.html").read_text(encoding="utf-8")

    regions = parse_region_master(html)

    assert regions == [
        AtgpRegionMaster(
            prefecture_code="13",
            city_code=None,
            region=Region(prefecture="東京都"),
        ),
        AtgpRegionMaster(
            prefecture_code="14",
            city_code=None,
            region=Region(prefecture="神奈川県"),
        ),
        AtgpRegionMaster(
            prefecture_code="27",
            city_code=None,
            region=Region(prefecture="大阪府"),
        ),
    ]
