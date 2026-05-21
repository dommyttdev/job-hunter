import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class Job:
    job_id: str
    site_id: str
    title: str
    company_name: str
    detail_url: str
    work_location: str
    occupation: str
    salary: str
    content_hash: str

    @staticmethod
    def generate_content_hash(
        *,
        title: str,
        company_name: str,
        detail_url: str,
        work_location: str,
        occupation: str,
        salary: str,
        description: str,
    ) -> str:
        content = "\n".join(
            [
                title,
                company_name,
                detail_url,
                work_location,
                occupation,
                salary,
                description,
            ]
        )
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
