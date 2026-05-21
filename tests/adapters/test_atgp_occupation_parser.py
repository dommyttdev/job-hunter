from pathlib import Path

from job_search_rss.adapters.atgp import AtgpOccupationMaster, parse_occupation_master
from job_search_rss.domain.condition_values import Occupation


FIXTURE_DIR = Path(__file__).parents[1] / "fixtures" / "atgp"


def test_parse_occupation_master_converts_atgp_links_to_occupations() -> None:
    html = (FIXTURE_DIR / "occupation_master.html").read_text(encoding="utf-8")

    occupations = parse_occupation_master(html)

    assert occupations == [
        AtgpOccupationMaster(
            category_code="b01001610000002000",
            type_codes=("b01001620000003000", "b01001620000004000"),
            occupation=Occupation(category="事務関連", detail="事務関連"),
        ),
        AtgpOccupationMaster(
            category_code="b01001610000003000",
            type_codes=("b01001630000001000",),
            occupation=Occupation(category="IT・エンジニア", detail="IT・エンジニア"),
        ),
    ]
