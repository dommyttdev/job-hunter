from tests.fakes.types import JobChangeData


class FakeRssRenderer:
    def render(self, changes: list[JobChangeData]) -> str:
        items = [
            f"{change['change_type']}:{change['title']}:{change['company_name']}"
            for change in changes
        ]
        return "\n".join(items)
