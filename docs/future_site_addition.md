# Future Site Addition Memo

This memo captures extension points for adding another job site such as doda
Challenge without changing the core collection and RSS flow.

## Adapter

Add a new `SiteAdapter` implementation for the site-specific concerns:

- master retrieval or static mapping
- search URL/query generation
- list page parsing
- pagination handling
- detail page parsing
- conversion into common `Region`, `Occupation`, and `Job` models

Keep site-specific URLs, query parameter names, CSS classes, and text labels
inside the adapter package.

## Mapping

Normalize site values into the common domain concepts before they reach
use cases. Reuse `Region.normalized_key`, `Occupation.normalized_key`, and
`CollectionCondition` where possible.

If the new site cannot represent the current region or occupation model cleanly,
add explicit mapping tests before extending the domain model.

## Persistence

The current schema stores site id and site-local job id. That is enough for
site-local collection. Cross-site duplicate detection is intentionally out of
scope and would need a separate canonical job identity model.

## Scheduler And CLI

The scheduler and CLI should continue to depend on `SiteAdapter` and
`Repository` protocols. Site selection can be added through configuration once
multiple adapters are available.

## Model Review Candidates

Review these areas when adding a second site:

- whether `Region` needs broader area hierarchy or aliases
- whether `Occupation` category/detail is enough for both sites
- whether salary and employment type need structured fields
- whether RSS items should include site-specific source labels
- whether collection frequency should differ by site
