import argparse
from dataclasses import dataclass
from typing import Sequence

from job_search_rss.domain.condition_values import Occupation, Region
from job_search_rss.domain.subscription_condition import SubscriptionCondition
from job_search_rss.infrastructure.database import (
    SqlAlchemyRepository,
    create_schema,
    create_sqlite_engine,
)
from job_search_rss.infrastructure.settings import load_settings
from job_search_rss.ports.repository import Repository
from job_search_rss.ports.site_adapter import SiteAdapter
from job_search_rss.usecase.manage_collection_condition import ManageCollectionCondition
from job_search_rss.usecase.register_subscription_condition import (
    RegisterSubscriptionCondition,
    SubscriptionConditionRepository,
)
from job_search_rss.usecase.run_collection import RunCollection


@dataclass(frozen=True)
class RegisterSubscriptionInput:
    prefecture: str | None = None
    city: str | None = None
    occupation_category: str | None = None
    occupation_detail: str | None = None


@dataclass(frozen=True)
class RegisterSubscriptionCommandResult:
    subscription_id: str
    rss_path: str


@dataclass(frozen=True)
class RunCollectionCommandResult:
    change_count: int
    succeeded_condition_count: int
    failed_condition_count: int


def register_subscription_command(
    command_input: RegisterSubscriptionInput,
    *,
    repository: SubscriptionConditionRepository,
) -> RegisterSubscriptionCommandResult:
    condition = _subscription_condition_from_input(command_input)
    registered = RegisterSubscriptionCondition(repository).execute(condition)
    return RegisterSubscriptionCommandResult(
        subscription_id=registered.id,
        rss_path=f"/rss/{registered.id}",
    )


def run_collection_command(
    *,
    repository: Repository,
    site_adapter: SiteAdapter,
) -> RunCollectionCommandResult:
    ManageCollectionCondition(repository).execute()
    result = RunCollection(repository, site_adapter).execute()
    return RunCollectionCommandResult(
        change_count=len(result.changes),
        succeeded_condition_count=len(result.succeeded_condition_keys),
        failed_condition_count=len(result.failed_condition_keys),
    )


def main(
    argv: Sequence[str] | None = None,
    *,
    repository: SubscriptionConditionRepository | None = None,
) -> int:
    args = _build_parser().parse_args(argv)
    command_repository = repository or _create_repository_from_settings()

    match args.command:
        case "subscribe":
            result = register_subscription_command(
                RegisterSubscriptionInput(
                    prefecture=args.prefecture,
                    city=args.city,
                    occupation_category=args.occupation_category,
                    occupation_detail=args.occupation_detail,
                ),
                repository=command_repository,
            )
            print(f"subscription_id={result.subscription_id}")
            print(f"rss_path={result.rss_path}")
            return 0
        case _:
            raise AssertionError(f"unsupported command: {args.command}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="job-search-rss")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subscribe = subparsers.add_parser("subscribe")
    subscribe.add_argument("--prefecture")
    subscribe.add_argument("--city")
    subscribe.add_argument("--occupation-category")
    subscribe.add_argument("--occupation-detail")

    return parser


def _create_repository_from_settings() -> SubscriptionConditionRepository:
    settings = load_settings()
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_sqlite_engine(f"sqlite:///{settings.db_path.as_posix()}")
    create_schema(engine)
    return SqlAlchemyRepository(engine)


def _subscription_condition_from_input(
    command_input: RegisterSubscriptionInput,
) -> SubscriptionCondition:
    region = None
    if command_input.prefecture is not None:
        region = Region(prefecture=command_input.prefecture, city=command_input.city)

    occupation = None
    if (
        command_input.occupation_category is not None
        and command_input.occupation_detail is not None
    ):
        occupation = Occupation(
            category=command_input.occupation_category,
            detail=command_input.occupation_detail,
        )

    return SubscriptionCondition(region=region, occupation=occupation)


if __name__ == "__main__":
    raise SystemExit(main())
