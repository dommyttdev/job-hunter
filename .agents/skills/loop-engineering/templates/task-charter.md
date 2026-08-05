# Loop Task Charter

## Identity

- Task ID: `<backlog-card-or-subtask-id>`
- Source: `<path-or-issue-url>`
- Branch: `<type/kebab-case-name>`
- Baseline commit: `<git-sha>`

## Objective

`<one observable outcome>`

## Scope

- Allowed paths:
  - `<path>`
- Forbidden changes:
  - `<explicit boundary>`
- Authoritative sources:
  - `<path>`

## Acceptance conditions

| ID | Observable condition | Verification command or evidence |
| --- | --- | --- |
| `AC-01` | `<condition>` | `<command-or-evidence>` |

## Budgets

- Maximum outer iterations: `5`
- Maximum maker edit-test attempts per iteration: `2`
- Maximum outer iterations per primary session: `3`
- Time or token limit: `<limit-or-not-set>`

## Authority

- Local in-scope edits: `allowed`
- Local deterministic tests: `allowed`
- Dependency installation: `requires-human`
- Git commit: `requires-human`
- Push, merge, deployment, external writes: `requires-human`
- Destructive recovery: `prohibited`

## Human gates

- Requirement, ADR, acceptance-condition, or allowed-path change
- Credentials or new external access
- User-owned conflicting changes
- New dependency or migration decision
- Critical or Major finding outside the charter

## Required final report

- Terminal state
- Acceptance condition to evidence mapping
- Changed paths
- Verification commands and results
- Remaining risks or human decision
