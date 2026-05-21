from datetime import UTC, datetime
from xml.etree import ElementTree

from job_search_rss.domain.history import JobChangeType
from job_search_rss.rss.renderer import RssItem, XmlRssRenderer


def test_xml_rss_renderer_outputs_expected_item_fields() -> None:
    item = RssItem(
        title="[new] Backend Engineer - Example Inc.",
        link="https://example.test/jobs/atgp-001",
        description="new / Tokyo / Web Engineer / Example Inc.",
        guid="atgp-001:hash-001:new",
        pub_date=datetime(2026, 5, 21, 12, 0, tzinfo=UTC),
        change_type=JobChangeType.NEW,
        region="Tokyo",
        occupation="Web Engineer",
    )

    xml = XmlRssRenderer(
        title="Job Search Changes",
        link="https://example.test/rss",
        description="Latest job posting changes",
    ).render_items([item])
    channel = ElementTree.fromstring(xml).find("channel")
    assert channel is not None
    rss_item = channel.find("item")
    assert rss_item is not None

    assert rss_item.findtext("title") == "[new] Backend Engineer - Example Inc."
    assert rss_item.findtext("link") == "https://example.test/jobs/atgp-001"
    assert rss_item.findtext("description") == "new / Tokyo / Web Engineer / Example Inc."
    assert rss_item.findtext("guid") == "atgp-001:hash-001:new"
    assert rss_item.findtext("category") == "new"
    assert rss_item.findtext("pubDate") == "Thu, 21 May 2026 12:00:00 +0000"
