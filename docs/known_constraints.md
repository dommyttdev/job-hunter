# Known Constraints

## atGP Structure Changes

The atGP adapter depends on current query parameters and HTML structure for
masters, list pages, pagination, and detail pages. If atGP changes required
fields or link shapes, collection should fail as an adapter error rather than
persisting partial jobs.

Automated tests use saved fixtures and do not prove the live site is unchanged.
Use `docs/atgp_manual_smoke.md` for intentional live confirmation.

## Collection Failures

Failed collection attempts are stored as collection run history. Deletion
detection is only valid after successful collection of a condition, so failures
must not create deletion changes from incomplete results.

`RunCollection` supports bounded retry per condition and optional delay between
conditions. MVP execution remains sequential to keep site load predictable.

## SQLite Operation

SQLite is the MVP persistence target. It is suitable for local and small-scale
operation, but it is not intended for high write concurrency or multi-worker
collection. If collection becomes parallel or multi-process, revisit locking,
transaction boundaries, and a PostgreSQL migration path.

## External Access

Live atGP access is disabled unless `JOB_SEARCH_RSS_ALLOW_EXTERNAL_ACCESS=true`
is set. RSS rendering never performs external access and should remain based on
stored job changes.

## MVP Out Of Scope

The MVP does not include Web UI, user accounts, per-user RSS ownership,
cross-site job deduplication, advanced ranking, detailed text diffs, or
doda Challenge support.
