from job_search_rss.domain.condition_values import Occupation, Region


def test_region_builds_key_from_prefecture_and_city() -> None:
    region = Region(prefecture="Tokyo", city="Shibuya")

    assert region.prefecture == "Tokyo"
    assert region.city == "Shibuya"
    assert region.normalized_key == "region:tokyo:shibuya"


def test_region_allows_prefecture_only() -> None:
    region = Region(prefecture="Tokyo")

    assert region.normalized_key == "region:tokyo"


def test_occupation_builds_key_from_category_and_detail() -> None:
    occupation = Occupation(category="IT Web", detail="Backend Engineer")

    assert occupation.category == "IT Web"
    assert occupation.detail == "Backend Engineer"
    assert occupation.normalized_key == "occupation:it-web:backend-engineer"
