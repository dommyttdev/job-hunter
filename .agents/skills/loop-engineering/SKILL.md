---
name: loop-engineering
description: Runs verifiable coding loops that repeatedly build context, implement one bounded change, check independent evidence, and stop safely. Use when the user asks for loop engineering, an autonomous implementation loop, repeated fix-and-verify cycles, or work that should continue until explicit acceptance conditions pass.
---

# Loop Engineering

## Purpose

Run one `Ready` backlog card or one independently committable subtask through bounded maker/checker iterations without carrying noisy agent history forward.

## Quick start

Example request: `Run MVP-FOUND-001-ST01 through loop engineering until its acceptance conditions pass; do not commit.` Build the charter first, then execute the workflow below.

## Required inputs

Before starting, create a task charter from [templates/task-charter.md](templates/task-charter.md). Stop if the objective, allowed paths, acceptance conditions, verification commands, budget, or human gates are missing.

Create runtime files under `.codex/loop-runs/<task-id>/`. They are operational state, not project documentation or commit targets.

## Workflow

1. Confirm the target is `Ready`, the Git worktree has no conflicting user changes, and the task has its own branch.
2. Copy [templates/loop-state.json](templates/loop-state.json) to the runtime directory and fill it from the charter.
3. Spawn a fresh `context_scout` without parent history when supported. Give it only the charter, current spine, unmet conditions, and an allowlist of sources.
4. Save its result as an iteration packet based on [templates/iteration-packet.md](templates/iteration-packet.md), summarize the useful result, then explicitly close the completed thread.
5. Spawn a fresh `implementer` with only that packet. Allow one bounded change and at most two edit-test attempts. It must not commit, push, merge, weaken checks, or expand scope.
6. Record its evidence references, summarize the result, then explicitly close the completed thread.
7. Spawn a fresh `reviewer`. For authentication, ownership, deletion, transactions, idempotency, concurrency, or notification correctness, use `critical_reviewer` instead or in parallel with `reviewer` after the writer is closed.
8. Do not give the checker the maker's reasoning or self-evaluation. Give it the charter, actual diff, current code, and verification commands.
9. Save the checker response using [templates/verification-result.json](templates/verification-result.json), validate it, summarize the verdict, then explicitly close every completed checker thread.
10. Apply the transition rules in [REFERENCE.md](REFERENCE.md). Update the spine by replacement, not by appending history.
11. Before another spawn, confirm no unnecessary `Done` thread remains open. If the surface cannot close completed threads, stop before reaching its open-thread limit and resume from the spine in a new primary session.

## Validation

Machine-readable contracts are [loop-state.schema.json](schemas/loop-state.schema.json) and [verification-result.schema.json](schemas/verification-result.schema.json).

Run after every spine or verification-result update:

```powershell
python .agents/skills/loop-engineering/scripts/validate_loop_artifact.py state .codex/loop-runs/<task-id>/state.json
python .agents/skills/loop-engineering/scripts/validate_loop_artifact.py verification .codex/loop-runs/<task-id>/verification.json
```

## Context boundaries

- Never forward the full parent conversation, raw logs, stack traces, or prior agent narratives.
- Keep the immutable charter separate from the mutable spine.
- Store raw evidence in files and pass paths plus the smallest relevant excerpt.
- Carry forward only unmet conditions, the latest failure fingerprint, bounded rejected approaches, verified evidence references, and one next action.
- Use a new subagent for every phase and iteration; never follow up with a completed agent for a later iteration.
- Start a new primary session after three outer iterations, loading only the charter and validated spine.

## Completion

Accept only when the independent checker returns `PASS`, every acceptance condition has reproducible evidence, and no Critical or Major finding remains. Git commit, push, merge, deployment, external writes, and destructive recovery require the authority stated in the charter.
