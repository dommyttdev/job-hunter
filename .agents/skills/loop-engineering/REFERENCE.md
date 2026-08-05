# Loop Engineering Protocol

## State machine

| State | Meaning | Allowed next states |
| --- | --- | --- |
| `READY` | Charter and initial spine are valid | `CONTEXT`, `HUMAN_GATE` |
| `CONTEXT` | A fresh scout is building the iteration packet | `IMPLEMENTING`, `BLOCKED` |
| `IMPLEMENTING` | A fresh maker owns the bounded change | `VERIFYING`, `BLOCKED` |
| `VERIFYING` | An independent checker is reproducing evidence | `ACCEPTED`, `RETRY`, `BLOCKED`, `HUMAN_GATE` |
| `RETRY` | A checker supplied a new, bounded correction | `CONTEXT`, `BUDGET_EXHAUSTED`, `HUMAN_GATE` |
| `ACCEPTED` | All acceptance conditions have independent evidence | none |
| `BLOCKED` | An in-scope dependency or required fact is unavailable | none |
| `HUMAN_GATE` | A decision or additional authority is required | none |
| `BUDGET_EXHAUSTED` | Iteration, time, token, or progress limit was reached | none |

## Controller algorithm

1. The controller owns the charter, spine, budgets, thread lifecycle, and final transition.
2. The controller does not edit implementation files or perform detailed diagnosis.
3. The scout produces one iteration packet for the smallest unmet acceptance slice.
4. The maker performs no more than two edit-test attempts in its session.
5. The checker reruns deterministic verification and inspects the actual diff.
6. `PASS` transitions to `ACCEPTED` only when all checks pass and no Critical or Major finding exists.
7. `RETRY` records one failure fingerprint and one next action, then starts with a new scout.
8. `BLOCKED`, `HUMAN_GATE`, or `BUDGET_EXHAUSTED` terminates the loop.

## Stop rules

Stop immediately when any rule applies:

- The outer iteration count reaches the charter limit; default `5`.
- The same normalized failure fingerprint occurs twice consecutively.
- Two iterations produce no new passing evidence or smaller set of unmet conditions.
- A requirement, ADR, acceptance condition, or allowed path must change.
- New credentials, external writes, dependency installation, destructive recovery, push, merge, or deployment lacks explicit authority.
- User-owned changes overlap the task.
- A Critical or Major finding cannot be resolved within the charter.

## Failure fingerprints

Build a stable fingerprint from the failing check identifier and normalized failure class. Exclude timestamps, temporary paths, random IDs, durations, and line numbers that change without changing the failure.

Examples:

```text
pytest:test_config_import:ModuleNotFoundError
ruff:src/jobhunter/app.py:F401
review:ownership-boundary:cross-user-read
```

## Evidence rules

- Prefer deterministic commands, database constraints, typed interfaces, and reproducible fixtures over model judgment.
- A maker's report is a claim, not evidence.
- The checker must reproduce required commands or mark the affected check `FAIL`.
- Evidence files stay in the runtime directory. The spine stores only relative references.
- Never treat deleted tests, weakened assertions, ignored failures, or broadened exclusions as progress.

## Git boundary

Use one task branch and one writer. Only the controller may perform Git operations, and only when the charter authorizes them. Failed attempts remain uncommitted and must be corrected in place or escalated; do not use destructive reset or checkout operations.
