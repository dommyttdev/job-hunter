from __future__ import annotations

import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

STATE_LIMIT_BYTES = 4_096
VERIFICATION_LIMIT_BYTES = 16_384

STATE_STATUSES = {
    "READY",
    "CONTEXT",
    "IMPLEMENTING",
    "VERIFYING",
    "RETRY",
    "ACCEPTED",
    "BLOCKED",
    "HUMAN_GATE",
    "BUDGET_EXHAUSTED",
}
VERDICTS = {"PASS", "RETRY", "BLOCKED"}
CHECK_RESULTS = {"PASS", "FAIL"}
SEVERITIES = {"Critical", "Major", "Minor"}

STATE_KEYS = {
    "task_id",
    "status",
    "iteration",
    "max_iterations",
    "baseline_commit",
    "unmet_acceptance_conditions",
    "last_failure_fingerprint",
    "same_failure_count",
    "last_verified_evidence",
    "rejected_approaches",
    "next_action",
}
VERIFICATION_KEYS = {
    "task_id",
    "iteration",
    "verdict",
    "acceptance_checks",
    "findings",
    "failure_fingerprint",
    "next_delta",
    "human_gate_reason",
}


def require_object(value: Any, label: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return {}
    return value


def require_exact_keys(
    value: dict[str, Any], expected: set[str], label: str, errors: list[str]
) -> None:
    missing = sorted(expected - value.keys())
    extra = sorted(value.keys() - expected)
    if missing:
        errors.append(f"{label} is missing keys: {', '.join(missing)}")
    if extra:
        errors.append(f"{label} has unknown keys: {', '.join(extra)}")


def require_string(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a non-empty string")


def require_nullable_string(value: Any, label: str, errors: list[str]) -> None:
    if value is not None:
        require_string(value, label, errors)


def require_integer(value: Any, minimum: int, label: str, errors: list[str]) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        errors.append(f"{label} must be an integer greater than or equal to {minimum}")


def require_string_list(value: Any, label: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{label} must be an array")
        return []
    strings: list[str] = []
    for index, item in enumerate(value):
        require_string(item, f"{label}[{index}]", errors)
        if isinstance(item, str):
            strings.append(item)
    if len(strings) != len(set(strings)):
        errors.append(f"{label} must not contain duplicates")
    return strings


def validate_state(payload: Any) -> list[str]:
    errors: list[str] = []
    state = require_object(payload, "state", errors)
    require_exact_keys(state, STATE_KEYS, "state", errors)

    require_string(state.get("task_id"), "task_id", errors)
    status = state.get("status")
    if not isinstance(status, str) or status not in STATE_STATUSES:
        errors.append(f"status must be one of: {', '.join(sorted(STATE_STATUSES))}")
    require_integer(state.get("iteration"), 0, "iteration", errors)
    require_integer(state.get("max_iterations"), 1, "max_iterations", errors)
    require_string(state.get("baseline_commit"), "baseline_commit", errors)
    unmet = require_string_list(
        state.get("unmet_acceptance_conditions"),
        "unmet_acceptance_conditions",
        errors,
    )
    require_nullable_string(
        state.get("last_failure_fingerprint"),
        "last_failure_fingerprint",
        errors,
    )
    require_integer(state.get("same_failure_count"), 0, "same_failure_count", errors)
    require_string_list(
        state.get("last_verified_evidence"), "last_verified_evidence", errors
    )
    require_nullable_string(state.get("next_action"), "next_action", errors)

    rejected = state.get("rejected_approaches")
    if not isinstance(rejected, list):
        errors.append("rejected_approaches must be an array")
    else:
        if len(rejected) > 5:
            errors.append("rejected_approaches must contain at most 5 items")
        for index, item in enumerate(rejected):
            approach = require_object(item, f"rejected_approaches[{index}]", errors)
            require_exact_keys(
                approach,
                {"id", "reason"},
                f"rejected_approaches[{index}]",
                errors,
            )
            require_string(approach.get("id"), f"rejected_approaches[{index}].id", errors)
            require_string(
                approach.get("reason"),
                f"rejected_approaches[{index}].reason",
                errors,
            )

    iteration = state.get("iteration")
    maximum = state.get("max_iterations")
    if (
        isinstance(iteration, int)
        and not isinstance(iteration, bool)
        and isinstance(maximum, int)
        and not isinstance(maximum, bool)
        and iteration > maximum
    ):
        errors.append("iteration must not exceed max_iterations")

    fingerprint = state.get("last_failure_fingerprint")
    if fingerprint is None and state.get("same_failure_count") != 0:
        errors.append("same_failure_count must be 0 when no failure fingerprint exists")
    if status == "RETRY":
        require_string(fingerprint, "last_failure_fingerprint for RETRY", errors)
        require_string(state.get("next_action"), "next_action for RETRY", errors)
    if status == "ACCEPTED":
        if unmet:
            errors.append("ACCEPTED state must not contain unmet acceptance conditions")
        if state.get("next_action") is not None:
            errors.append("ACCEPTED state must have a null next_action")

    return errors


def validate_verification(payload: Any) -> list[str]:
    errors: list[str] = []
    result = require_object(payload, "verification", errors)
    require_exact_keys(result, VERIFICATION_KEYS, "verification", errors)

    require_string(result.get("task_id"), "task_id", errors)
    require_integer(result.get("iteration"), 1, "iteration", errors)
    verdict = result.get("verdict")
    if not isinstance(verdict, str) or verdict not in VERDICTS:
        errors.append(f"verdict must be one of: {', '.join(sorted(VERDICTS))}")
    require_nullable_string(
        result.get("failure_fingerprint"), "failure_fingerprint", errors
    )
    require_nullable_string(result.get("next_delta"), "next_delta", errors)
    require_nullable_string(
        result.get("human_gate_reason"), "human_gate_reason", errors
    )

    checks = result.get("acceptance_checks")
    parsed_checks: list[dict[str, Any]] = []
    if not isinstance(checks, list) or not checks:
        errors.append("acceptance_checks must be a non-empty array")
    else:
        for index, item in enumerate(checks):
            check = require_object(item, f"acceptance_checks[{index}]", errors)
            require_exact_keys(
                check,
                {"id", "result", "evidence_ref"},
                f"acceptance_checks[{index}]",
                errors,
            )
            require_string(check.get("id"), f"acceptance_checks[{index}].id", errors)
            check_result = check.get("result")
            if not isinstance(check_result, str) or check_result not in CHECK_RESULTS:
                errors.append(
                    f"acceptance_checks[{index}].result must be PASS or FAIL"
                )
            require_string(
                check.get("evidence_ref"),
                f"acceptance_checks[{index}].evidence_ref",
                errors,
            )
            parsed_checks.append(check)

    findings = result.get("findings")
    parsed_findings: list[dict[str, Any]] = []
    if not isinstance(findings, list):
        errors.append("findings must be an array")
    else:
        for index, item in enumerate(findings):
            finding = require_object(item, f"findings[{index}]", errors)
            require_exact_keys(
                finding,
                {"severity", "summary", "evidence_ref"},
                f"findings[{index}]",
                errors,
            )
            severity = finding.get("severity")
            if not isinstance(severity, str) or severity not in SEVERITIES:
                errors.append(
                    f"findings[{index}].severity must be Critical, Major, or Minor"
                )
            require_string(finding.get("summary"), f"findings[{index}].summary", errors)
            require_string(
                finding.get("evidence_ref"),
                f"findings[{index}].evidence_ref",
                errors,
            )
            parsed_findings.append(finding)

    if verdict == "PASS":
        if any(check.get("result") != "PASS" for check in parsed_checks):
            errors.append("PASS verdict requires every acceptance check to pass")
        if any(
            finding.get("severity") in {"Critical", "Major"}
            for finding in parsed_findings
        ):
            errors.append("PASS verdict cannot contain Critical or Major findings")
        if result.get("failure_fingerprint") is not None:
            errors.append("PASS verdict must have a null failure_fingerprint")
        if result.get("next_delta") is not None:
            errors.append("PASS verdict must have a null next_delta")
        if result.get("human_gate_reason") is not None:
            errors.append("PASS verdict must have a null human_gate_reason")
    elif verdict == "RETRY":
        require_string(
            result.get("failure_fingerprint"),
            "failure_fingerprint for RETRY",
            errors,
        )
        require_string(result.get("next_delta"), "next_delta for RETRY", errors)
    elif verdict == "BLOCKED":
        require_string(
            result.get("human_gate_reason"),
            "human_gate_reason for BLOCKED",
            errors,
        )

    return errors


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def main(argv: list[str]) -> int:
    if len(argv) != 3 or argv[1] not in {"state", "verification"}:
        print(
            "usage: validate_loop_artifact.py <state|verification> <json-path>",
            file=sys.stderr,
        )
        return 2

    kind = argv[1]
    path = Path(argv[2])
    try:
        raw = path.read_bytes()
    except OSError as error:
        print(f"ERROR: cannot read {path}: {error}", file=sys.stderr)
        return 1

    limit = STATE_LIMIT_BYTES if kind == "state" else VERIFICATION_LIMIT_BYTES
    errors: list[str] = []
    if len(raw) > limit:
        errors.append(f"artifact exceeds the {limit}-byte limit")

    try:
        payload = json.loads(raw.decode("utf-8"), object_pairs_hook=reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        print(f"ERROR: invalid JSON in {path}: {error}", file=sys.stderr)
        return 1

    validator: Callable[[Any], list[str]] = (
        validate_state if kind == "state" else validate_verification
    )
    errors.extend(validator(payload))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: {kind} artifact {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
