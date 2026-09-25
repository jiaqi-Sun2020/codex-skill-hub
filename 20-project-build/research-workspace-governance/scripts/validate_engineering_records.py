#!/usr/bin/env python3
"""Validate engineering repair, execution, and GitHub Actions evidence records."""

from __future__ import annotations

import argparse
from datetime import datetime
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any


RESULT_SCHEMA = "engineering-record-validation/v1"
REPAIR_SCHEMA = "engineering-repair-record/v1"
PLAN_SCHEMA = "engineering-execution-plan/v1"
RECEIPT_SCHEMA = "engineering-execution-receipt/v1"
CI_SCHEMA = "github-actions-evidence/v1"
MAX_RECORD_BYTES = 5 * 1024 * 1024
SCHEMA_ROOT = Path(__file__).resolve().parents[1] / "references"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
OBJECT_ID = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
STABLE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/#-]{0,255}$")
NORMAL_STATES = [
    "reported", "reproduced", "diagnosed", "planned", "approved", "fixed",
    "locally_verified", "ci_verified", "closed",
]
EXCEPTION_STATES = {"blocked", "stale", "rolled_back"}
RUN_STATES = {
    "not_started", "stale", "awaiting_authorization", "prepared",
    "canary_passed", "full_authorized",
}
FAILURE_CLASSES = {
    "none", "portability", "infrastructure", "artifact_integrity", "contract", "scientific",
}
TRANSACTION_NAME = re.compile(
    r"^[.]txn-(?P<phase>[a-z0-9-]+)-(?P<prefix>[0-9a-f]{16})-(?P<nonce>[A-Za-z0-9_-]{8,24})$"
)


class UnsafeInput(ValueError):
    pass


def is_link_like(path: Path) -> bool:
    try:
        if path.is_symlink():
            return True
        junction_check = getattr(path, "is_junction", None)
        if junction_check and junction_check():
            return True
        return bool(getattr(path.lstat(), "st_file_attributes", 0) & 0x400)
    except OSError:
        return True


def first_link_component(path: Path) -> Path | None:
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        if current.exists() and is_link_like(current):
            return current
    return None


def resolve_project(raw: str) -> Path:
    candidate = Path(raw).expanduser().absolute()
    linked = first_link_component(candidate)
    if linked is not None:
        raise UnsafeInput(f"project path traverses a link or junction: {linked}")
    root = candidate.resolve(strict=True)
    if not root.is_dir():
        raise UnsafeInput(f"project root is not a directory: {root}")
    return root


def resolve_record(root: Path, raw: str) -> Path:
    relative = Path(raw)
    if relative.is_absolute() or ".." in relative.parts:
        raise UnsafeInput(f"record path must be project-relative without '..': {raw}")
    candidate = (root / relative).absolute()
    linked = first_link_component(candidate)
    if linked is not None:
        raise UnsafeInput(f"record path traverses a link or junction: {linked}")
    resolved = candidate.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise UnsafeInput(f"record escapes the project root: {raw}") from exc
    if not resolved.is_file() or is_link_like(resolved):
        raise UnsafeInput(f"record is not a safe regular file: {raw}")
    if resolved.stat().st_size > MAX_RECORD_BYTES:
        raise UnsafeInput(f"record exceeds {MAX_RECORD_BYTES} bytes: {raw}")
    return resolved


def load_record(root: Path, raw: str) -> dict[str, Any]:
    path = resolve_record(root, raw)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise UnsafeInput(f"record is not valid UTF-8 JSON: {raw}: {exc}") from exc
    if not isinstance(value, dict):
        raise UnsafeInput(f"record root must be an object: {raw}")
    return value


