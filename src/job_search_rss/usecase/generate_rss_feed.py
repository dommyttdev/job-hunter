from typing import Protocol


class ChangeRepository(Protocol):
    def list_changes_for_subscription(self, subscription_id: str) -> list[dict[str, str]]:
        pass


class RssRenderer(Protocol):
    def render(self, changes: list[dict[str, str]]) -> str:
        pass


class GenerateRssFeed:
    def __init__(self, repository: ChangeRepository, renderer: RssRenderer) -> None:
        self._repository = repository
        self._renderer = renderer

    def execute(self, subscription_id: str) -> str:
        changes = self._repository.list_changes_for_subscription(subscription_id)
        return self._renderer.render(changes)
