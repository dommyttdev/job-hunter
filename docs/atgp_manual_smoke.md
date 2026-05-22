# atGP Manual Smoke Procedure

Automated tests must use saved fixtures and must not access the live atGP site.
Use this checklist only when manually confirming the live adapter behavior.

## Preconditions

- Network access is available.
- The check is run intentionally by an operator.
- Test fixtures are not updated directly from live HTML without review.

## Checks

1. Open `https://www.atgp.jp/search/top/search_result`.
2. Confirm the page still exposes region links with `prefectures` query values.
3. Confirm occupation links still expose `job_categories` and `job_types` query
   values.
4. Open a region filtered page such as
   `https://www.atgp.jp/search/top/search_result?prefectures=13`.
5. Confirm job cards still provide a detail URL, title, company name, work
   location, occupation, and salary.
6. Open one detail page and confirm it still provides job id, title, company
   name, occupation, work location, salary, and description.
7. If structure changed, capture a new minimal fixture under
   `tests/fixtures/atgp/` and update parser tests before changing production
   code.

## Latest Result

Checked on 2026-05-22.

- `https://www.atgp.jp/search/top/search_result` returned HTTP 200.
- Raw HTML still contains `prefectures=`, `job_categories=`, and
  `search_result_detail`.
- `https://www.atgp.jp/search/top/search_result?prefectures=13` returned
  HTTP 200 and included at least one detail link.
- One live detail page returned HTTP 200:
  `https://www.atgp.jp/search/top/search_result_detail/a076000000010rrp28`.
- The detail page still contained occupation-related content.
