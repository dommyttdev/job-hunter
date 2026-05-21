class FakeSiteAdapter:
    def __init__(self) -> None:
        self._jobs_by_condition: dict[str, list[dict[str, str]]] = {}
        self.call_count = 0
        self.raise_if_called = False

    def add_job(
        self,
        *,
        condition_key: str,
        job_id: str,
        title: str,
        company_name: str,
    ) -> None:
        self._jobs_by_condition.setdefault(condition_key, []).append(
            {
                "job_id": job_id,
                "title": title,
                "company_name": company_name,
            }
        )

    def fetch_jobs(self, condition_key: str) -> list[dict[str, str]]:
        if self.raise_if_called:
            msg = "SiteAdapter must not be called"
            raise AssertionError(msg)

        self.call_count += 1
        return list(self._jobs_by_condition.get(condition_key, []))
