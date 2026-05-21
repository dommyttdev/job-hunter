from datetime import UTC, datetime

from sqlalchemy import DateTime, Engine, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from job_search_rss.domain.collection_condition import CollectionCondition
from job_search_rss.domain.condition_values import Occupation, Region
from job_search_rss.domain.history import (
    CollectionRun,
    CollectionRunStatus,
    JobChange,
    JobChangeType,
)
from job_search_rss.domain.job import Job
from job_search_rss.domain.subscription_condition import SubscriptionCondition
from job_search_rss.ports.repository import Repository


class Base(DeclarativeBase):
    pass


class JobRecord(Base):
    __tablename__ = "jobs"

    job_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    site_id: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    company_name: Mapped[str] = mapped_column(Text, nullable=False)
    detail_url: Mapped[str] = mapped_column(Text, nullable=False)
    work_location: Mapped[str] = mapped_column(Text, nullable=False)
    occupation: Mapped[str] = mapped_column(Text, nullable=False)
    salary: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False)


class RegionRecord(Base):
    __tablename__ = "regions"

    normalized_key: Mapped[str] = mapped_column(String(512), primary_key=True)
    prefecture: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str | None] = mapped_column(String(255))


class OccupationRecord(Base):
    __tablename__ = "occupations"

    normalized_key: Mapped[str] = mapped_column(String(512), primary_key=True)
    category: Mapped[str] = mapped_column(String(255), nullable=False)
    detail: Mapped[str] = mapped_column(String(255), nullable=False)


class JobChangeRecord(Base):
    __tablename__ = "job_changes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String(255), nullable=False)
    collection_condition_key: Mapped[str] = mapped_column(String(512), nullable=False)
    change_type: Mapped[str] = mapped_column(String(32), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SubscriptionConditionRecord(Base):
    __tablename__ = "subscription_conditions"

    normalized_key: Mapped[str] = mapped_column(String(512), primary_key=True)
    region_prefecture: Mapped[str | None] = mapped_column(String(255))
    region_city: Mapped[str | None] = mapped_column(String(255))
    occupation_category: Mapped[str | None] = mapped_column(String(255))
    occupation_detail: Mapped[str | None] = mapped_column(String(255))


class CollectionConditionRecord(Base):
    __tablename__ = "collection_conditions"

    normalized_key: Mapped[str] = mapped_column(String(512), primary_key=True)
    site_id: Mapped[str] = mapped_column(String(64), nullable=False)
    condition_key: Mapped[str] = mapped_column(String(512), nullable=False)


class CollectionRunRecord(Base):
    __tablename__ = "collection_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    collection_condition_key: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    collected_job_count: Mapped[int] = mapped_column(Integer, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)


class ConditionSnapshotRecord(Base):
    __tablename__ = "condition_snapshots"

    collection_condition_key: Mapped[str] = mapped_column(String(512), primary_key=True)
    job_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("jobs.job_id"),
        primary_key=True,
    )


def create_sqlite_engine(db_url: str) -> Engine:
    return create_engine(db_url)


def create_schema(engine: Engine) -> None:
    Base.metadata.create_all(engine)


class SqlAlchemyRepository(Repository):
    def __init__(self, engine: Engine) -> None:
        self._session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    def save_region(self, region: Region) -> None:
        with self._session_factory() as session:
            session.merge(_region_record_from_domain(region))
            session.commit()

    def list_regions(self) -> list[Region]:
        with self._session_factory() as session:
            records = session.query(RegionRecord).order_by(RegionRecord.normalized_key).all()
            return [_region_from_record(record) for record in records]

    def save_occupation(self, occupation: Occupation) -> None:
        with self._session_factory() as session:
            session.merge(_occupation_record_from_domain(occupation))
            session.commit()

    def list_occupations(self) -> list[Occupation]:
        with self._session_factory() as session:
            records = (
                session.query(OccupationRecord)
                .order_by(OccupationRecord.normalized_key)
                .all()
            )
            return [_occupation_from_record(record) for record in records]

    def save_job(self, job: Job) -> None:
        with self._session_factory() as session:
            session.merge(_job_record_from_domain(job))
            session.commit()

    def list_jobs(self) -> list[Job]:
        with self._session_factory() as session:
            records = session.query(JobRecord).order_by(JobRecord.job_id).all()
            return [_job_from_record(record) for record in records]

    def save_job_change(self, change: JobChange) -> None:
        with self._session_factory() as session:
            session.add(_job_change_record_from_domain(change))
            session.commit()

    def list_job_changes(self) -> list[JobChange]:
        with self._session_factory() as session:
            records = session.query(JobChangeRecord).order_by(JobChangeRecord.id).all()
            return [_job_change_from_record(record) for record in records]

    def save_subscription_condition(self, condition: SubscriptionCondition) -> None:
        with self._session_factory() as session:
            session.merge(_subscription_condition_record_from_domain(condition))
            session.commit()

    def list_subscription_conditions(self) -> list[SubscriptionCondition]:
        with self._session_factory() as session:
            records = (
                session.query(SubscriptionConditionRecord)
                .order_by(SubscriptionConditionRecord.normalized_key)
                .all()
            )
            return [_subscription_condition_from_record(record) for record in records]

    def save_collection_condition(self, condition: CollectionCondition) -> None:
        with self._session_factory() as session:
            session.merge(_collection_condition_record_from_domain(condition))
            session.commit()

    def list_collection_conditions(self) -> list[CollectionCondition]:
        with self._session_factory() as session:
            records = (
                session.query(CollectionConditionRecord)
                .order_by(CollectionConditionRecord.normalized_key)
                .all()
            )
            return [_collection_condition_from_record(record) for record in records]

    def save_collection_run(self, run: CollectionRun) -> None:
        with self._session_factory() as session:
            session.add(_collection_run_record_from_domain(run))
            session.commit()

    def list_collection_runs(self) -> list[CollectionRun]:
        with self._session_factory() as session:
            records = session.query(CollectionRunRecord).order_by(CollectionRunRecord.id).all()
            return [_collection_run_from_record(record) for record in records]

    def save_condition_snapshot(
        self,
        *,
        collection_condition_key: str,
        job_ids: list[str],
    ) -> None:
        with self._session_factory() as session:
            session.query(ConditionSnapshotRecord).filter_by(
                collection_condition_key=collection_condition_key
            ).delete()
            session.add_all(
                ConditionSnapshotRecord(
                    collection_condition_key=collection_condition_key,
                    job_id=job_id,
                )
                for job_id in job_ids
            )
            session.commit()

    def list_job_ids_for_condition(self, collection_condition_key: str) -> list[str]:
        with self._session_factory() as session:
            records = (
                session.query(ConditionSnapshotRecord)
                .filter_by(collection_condition_key=collection_condition_key)
                .order_by(ConditionSnapshotRecord.job_id)
                .all()
            )
            return [record.job_id for record in records]


