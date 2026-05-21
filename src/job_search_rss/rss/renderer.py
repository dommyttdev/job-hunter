from dataclasses import dataclass
from datetime import datetime
from email.utils import format_datetime
from xml.etree import ElementTree

from job_search_rss.domain.history import JobChangeType


@dataclass(frozen=True)
class RssItem:
    title: str
    link: str
    description: str
    guid: str
    pub_date: datetime
    change_type: JobChangeType
    region: str
    occupation: str


class XmlRssRenderer:
    def __init__(self, *, title: str, link: str, description: str) -> None:
        self._title = title
        self._link = link
        self._description = description

    def render_items(self, items: list[RssItem]) -> str:
        rss = ElementTree.Element("rss", {"version": "2.0"})
        channel = ElementTree.SubElement(rss, "channel")
        _add_text(channel, "title", self._title)
        _add_text(channel, "link", self._link)
        _add_text(channel, "description", self._description)

        for item in items:
            item_element = ElementTree.SubElement(channel, "item")
            _add_text(item_element, "title", item.title)
            _add_text(item_element, "link", item.link)
            _add_text(item_element, "description", item.description)
            _add_text(
                item_element,
                "guid",
                item.guid,
                attributes={"isPermaLink": "false"},
            )
            _add_text(item_element, "pubDate", format_datetime(item.pub_date))
            _add_text(item_element, "category", item.change_type.value)
            _add_text(item_element, "category", item.region)
            _add_text(item_element, "category", item.occupation)

        return ElementTree.tostring(
            rss,
            encoding="utf-8",
            xml_declaration=True,
        ).decode("utf-8")


def _add_text(
    parent: ElementTree.Element,
    tag: str,
    text: str,
    *,
    attributes: dict[str, str] | None = None,
) -> None:
    element = ElementTree.SubElement(parent, tag, attributes or {})
    element.text = text