def canonical_hash(value: dict[str, Any], field: str) -> str:
    copy = dict(value)
    copy.pop(field, None)
    payload = json.dumps(
        copy, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def transaction_sibling_name(phase: str, target_identity_sha256: str, nonce: str) -> str:
    """Build a fixed-overhead transaction name without repeating the target basename."""
    if not re.fullmatch(r"[a-z0-9-]{1,16}", phase):
        raise ValueError("transaction phase code must be 1-16 lowercase safe characters")
    if not SHA256.fullmatch(target_identity_sha256):
        raise ValueError("transaction target identity must be a lowercase SHA-256")
    if not re.fullmatch(r"[A-Za-z0-9_-]{8,24}", nonce):
        raise ValueError("transaction nonce must be 8-24 safe characters")
    return f".txn-{phase}-{target_identity_sha256[:16]}-{nonce}"


def classify_transaction_candidate(
    candidate: Path,
    final_target: Path,
    target_identity_sha256: str,
    attempt_id: str,
    manifest: dict[str, Any] | None,
) -> str:
    """Classify a sibling transaction without granting cleanup authority."""
    if candidate.parent != final_target.parent:
        return "unsafe_parent"
    if candidate.exists() and (is_link_like(candidate) or not candidate.is_dir()):
        return "unsafe_type"
    legacy_prefixes = (
        f"{final_target.name}.prepare-",
        f".{final_target.name}.prepare-",
        f"{final_target.name}-prepare-",
    )
    if candidate.name.startswith(legacy_prefixes):
        return "legacy"
    match = TRANSACTION_NAME.fullmatch(candidate.name)
    if match is None:
        return "unrelated"
    if match.group("prefix") != target_identity_sha256[:16]:
        return "unrelated"
    if not isinstance(manifest, dict):
        return "stale"
    if manifest.get("target_identity_sha256") != target_identity_sha256:
        return "identity_collision"
    if manifest.get("attempt_id") != attempt_id:
        return "stale"
    return "current"


def transaction_cleanup_allowed(
    candidate: Path,
    final_target: Path,
    target_identity_sha256: str,
    attempt_id: str,
    manifest: dict[str, Any] | None,
    created_paths: set[Path],
) -> bool:
    """Authorize no mutation; return whether an exact caller-owned path may be cleaned."""
    return (
        candidate in created_paths
        and classify_transaction_candidate(
            candidate, final_target, target_identity_sha256, attempt_id, manifest,
        ) == "current"
    )


def finding(code: str, severity: str, message: str, path: str = "$") -> dict[str, str]:
    return {"code": code, "severity": severity, "path": path, "message": message}


def require_fields(
    value: dict[str, Any], fields: set[str], findings: list[dict[str, str]], path: str = "$",
) -> None:
    for name in sorted(fields - value.keys()):
        findings.append(finding("missing-field", "invalid", f"required field is missing: {name}", path))


def valid_timestamp(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return "T" in value


def valid_project_path(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and not re.match(r"^[A-Za-z]:", value)


def valid_ref(value: object) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == {"path", "sha256"}
        and valid_project_path(value.get("path"))
        and isinstance(value.get("sha256"), str)
        and bool(SHA256.fullmatch(value["sha256"]))
    )


@lru_cache(maxsize=8)
def load_schema(name: str) -> dict[str, Any]:
    value = json.loads((SCHEMA_ROOT / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"schema root is not an object: {name}")
    return value


def _matches_json_type(value: object, expected: str) -> bool:
    if expected == "null":
        return value is None
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "string":
        return isinstance(value, str)
    if expected == "array":
        return isinstance(value, list)
    if expected == "object":
        return isinstance(value, dict)
    return False


def _schema_errors(
    value: object,
    schema: dict[str, Any],
    root_schema: dict[str, Any],
    path: str,
) -> list[str]:
    if "$ref" in schema:
        reference = schema["$ref"]
        if not isinstance(reference, str) or not reference.startswith("#/$defs/"):
            return [f"{path}: unsupported schema reference {reference!r}"]
        name = reference[len("#/$defs/"):]
        target = root_schema.get("$defs", {}).get(name)
        if not isinstance(target, dict):
            return [f"{path}: unresolved schema reference {reference}"]
        return _schema_errors(value, target, root_schema, path)
    if "oneOf" in schema:
        branches = schema["oneOf"]
        matches = [branch for branch in branches if not _schema_errors(value, branch, root_schema, path)]
        if len(matches) != 1:
            return [f"{path}: value must match exactly one schema alternative"]
        return []
    if "const" in schema and value != schema["const"]:
        return [f"{path}: value does not equal required constant"]
    if "enum" in schema and value not in schema["enum"]:
        return [f"{path}: value is outside the allowed enumeration"]
    expected = schema.get("type")
    if expected is not None:
        expected_types = [expected] if isinstance(expected, str) else expected
        if not isinstance(expected_types, list) or not any(
            isinstance(item, str) and _matches_json_type(value, item) for item in expected_types
        ):
            return [f"{path}: value has the wrong JSON type"]
    errors: list[str] = []
    if isinstance(value, dict):
        required = schema.get("required", [])
        if isinstance(required, list):
            for name in required:
                if name not in value:
                    errors.append(f"{path}: missing required property {name}")
        properties = schema.get("properties", {})
        if isinstance(properties, dict):
            if schema.get("additionalProperties") is False:
                for name in value.keys() - properties.keys():
                    errors.append(f"{path}: additional property is forbidden: {name}")
            for name, child in properties.items():
                if name in value and isinstance(child, dict):
                    errors.extend(_schema_errors(value[name], child, root_schema, f"{path}.{name}"))
    elif isinstance(value, list):
        if isinstance(schema.get("minItems"), int) and len(value) < schema["minItems"]:
            errors.append(f"{path}: array has fewer than {schema['minItems']} items")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(_schema_errors(item, item_schema, root_schema, f"{path}[{index}]"))
    elif isinstance(value, str):
        if isinstance(schema.get("minLength"), int) and len(value) < schema["minLength"]:
            errors.append(f"{path}: string is shorter than {schema['minLength']}")
        if isinstance(schema.get("maxLength"), int) and len(value) > schema["maxLength"]:
            errors.append(f"{path}: string is longer than {schema['maxLength']}")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.search(pattern, value) is None:
            errors.append(f"{path}: string does not match {pattern}")
        if schema.get("format") == "date-time" and not valid_timestamp(value):
            errors.append(f"{path}: string is not an ISO date-time")
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        if isinstance(minimum, (int, float)) and value < minimum:
            errors.append(f"{path}: number is below {minimum}")
    return errors


def validate_schema_document(value: dict[str, Any], schema_name: str) -> list[dict[str, str]]:
    schema = load_schema(schema_name)
    return [
        finding("schema-violation", "invalid", message)
        for message in _schema_errors(value, schema, schema, "$")
    ]


def validate_hash(value: dict[str, Any], field: str, findings: list[dict[str, str]]) -> None:
    actual = value.get(field)
    if not isinstance(actual, str) or not SHA256.fullmatch(actual):
        findings.append(finding("invalid-hash", "invalid", f"{field} must be lowercase SHA-256", f"$.{field}"))
    elif actual != canonical_hash(value, field):
        findings.append(finding("hash-mismatch", "stale", f"{field} does not bind the current record", f"$.{field}"))


def validate_common_identity(value: dict[str, Any], findings: list[dict[str, str]]) -> None:
    for field in ("issue_id", "attempt_id", "stage_id"):
        if field in value and (not isinstance(value[field], str) or not STABLE_ID.fullmatch(value[field])):
            findings.append(finding("invalid-id", "invalid", f"{field} is not a stable identifier", f"$.{field}"))
    for field in ("base_sha", "head_sha"):
        if field in value and (not isinstance(value[field], str) or not OBJECT_ID.fullmatch(value[field])):
            findings.append(finding("invalid-object-id", "invalid", f"{field} must be a 40- or 64-digit lowercase object ID", f"$.{field}"))


def validate_repair(record: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    required = {
        "schema_version", "issue_id", "revision", "supersedes", "record_sha256", "title",
        "classification", "failure_signature", "discovered_at", "source_control", "environment",
        "reproduction", "root_cause", "invalidation", "repair_state", "state_history",
        "run_authorization", "plan_ref", "authorization", "implementation", "verification",
        "action_boundary", "residual_risks", "closure_evidence",
        "closed_at", "closed_by", "blocked_from", "blocker", "unblock_condition",
    }
    require_fields(record, required, findings)
    if record.get("schema_version") != REPAIR_SCHEMA:
        findings.append(finding("unsupported-schema", "invalid", f"expected {REPAIR_SCHEMA}"))
        return findings
    findings.extend(validate_schema_document(record, "engineering-repair-record.schema.json"))
    validate_hash(record, "record_sha256", findings)
    validate_common_identity(record, findings)
    if not isinstance(record.get("revision"), int) or record.get("revision", 0) < 1:
        findings.append(finding("invalid-revision", "invalid", "revision must be a positive integer", "$.revision"))
    if record.get("classification") not in FAILURE_CLASSES - {"none"}:
        findings.append(finding("invalid-classification", "invalid", "classification is not recognized", "$.classification"))
    if not valid_timestamp(record.get("discovered_at")):
        findings.append(finding("invalid-timestamp", "invalid", "discovered_at must be an ISO timestamp", "$.discovered_at"))

    source = record.get("source_control")
    if not isinstance(source, dict):
        findings.append(finding("invalid-source-control", "invalid", "source_control must be an object", "$.source_control"))
    else:
        require_fields(source, {"base_sha", "head_sha", "branch", "remote", "remote_ref"}, findings, "$.source_control")
        validate_common_identity(source, findings)

    history = record.get("state_history")
    current: str | None = None
    if not isinstance(history, list) or not history:
        findings.append(finding("invalid-state-history", "invalid", "state_history must be non-empty", "$.state_history"))
    else:
        for index, event in enumerate(history):
            location = f"$.state_history[{index}]"
            if not isinstance(event, dict):
                findings.append(finding("invalid-state-event", "invalid", "state event must be an object", location))
                continue
            require_fields(event, {"from", "to", "at", "actor", "evidence_refs", "decision_ref"}, findings, location)
            before, after = event.get("from"), event.get("to")
            if index == 0 and (before is not None or after != "reported"):
                findings.append(finding("invalid-initial-state", "invalid", "history must begin null -> reported", location))
            if index > 0 and before != current:
                findings.append(finding("state-chain-broken", "invalid", "event.from does not match the previous event", location))
            if after not in set(NORMAL_STATES) | EXCEPTION_STATES:
                findings.append(finding("invalid-state", "invalid", f"unknown repair state: {after}", location))
            elif index > 0 and before in NORMAL_STATES and after in NORMAL_STATES:
                if NORMAL_STATES.index(after) != NORMAL_STATES.index(before) + 1:
                    findings.append(finding("invalid-transition", "invalid", f"transition {before} -> {after} skips or reverses the lifecycle", location))
            elif before == "blocked" and after != record.get("blocked_from"):
                findings.append(finding("invalid-unblock", "invalid", "blocked may resume only to blocked_from", location))
            elif before == "stale" and after not in {"reproduced", "planned"}:
                findings.append(finding("invalid-stale-reentry", "invalid", "stale may re-enter only at reproduced or planned", location))
            elif before == "rolled_back" and after != "planned":
                findings.append(finding("invalid-rollback-reentry", "invalid", "rolled_back requires a new planned attempt", location))
            if not valid_timestamp(event.get("at")):
                findings.append(finding("invalid-timestamp", "invalid", "state event timestamp is invalid", location))
            refs = event.get("evidence_refs")
            if not isinstance(refs, list) or any(not valid_ref(item) for item in refs):
                findings.append(finding("invalid-evidence-ref", "invalid", "state evidence_refs are invalid", location))
            current = after if isinstance(after, str) else current
    if current is not None and record.get("repair_state") != current:
        findings.append(finding("current-state-mismatch", "stale", "repair_state does not equal the last valid event", "$.repair_state"))
    if record.get("repair_state") == "blocked":
        if record.get("blocked_from") not in NORMAL_STATES or not record.get("blocker") or not record.get("unblock_condition"):
            findings.append(finding("incomplete-blocker", "incomplete", "blocked state needs blocked_from, blocker, and unblock_condition"))

    authorization = record.get("authorization")
    state = record.get("repair_state")
    if state in {"approved", "fixed", "locally_verified", "ci_verified", "closed"}:
        if not isinstance(authorization, dict) or authorization.get("state") != "granted" or not valid_ref(authorization.get("decision_ref")):
            findings.append(finding("missing-repair-authorization", "incomplete", "approved or later repair state needs a granted decision reference", "$.authorization"))
    implementation = record.get("implementation")
    if state in {"fixed", "locally_verified", "ci_verified", "closed"}:
        if not isinstance(implementation, dict) or not implementation.get("execution_receipt_refs"):
            findings.append(finding("missing-execution-receipt", "incomplete", "fixed or later state needs an execution receipt", "$.implementation"))
    verification = record.get("verification")
    if state in {"locally_verified", "ci_verified", "closed"}:
        if not isinstance(verification, dict) or not verification.get("test_layers"):
            findings.append(finding("missing-local-verification", "incomplete", "locally_verified or later state needs test layers", "$.verification"))
    if state in {"ci_verified", "closed"}:
        if not isinstance(verification, dict) or not valid_ref(verification.get("ci_evidence_ref")):
            findings.append(finding("missing-ci-evidence", "incomplete", "ci_verified or closed state needs CI evidence", "$.verification.ci_evidence_ref"))
    if state == "closed":
        if not valid_ref(record.get("closure_evidence")) or not valid_timestamp(record.get("closed_at")) or not record.get("closed_by"):
            findings.append(finding("incomplete-closure", "incomplete", "closed state needs closure evidence, time, and actor"))

    run = record.get("run_authorization")
    if not isinstance(run, dict) or run.get("state") not in RUN_STATES:
        findings.append(finding("invalid-run-state", "invalid", "run_authorization has an invalid independent state", "$.run_authorization"))
    else:
        run_history = run.get("state_history")
        last_run_state: str | None = None
        last_milestone = "not_started"
        stale_reentry = False
        if not isinstance(run_history, list) or not run_history:
            findings.append(finding("invalid-run-history", "invalid", "run state_history must be non-empty", "$.run_authorization.state_history"))
        else:
            for index, event in enumerate(run_history):
                location = f"$.run_authorization.state_history[{index}]"
                if not isinstance(event, dict):
                    findings.append(finding("invalid-run-event", "invalid", "run event must be an object", location))
                    continue
                require_fields(event, {"from", "to", "at", "authorization_ref", "execution_receipt_ref", "evidence_refs"}, findings, location)
                before, after = event.get("from"), event.get("to")
                if index == 0 and (before is not None or after != "not_started"):
                    findings.append(finding("invalid-run-initial-state", "invalid", "run history must begin null -> not_started", location))
                if index > 0 and before != last_run_state:
                    findings.append(finding("run-state-chain-broken", "invalid", "run event.from does not match the previous event", location))
                allowed = False
                if index == 0:
                    allowed = before is None and after == "not_started"
                elif after == "stale":
                    allowed = before in RUN_STATES - {"stale"}
                    stale_reentry = True
                elif before == "stale":
                    allowed = after == "awaiting_authorization"
                elif before == "not_started":
                    allowed = after == "awaiting_authorization"
                elif before in {"prepared", "canary_passed"}:
                    allowed = after == "awaiting_authorization"
                    last_milestone = before
                elif before == "awaiting_authorization":
                    expected = {"not_started": "prepared", "prepared": "canary_passed", "canary_passed": "full_authorized"}.get(last_milestone)
                    allowed = after in {"prepared", "canary_passed", "full_authorized"} if stale_reentry else after == expected
                if not allowed:
                    findings.append(finding("invalid-run-transition", "invalid", f"invalid run transition {before} -> {after}", location))
                if after in {"prepared", "canary_passed", "full_authorized"}:
                    if not valid_ref(event.get("authorization_ref")) or not valid_ref(event.get("execution_receipt_ref")):
                        findings.append(finding("missing-stage-authorization", "incomplete", "prepare, canary, and full authorization transitions need separate authorization and receipt references", location))
                    last_milestone = after
                    stale_reentry = False
                if not valid_timestamp(event.get("at")):
                    findings.append(finding("invalid-timestamp", "invalid", "run event timestamp is invalid", location))
                last_run_state = after if isinstance(after, str) else last_run_state
        if last_run_state is not None and run.get("state") != last_run_state:
            findings.append(finding("run-current-state-mismatch", "stale", "run state does not equal its last event", "$.run_authorization.state"))
        if run.get("state") in {"prepared", "canary_passed", "full_authorized"} and not valid_ref(run.get("authorization_ref")):
            findings.append(finding("missing-run-authorization", "incomplete", "advanced run state needs its own authorization reference", "$.run_authorization.authorization_ref"))
    return findings


def validate_plan(plan: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    required = {
        "schema_version", "plan_id", "plan_sha256", "issue_id", "attempt_id", "base_sha", "head_sha",
        "worktree_fingerprint_sha256", "code_fingerprint_sha256", "campaign_binding", "profile_binding",
        "stage_id", "predecessor_receipt_ref", "authorization_ref", "commands", "planned_writes",
        "protected_paths", "side_effects", "transaction", "stop_conditions", "required_verification",
    }
    require_fields(plan, required, findings)
    if plan.get("schema_version") != PLAN_SCHEMA:
        findings.append(finding("unsupported-schema", "invalid", f"expected {PLAN_SCHEMA}"))
        return findings
    findings.extend(validate_schema_document(plan, "engineering-execution-plan.schema.json"))
    validate_hash(plan, "plan_sha256", findings)
    validate_common_identity(plan, findings)
    if not STABLE_ID.fullmatch(str(plan.get("plan_id", ""))):
        findings.append(finding("invalid-id", "invalid", "plan_id is invalid", "$.plan_id"))
    for field in ("worktree_fingerprint_sha256", "code_fingerprint_sha256"):
        if not SHA256.fullmatch(str(plan.get(field, ""))):
            findings.append(finding("invalid-hash", "invalid", f"{field} is invalid", f"$.{field}"))
    for field in ("campaign_binding", "profile_binding"):
        binding = plan.get(field)
        if not isinstance(binding, dict) or binding.get("status") not in {"bound", "not_applicable"}:
            findings.append(finding("invalid-binding", "invalid", f"{field} is invalid", f"$.{field}"))
        elif binding["status"] == "bound" and not valid_ref(binding.get("ref")):
            findings.append(finding("missing-binding-ref", "incomplete", f"bound {field} needs ref", f"$.{field}"))
        elif binding["status"] == "not_applicable" and (binding.get("ref") is not None or not valid_ref(binding.get("decision_ref"))):
            findings.append(finding("missing-na-decision", "incomplete", f"not_applicable {field} needs a decision_ref and null ref", f"$.{field}"))
    commands = plan.get("commands")
    if not isinstance(commands, list) or not commands:
        findings.append(finding("missing-commands", "invalid", "commands must be non-empty", "$.commands"))
    elif any(not isinstance(row, dict) or not valid_project_path(row.get("cwd")) or not isinstance(row.get("argv"), list) or not row["argv"] for row in commands):
        findings.append(finding("invalid-command", "invalid", "each command needs project-relative cwd and argv", "$.commands"))
    transaction = plan.get("transaction")
    if not isinstance(transaction, dict):
        findings.append(finding("invalid-transaction", "invalid", "transaction must be an object", "$.transaction"))
    else:
        identity = transaction.get("target_identity_sha256")
        prefix = transaction.get("name_prefix")
        if not SHA256.fullmatch(str(identity or "")) or not isinstance(prefix, str) or f"-{str(identity)[:16]}-" not in prefix:
            findings.append(finding("identity-prefix-mismatch", "invalid", "transaction name prefix must bind the first 16 digits of the full target identity", "$.transaction"))
        budget = transaction.get("path_budget")
        if not isinstance(budget, dict):
            findings.append(finding("missing-path-budget", "invalid", "transaction path budget is required", "$.transaction.path_budget"))
        else:
            required_budget = {"portable_limit_chars", "final_path_chars", "legacy_staging_path_chars", "staging_path_chars", "max_descendant_relative_chars"}
            require_fields(budget, required_budget, findings, "$.transaction.path_budget")
            if all(isinstance(budget.get(key), int) for key in required_budget):
                if budget["staging_path_chars"] + budget["max_descendant_relative_chars"] > budget["portable_limit_chars"]:
                    findings.append(finding("path-budget-exceeded", "incomplete", "staging plus descendants exceeds the declared portable limit", "$.transaction.path_budget"))
    return findings


def validate_receipt(receipt: dict[str, Any], plan: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    required = {
        "schema_version", "receipt_id", "receipt_sha256", "supersedes", "plan_id", "plan_sha256",
        "issue_id", "attempt_id", "stage_id", "base_sha", "head_sha", "worktree_fingerprint_sha256",
        "code_fingerprint_sha256", "operator", "delegation", "started_at", "finished_at", "commands",
        "changed_files", "write_reconciliation", "cleanup", "rollback", "partial_output", "commit", "push",
        "ci", "failure_class", "handoff_state",
    }
    require_fields(receipt, required, findings)
    if receipt.get("schema_version") != RECEIPT_SCHEMA:
        findings.append(finding("unsupported-schema", "invalid", f"expected {RECEIPT_SCHEMA}"))
        return findings
    findings.extend(validate_schema_document(receipt, "engineering-execution-receipt.schema.json"))
    validate_hash(receipt, "receipt_sha256", findings)
    validate_common_identity(receipt, findings)
    bindings = (
        "plan_id", "plan_sha256", "issue_id", "attempt_id", "stage_id", "base_sha", "head_sha",
        "worktree_fingerprint_sha256", "code_fingerprint_sha256",
    )
    for field in bindings:
        if receipt.get(field) != plan.get(field):
            findings.append(finding("plan-receipt-mismatch", "stale", f"receipt {field} does not match plan", f"$.{field}"))
    delegation = receipt.get("delegation")
    if not isinstance(delegation, dict) or delegation.get("requested_plan_sha256") != plan.get("plan_sha256"):
        findings.append(finding("delegation-plan-mismatch", "stale", "delegation does not bind the requested plan", "$.delegation"))
    operator = receipt.get("operator")
    if not isinstance(operator, dict) or operator.get("kind") not in {"human", "agent", "automation"} or not operator.get("id"):
        findings.append(finding("missing-operator", "invalid", "receipt needs a stable operator", "$.operator"))
    if not valid_timestamp(receipt.get("started_at")) or not valid_timestamp(receipt.get("finished_at")):
        findings.append(finding("invalid-timestamp", "invalid", "receipt timestamps are invalid"))
    commands = receipt.get("commands")
    if not isinstance(commands, list) or not commands:
        findings.append(finding("missing-command-results", "incomplete", "receipt must record every command result", "$.commands"))
    else:
        planned_commands = plan.get("commands")
        observed = [{"cwd": row.get("cwd"), "argv": row.get("argv")} for row in commands if isinstance(row, dict)]
        if observed != planned_commands:
            findings.append(finding("command-plan-mismatch", "stale", "executed command list differs from the plan", "$.commands"))
        for index, row in enumerate(commands):
            if not isinstance(row, dict) or not isinstance(row.get("exit_code"), int):
                findings.append(finding("missing-exit-code", "invalid", "command result lacks an integer exit code", f"$.commands[{index}]"))
            elif row["exit_code"] != 0:
                findings.append(finding("command-failed", "incomplete", "an executed command returned non-zero", f"$.commands[{index}]"))
    reconciliation = receipt.get("write_reconciliation")
    if not isinstance(reconciliation, dict):
        findings.append(finding("missing-write-reconciliation", "invalid", "write reconciliation is required"))
    else:
        if reconciliation.get("planned") != plan.get("planned_writes"):
            findings.append(finding("planned-write-mismatch", "stale", "receipt planned writes differ from plan", "$.write_reconciliation.planned"))
        if reconciliation.get("unexpected"):
            findings.append(finding("unexpected-writes", "incomplete", "receipt reports writes outside the plan", "$.write_reconciliation.unexpected"))
    if receipt.get("cleanup") in {"incomplete", "failed"} or receipt.get("rollback") in {"incomplete", "failed"} or receipt.get("partial_output") in {"retained", "unknown"}:
        findings.append(finding("unsafe-partial-state", "incomplete", "cleanup, rollback, or partial output is unresolved"))
    if receipt.get("failure_class") not in FAILURE_CLASSES:
        findings.append(finding("invalid-failure-class", "invalid", "failure_class is invalid", "$.failure_class"))
    push = receipt.get("push")
    if not isinstance(push, dict):
        findings.append(finding("invalid-push-state", "invalid", "push must be an object", "$.push"))
    else:
        push_required = {"status", "evidence_ref", "remote", "updates", "fast_forward_verified", "atomic", "forced", "protection_rejected"}
        require_fields(push, push_required, findings, "$.push")
        if push.get("forced"):
            findings.append(finding("force-push-forbidden", "invalid", "v1 receipts must never report an allowed force push", "$.push.forced"))
        if push.get("protection_rejected") and push.get("status") == "succeeded":
            findings.append(finding("protection-rejection-ignored", "invalid", "a protection rejection must stop the push", "$.push"))
        updates = push.get("updates")
        if push.get("status") == "succeeded":
            if not push.get("remote") or not push.get("fast_forward_verified") or not isinstance(updates, list) or not updates:
                findings.append(finding("incomplete-push-proof", "incomplete", "successful push needs remote, ref updates, and fast-forward proof", "$.push"))
            elif len(updates) > 1 and push.get("atomic") is not True:
                findings.append(finding("non-atomic-multi-ref", "invalid", "multi-ref push must be atomic", "$.push.atomic"))
        if isinstance(updates, list):
            for index, update in enumerate(updates):
                if (
                    not isinstance(update, dict)
                    or not str(update.get("ref", "")).startswith("refs/")
                    or not OBJECT_ID.fullmatch(str(update.get("remote_before", "")))
                    or not OBJECT_ID.fullmatch(str(update.get("remote_after", "")))
                ):
                    findings.append(finding("invalid-push-update", "invalid", "push update lacks exact ref and object IDs", f"$.push.updates[{index}]"))
    return findings


def validate_ci(evidence: dict[str, Any], expected_head: str | None = None) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    required = {
        "schema_version", "evidence_sha256", "repository", "queried_at", "head_sha", "api_query",
        "pagination_complete", "total_count", "runs", "required_check_policy_ref", "status",
        "supplemental_legacy_statuses",
    }
    require_fields(evidence, required, findings)
    if evidence.get("schema_version") != CI_SCHEMA:
        findings.append(finding("unsupported-schema", "invalid", f"expected {CI_SCHEMA}"))
        return findings
    findings.extend(validate_schema_document(evidence, "github-actions-evidence.schema.json"))
    validate_hash(evidence, "evidence_sha256", findings)
    head = evidence.get("head_sha")
    if not isinstance(head, str) or not OBJECT_ID.fullmatch(head):
        findings.append(finding("invalid-object-id", "invalid", "head_sha is invalid", "$.head_sha"))
    if expected_head is not None and head != expected_head:
        findings.append(finding("ci-head-mismatch", "stale", "CI evidence is for a different commit", "$.head_sha"))
    query = evidence.get("api_query")
    if not isinstance(query, dict) or query.get("head_sha") != head or query.get("branch_filter") is not None:
        findings.append(finding("unsafe-actions-query", "invalid", "Actions must first be queried by head SHA without a branch filter", "$.api_query"))
    runs = evidence.get("runs")
    if not evidence.get("pagination_complete") or not isinstance(runs, list) or evidence.get("total_count") != len(runs):
        findings.append(finding("incomplete-actions-pagination", "incomplete", "Actions pagination or run count is incomplete"))
    if isinstance(runs, list):
        for index, run in enumerate(runs):
            if not isinstance(run, dict) or run.get("head_sha") != head:
                findings.append(finding("run-head-mismatch", "stale", "workflow run is not bound to the queried head", f"$.runs[{index}]"))
                continue
            if not run.get("jobs"):
                findings.append(finding("missing-jobs", "incomplete", "workflow run has no job evidence", f"$.runs[{index}].jobs"))
    if evidence.get("status") == "passed":
        if not runs:
            findings.append(finding("empty-ci-pass", "incomplete", "CI cannot pass without Actions runs"))
        elif any(run.get("status") != "completed" or run.get("conclusion") != "success" for run in runs if isinstance(run, dict)):
            findings.append(finding("ci-status-contradiction", "invalid", "passed evidence contains a non-successful run"))
    if not valid_ref(evidence.get("required_check_policy_ref")):
        findings.append(finding("missing-check-policy", "incomplete", "required-check policy reference is invalid"))
    return findings


def overall(findings: list[dict[str, str]]) -> tuple[str, int]:
    severities = {row["severity"] for row in findings}
    if "invalid" in severities:
        return "invalid", 2
    if "stale" in severities:
        return "stale", 1
    if "incomplete" in severities:
        return "incomplete", 1
    return "valid", 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    repair = subparsers.add_parser("repair", help="validate one repair record")
    repair.add_argument("project")
    repair.add_argument("--record", required=True)
    execution = subparsers.add_parser("execution", help="cross-validate one plan and receipt")
    execution.add_argument("project")
    execution.add_argument("--plan", required=True)
    execution.add_argument("--receipt", required=True)
    bundle = subparsers.add_parser("bundle", help="cross-validate repair, plan, receipts, and CI")
    bundle.add_argument("project")
    bundle.add_argument("--record", required=True)
    bundle.add_argument("--plan", required=True)
    bundle.add_argument("--receipt", action="append", default=[])
    bundle.add_argument("--ci-evidence")
    return parser.parse_args(argv)


def evaluate(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    root = resolve_project(args.project)
    findings: list[dict[str, str]] = []
    checked: list[str] = []
    if args.command == "repair":
        record = load_record(root, args.record)
        checked.append(args.record)
        findings.extend(validate_repair(record))
    elif args.command == "execution":
        plan = load_record(root, args.plan)
        receipt = load_record(root, args.receipt)
        checked.extend([args.plan, args.receipt])
        findings.extend(validate_plan(plan))
        findings.extend(validate_receipt(receipt, plan))
    else:
        record = load_record(root, args.record)
        plan = load_record(root, args.plan)
        checked.extend([args.record, args.plan])
        findings.extend(validate_repair(record))
        findings.extend(validate_plan(plan))
        plan_ref = record.get("plan_ref")
        if not valid_ref(plan_ref) or plan_ref.get("sha256") != plan.get("plan_sha256"):
            findings.append(finding("repair-plan-mismatch", "stale", "repair record does not bind the supplied plan", "$.plan_ref"))
        receipts = []
        for raw in args.receipt:
            receipt = load_record(root, raw)
            checked.append(raw)
            receipts.append(receipt)
            findings.extend(validate_receipt(receipt, plan))
        if record.get("repair_state") in {"fixed", "locally_verified", "ci_verified", "closed"} and not receipts:
            findings.append(finding("missing-receipt", "incomplete", "the current repair state requires a receipt"))
        ci = None
        if args.ci_evidence:
            ci = load_record(root, args.ci_evidence)
            checked.append(args.ci_evidence)
            findings.extend(validate_ci(ci, record.get("source_control", {}).get("head_sha")))
        if record.get("repair_state") in {"ci_verified", "closed"} and ci is None:
            findings.append(finding("missing-ci-evidence", "incomplete", "the current repair state requires CI evidence"))
    status, code = overall(findings)
    return {
        "schema_version": RESULT_SCHEMA,
        "status": status,
        "commands_executed": False,
        "checked_records": checked,
        "findings": findings,
    }, code


def main(argv: list[str]) -> int:
    try:
        result, code = evaluate(parse_args(argv))
    except (OSError, UnsafeInput, ValueError) as exc:
        result = {
            "schema_version": RESULT_SCHEMA,
            "status": "invalid",
            "commands_executed": False,
            "checked_records": [],
            "findings": [finding("unsafe-input", "invalid", str(exc))],
        }
        code = 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