def _job_record_from_domain(job: Job) -> JobRecord:
    return JobRecord(
        job_id=job.job_id,
        site_id=job.site_id,
        title=job.title,
        company_name=job.company_name,
        detail_url=job.detail_url,
        work_location=job.work_location,
        occupation=job.occupation,
        salary=job.salary,
        content_hash=job.content_hash,
    )


def _region_record_from_domain(region: Region) -> RegionRecord:
    return RegionRecord(
        normalized_key=region.normalized_key,
        prefecture=region.prefecture,
        city=region.city,
    )


def _region_from_record(record: RegionRecord) -> Region:
    return Region(prefecture=record.prefecture, city=record.city)


def _occupation_record_from_domain(occupation: Occupation) -> OccupationRecord:
    return OccupationRecord(
        normalized_key=occupation.normalized_key,
        category=occupation.category,
        detail=occupation.detail,
    )


def _occupation_from_record(record: OccupationRecord) -> Occupation:
    return Occupation(category=record.category, detail=record.detail)


def _job_from_record(record: JobRecord) -> Job:
    return Job(
        job_id=record.job_id,
        site_id=record.site_id,
        title=record.title,
        company_name=record.company_name,
        detail_url=record.detail_url,
        work_location=record.work_location,
        occupation=record.occupation,
        salary=record.salary,
        content_hash=record.content_hash,
    )


def _job_change_record_from_domain(change: JobChange) -> JobChangeRecord:
    return JobChangeRecord(
        job_id=change.job_id,
        collection_condition_key=change.collection_condition_key,
        change_type=change.change_type.value,
        content_hash=change.content_hash,
        occurred_at=change.occurred_at,
    )


def _job_change_from_record(record: JobChangeRecord) -> JobChange:
    return JobChange(
        job_id=record.job_id,
        collection_condition_key=record.collection_condition_key,
        change_type=JobChangeType(record.change_type),
        content_hash=record.content_hash,
        occurred_at=_ensure_aware(record.occurred_at),
    )


def _subscription_condition_record_from_domain(
    condition: SubscriptionCondition,
) -> SubscriptionConditionRecord:
    return SubscriptionConditionRecord(
        normalized_key=condition.normalized_key,
        region_prefecture=None if condition.region is None else condition.region.prefecture,
        region_city=None if condition.region is None else condition.region.city,
        occupation_category=(
            None if condition.occupation is None else condition.occupation.category
        ),
        occupation_detail=None if condition.occupation is None else condition.occupation.detail,
    )


def _subscription_condition_from_record(
    record: SubscriptionConditionRecord,
) -> SubscriptionCondition:
    region = None
    if record.region_prefecture is not None:
        region = Region(prefecture=record.region_prefecture, city=record.region_city)

    occupation = None
    if record.occupation_category is not None and record.occupation_detail is not None:
        occupation = Occupation(
            category=record.occupation_category,
            detail=record.occupation_detail,
        )

    return SubscriptionCondition(region=region, occupation=occupation)


def _collection_condition_record_from_domain(
    condition: CollectionCondition,
) -> CollectionConditionRecord:
    return CollectionConditionRecord(
        normalized_key=condition.normalized_key,
        site_id=condition.site_id,
        condition_key=condition.condition_key,
    )


def _collection_condition_from_record(record: CollectionConditionRecord) -> CollectionCondition:
    return CollectionCondition(site_id=record.site_id, condition_key=record.condition_key)


def _collection_run_record_from_domain(run: CollectionRun) -> CollectionRunRecord:
    return CollectionRunRecord(
        collection_condition_key=run.collection_condition_key,
        status=run.status.value,
        started_at=run.started_at,
        finished_at=run.finished_at,
        collected_job_count=run.collected_job_count,
        error_message=run.error_message,
    )


def _collection_run_from_record(record: CollectionRunRecord) -> CollectionRun:
    return CollectionRun(
        collection_condition_key=record.collection_condition_key,
        status=CollectionRunStatus(record.status),
        started_at=_ensure_aware(record.started_at),
        finished_at=_ensure_aware(record.finished_at),
        collected_job_count=record.collected_job_count,
        error_message=record.error_message,
    )


def _ensure_aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value
