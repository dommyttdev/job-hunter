# Local Operation Guide

This guide describes the MVP local workflow for Job Search RSS.

## Setup

1. Create and activate a Python 3.12+ virtual environment.
2. Install the package with development dependencies.

```powershell
python -m pip install -e ".[dev]"
```

## Database

The default SQLite file is `data/job_search_rss.sqlite3`.
Override it when needed:

```powershell
$env:JOB_SEARCH_RSS_DB_PATH = "data/job_search_rss.sqlite3"
```

The app and CLI create the current schema automatically through SQLAlchemy.
Alembic migration files are kept under `migrations/` for explicit migration
checks and future operational use.

## External Access

Live atGP collection is disabled by default. Enable it only for intentional
manual operation:

```powershell
$env:JOB_SEARCH_RSS_ALLOW_EXTERNAL_ACCESS = "true"
```

## Master Sync

```powershell
job-search-rss sync-master
```

This fetches atGP region and occupation masters and stores normalized common
models in SQLite.

## Register A Subscription

Region only:

```powershell
job-search-rss subscribe --prefecture Tokyo
```

Region and occupation:

```powershell
job-search-rss subscribe `
  --prefecture Tokyo `
  --occupation-category Engineering `
  --occupation-detail "Backend Engineer"
```

The command prints `subscription_id` and `rss_path`.

## Run Collection

```powershell
job-search-rss collect
```

Collection derives collection conditions from registered subscriptions, fetches
jobs from atGP, stores job snapshots and changes, and prints collection counts.

## Start The API

Install an ASGI server such as `uvicorn` if you want to run the HTTP API
locally. The project keeps server selection outside the MVP dependency set.

```powershell
python -m pip install uvicorn
python -c "from job_search_rss.api import create_app_from_settings; from job_search_rss.infrastructure.settings import load_settings; import uvicorn; uvicorn.run(create_app_from_settings(load_settings()))"
```

## Get RSS

After registering and collecting, request the path printed by the subscription
command or API response:

```powershell
Invoke-WebRequest http://127.0.0.1:8000/rss/subscription:region:tokyo
```

RSS generation reads stored changes only. It does not access atGP.

## Quality Checks

```powershell
python -m pytest
python -m ruff check .
python -m pyright
```
