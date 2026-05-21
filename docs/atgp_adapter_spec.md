# atGP Adapter Spec Memo

## Scope

This memo captures the minimum atGP assumptions used by WBS 8 adapter tests and
fixtures. The implementation must keep these details inside
`job_search_rss.adapters.atgp` so domain and use case layers stay independent
from atGP-specific URLs, parameters, and HTML structure.

## Source Pages

- Search result base URL: `https://www.atgp.jp/search/top/search_result`
- Region filtered example: `https://www.atgp.jp/search/top/search_result?prefectures=13`
- Occupation filtered example:
  `https://www.atgp.jp/search/top/search_result?job_categories=b01001610000002000&job_types=...`
- Detail URL shape: `https://www.atgp.jp/search/top/search_result_detail/{site_job_id}`

## Observed Search Result Structure

- The list page shows a total count and a visible range such as `1件〜30件表示中`.
- Each item contains:
  - update date, for example `更新日：2026年5月21日`
  - detail link
  - title
  - company name
  - occupation lines after `職種`
  - work location after `勤務地`
  - employment type after `雇用形態`
  - salary after `給与`
- Popular condition links near the footer expose current query parameters for
  region and occupation masters.

## Adapter Rules

- Parse saved HTML fixtures in automated tests. Do not depend on live atGP
  access in the test suite.
- Convert atGP-specific master values into common `Region` and `Occupation`
  domain values before exposing them outside the adapter.
- Derive common `Job` values from list and detail pages. Content hash generation
  must use the common `Job.generate_content_hash` API.
- Treat missing required fields, unknown structural changes, and unexpected data
  as adapter failures, not partially valid domain objects.
