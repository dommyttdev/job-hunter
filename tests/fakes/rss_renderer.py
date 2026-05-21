class FakeRssRenderer:
    def render(self, changes: list[dict[str, str]]) -> str:
        items = [
            f"{change['change_type']}:{change['title']}:{change['company_name']}"
            for change in changes
        ]
        return "\n".join(items)
