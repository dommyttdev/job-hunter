from datetime import UTC, datetime

from job_search_rss.domain.history import JobChange, JobChangeType
from job_search_rss.ports.rss_renderer import RssRenderer
from tests.fakes.rss_renderer import FakeRssRenderer


def test_fake_rss_renderer_renders_domain_changes() -> None:
    renderer: RssRenderer = FakeRssRenderer()
    change = JobChange(
        job_id="atgp-001",
        collection_condition_key="collection:atgp:region:tokyo",
        change_type=JobChangeType.NEW,
        content_hash="hash-001",
        occurred_at=datetime(2026, 5, 21, 12, 0, tzinfo=UTC),
    )

    rss = renderer.render_changes([change])

    assert "new" in rss
    assert "atgp-001" in rss
    assert "collection:atgp:region:tokyo" in rss
