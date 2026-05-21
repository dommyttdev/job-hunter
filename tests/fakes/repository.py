from job_search_rss.usecase.register_subscription_condition import Subscription
from tests.fakes.site_adapter import FakeSiteAdapter
from tests.fakes.types import JobChangeData


class FakeRepository:
    def __init__(self) -> None:
        self._subscriptions: dict[str, Subscription] = {}
        self._changes_by_subscription: dict[str, list[JobChangeData]] = {}

    def add_subscription(
        self,
        *,
        prefecture: str,
        occupation_category: str,
        occupation_detail: str,
    ) -> Subscription:
        condition_key = self._condition_key(prefecture, occupation_detail)
        subscription = Subscription(
            id=f"subscription-{len(self._subscriptions) + 1}",
            condition_key=condition_key,
        )
        self._subscriptions[subscription.id] = subscription
        self._changes_by_subscription.setdefault(subscription.id, [])
        return subscription

    def collect_jobs_for_subscription(
        self, subscription_id: str, site_adapter: FakeSiteAdapter
    ) -> None:
        subscription = self._subscriptions[subscription_id]
        jobs = site_adapter.fetch_jobs(subscription.condition_key)
        self._changes_by_subscription[subscription_id].extend(
            {
                "change_type": "new",
                "job_id": job["job_id"],
                "title": job["title"],
                "company_name": job["company_name"],
            }
            for job in jobs
        )

    def list_changes_for_subscription(self, subscription_id: str) -> list[JobChangeData]:
        return list(self._changes_by_subscription[subscription_id])

    @staticmethod
    def _condition_key(prefecture: str, occupation_detail: str) -> str:
        region = {"東京都": "tokyo"}.get(prefecture, prefecture)
        occupation = {"Webエンジニア": "web-engineer"}.get(occupation_detail, occupation_detail)
        return f"region:{region}|occupation:{occupation}"
