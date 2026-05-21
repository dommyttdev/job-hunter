import pytest

from job_search_rss.adapters.atgp import AtgpFetchError, AtgpPageFetcher


class FakePageClient:
    def __init__(self, pages: dict[str, str] | None = None, error: Exception | None = None) -> None:
        self.pages = pages or {}
        self.error = error
        self.calls: list[tuple[str, float]] = []

    def get_text(self, url: str, *, timeout_seconds: float) -> str:
        self.calls.append((url, timeout_seconds))
        if self.error is not None:
            raise self.error
        return self.pages[url]


def test_page_fetcher_returns_text_from_client() -> None:
    client = FakePageClient({"https://example.test/list": "<html>ok</html>"})
    fetcher = AtgpPageFetcher(client, timeout_seconds=3.5)

    html = fetcher.fetch_page("https://example.test/list")

    assert html == "<html>ok</html>"
    assert client.calls == [("https://example.test/list", 3.5)]


def test_page_fetcher_wraps_client_errors() -> None:
    client = FakePageClient(error=TimeoutError("timeout"))
    fetcher = AtgpPageFetcher(client)

    with pytest.raises(AtgpFetchError, match="Failed to fetch atGP page"):
        fetcher.fetch_page("https://example.test/list")
