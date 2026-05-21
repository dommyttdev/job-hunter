from job_search_rss.domain.collection_condition import CollectionCondition
from job_search_rss.domain.history import CollectionRun, JobChange
from job_search_rss.domain.job import Job
from job_search_rss.domain.subscription_condition import SubscriptionCondition
from job_search_rss.usecase.register_subscription_condition import Subscription
from tests.fakes.site_adapter import FakeSiteAdapter
from tests.fakes.types import JobChangeData


class FakeRepository:
    def __init__(self) -> None:
        self._subscriptions: dict[str, Subscription] = {}
        self._changes_by_subscription: dict[str, list[JobChangeData]] = {}
        self._jobs: list[Job] = []
        self._job_changes: list[JobChange] = []
        self._subscription_conditions: list[SubscriptionCondition] = []
        self._collection_conditions: list[CollectionCondition] = []
        self._collection_runs: list[CollectionRun] = []

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

    def save_job(self, job: Job) -> None:
        self._jobs.append(job)

    def list_jobs(self) -> list[Job]:
        return list(self._jobs)

    def save_job_change(self, change: JobChange) -> None:
        self._job_changes.append(change)

    def list_job_changes(self) -> list[JobChange]:
        return list(self._job_changes)

    def save_subscription_condition(self, condition: SubscriptionCondition) -> None:
        self._subscription_conditions.append(condition)

    def list_subscription_conditions(self) -> list[SubscriptionCondition]:
        return list(self._subscription_conditions)

    def save_collection_condition(self, condition: CollectionCondition) -> None:
        self._collection_conditions.append(condition)

    def list_collection_conditions(self) -> list[CollectionCondition]:
        return list(self._collection_conditions)

    def save_collection_run(self, run: CollectionRun) -> None:
        self._collection_runs.append(run)

    def list_collection_runs(self) -> list[CollectionRun]:
        return list(self._collection_runs)

    @staticmethod
    def _condition_key(prefecture: str, occupation_detail: str) -> str:
        region = {"東京都": "tokyo"}.get(prefecture, prefecture)
        occupation = {"Webエンジニア": "web-engineer"}.get(occupation_detail, occupation_detail)
        return f"region:{region}|occupation:{occupation}"
