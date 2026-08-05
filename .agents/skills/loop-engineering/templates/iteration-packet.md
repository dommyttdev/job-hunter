# Iteration Packet

## Control

- Task ID: `<task-id>`
- Iteration: `<number>`
- Baseline commit: `<git-sha>`
- Phase owner: `<context_scout|implementer|reviewer|critical_reviewer>`

## Current slice

- Unmet acceptance condition: `<one condition>`
- Required outcome: `<observable result>`
- Next action: `<one bounded action>`

## Context allowlist

- Charter: `<path>`
- Spine: `<path>`
- Authoritative sources:
  - `<path>`
- Implementation paths:
  - `<path>`

Do not read unrelated planning cards, historical logs, or files outside this allowlist unless a stop condition requires escalation.

## Latest checker delta

- Failure fingerprint: `<fingerprint-or-none>`
- Failed check: `<check-id-or-none>`
- Smallest relevant evidence: `<path-and-short-excerpt-or-none>`
- Rejected approaches:
  - `<id-and-reason-or-none>`

## Boundaries

- Allowed edits: `<paths-or-read-only>`
- Forbidden actions: commit, push, merge, deployment, destructive recovery, weakened tests, scope expansion
- Verification commands:
  - `<command>`
- Stop when:
  - The current slice passes.
  - Two maker edit-test attempts are exhausted.
  - New authority, scope, or an unavailable dependency is required.

## Return contract

Return only the role-specific structured result. Do not return raw logs, full file contents, hidden reasoning, or a narrative of failed attempts.
