import pytest

from job_search_rss.adapters.atgp import parse_job_detail, parse_job_list


def test_parse_job_list_fails_when_required_fields_are_missing() -> None:
    html = """
    <article class="job-card" data-job-id="missing-fields">
      <a class="job-title" href="/search/top/search_result_detail/missing-fields">
        Missing fields
      </a>
    </article>
    """

    with pytest.raises(ValueError, match="missing required fields"):
        parse_job_list(html)


def test_parse_job_detail_fails_when_required_fields_are_missing() -> None:
    html = """
    <article class="job-detail" data-job-id="missing-fields">
      <h1>Missing fields</h1>
    </article>
    """

    with pytest.raises(ValueError, match="missing required fields"):
        parse_job_detail(
            html,
            detail_url="https://www.atgp.jp/search/top/search_result_detail/missing-fields",
        )


def test_parse_job_detail_fails_when_detail_article_is_missing() -> None:
    with pytest.raises(ValueError, match="detail was not found"):
        parse_job_detail(
            "<main></main>",
            detail_url="https://www.atgp.jp/search/top/search_result_detail/missing-fields",
        )
