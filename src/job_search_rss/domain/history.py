from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class JobChangeType(Enum):
    NEW = "new"
    UPDATED = "updated"
    DELETED = "deleted"


@dataclass(frozen=True)
class JobChange:
    job_id: str
    collection_condition_key: str
    change_type: JobChangeType
    content_hash: str
    occurred_at: datetime


class CollectionRunStatus(Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(frozen=True)
class CollectionRun:
    collection_condition_key: str
    status: CollectionRunStatus
    started_at: datetime
    finished_at: datetime
    collected_job_count: int
    error_message: str | None = None

    @classmethod
    def succeeded(
        cls,
        *,
        collection_condition_key: str,
        started_at: datetime,
        finished_at: datetime,
        collected_job_count: int,
    ) -> "CollectionRun":
        return cls(
            collection_condition_key=collection_condition_key,
            status=CollectionRunStatus.SUCCEEDED,
            started_at=started_at,
            finished_at=finished_at,
            collected_job_count=collected_job_count,
        )

    @classmethod
    def failed(
        cls,
        *,
        collection_condition_key: str,
        started_at: datetime,
        finished_at: datetime,
        error_message: str,
    ) -> "CollectionRun":
        return cls(
            collection_condition_key=collection_condition_key,
            status=CollectionRunStatus.FAILED,
            started_at=started_at,
            finished_at=finished_at,
            collected_job_count=0,
            error_message=error_message,
        )
