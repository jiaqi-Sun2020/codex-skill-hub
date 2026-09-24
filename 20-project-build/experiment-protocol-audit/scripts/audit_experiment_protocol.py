#!/usr/bin/env python3
"""Audit declared experiment protocols without executing project code."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any


RESULT_SCHEMA_V1 = "experiment-protocol-audit-result/v1"
RESULT_SCHEMA_V2 = "experiment-protocol-audit-result/v2"
PROFILE_SCHEMA_V1 = "experiment-domain-profile/v1"
PROFILE_SCHEMA_V2 = "experiment-domain-profile/v2"
PROTOCOL_SCHEMA_V1 = "experiment-project-protocol/v1"
PROTOCOL_SCHEMA_V2 = "experiment-project-protocol/v2"
OBSERVATION_SCHEMA = "experiment-runtime-observation/v1"
MANIFEST_SCHEMA = "experiment-cell-manifest/v1"
RUNTIME_SCHEMA = "experiment-runtime-evidence/v1"
VALIDATOR_ID = "experiment-protocol-audit"
VALIDATOR_VERSION = "2.0.0"
MAX_INPUT_BYTES = 5 * 1024 * 1024
CLAIM_LEVELS = {"unsupported", "diagnostic_only", "conditionally_supported", "supported"}
RULE_TYPES = {
    "numeric-bound", "equality", "shape-equality", "set-equality",
    "cardinality", "allowed-transform",
}
MANUAL_REVIEW_FIELDS = {"id", "reviewer_ref", "decision", "scopes", "path", "sha256"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def linked_component_below(root: Path, target: Path) -> Path | None:
    try:
        relative = target.absolute().relative_to(root.absolute())
    except ValueError:
        return target
    current = root
    for part in relative.parts:
        current = current / part
        if current.exists() and is_link_like(current):
            return current
    return None


def project_root(raw: str) -> Path:
    unresolved = Path(raw).expanduser().absolute()
    current = Path(unresolved.anchor)
    for part in unresolved.parts[1:]:
        current = current / part
        if current.exists() and is_link_like(current):
            raise ValueError(f"project root traverses a link or junction: {current}")
    root = unresolved.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("project root must be a directory")
    return root


def contained_file(root: Path, raw: str, label: str) -> Path:
    supplied = Path(raw).expanduser()
    if ".." in supplied.parts:
        raise ValueError(f"{label} must not contain parent traversal")
    candidate = supplied if supplied.is_absolute() else root / supplied
    unresolved = candidate.absolute()
    try:
        unresolved.relative_to(root.absolute())
    except ValueError as exc:
        raise ValueError(f"{label} must stay inside the project root") from exc
    linked = linked_component_below(root, unresolved)
    if linked is not None:
        raise ValueError(f"{label} must not traverse a link or junction: {linked}")
    resolved = unresolved.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"{label} escapes the project root") from exc
    if not resolved.is_file() or is_link_like(resolved):
        raise ValueError(f"{label} must be a regular non-linked file")
    if resolved.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError(f"{label} exceeds 5 MiB")
    return resolved


def load_json(root: Path, raw: str, label: str) -> tuple[Path, dict[str, Any]]:
    path = contained_file(root, raw, label)
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{label} must contain a JSON object")
    return path, value


def relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def get_observation(observations: dict[str, Any], dotted: str) -> Any:
    if not isinstance(dotted, str) or not dotted or any(not part for part in dotted.split(".")):
        raise ValueError("observation paths must be non-empty dot-separated object keys")
    current: Any = observations
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            raise KeyError(dotted)
        current = current[part]
    return current


def finding(
    code: str,
    rule_id: str,
    obj: str,
    expected: Any,
    actual: Any,
    risk: str,
) -> dict[str, Any]:
    return {
        "code": code,
        "severity": "blocker",
        "rule_id": rule_id,
        "object": obj,
        "expected": expected,
        "actual": actual,
        "risk": risk,
        "minimum_fix": "Correct the declared protocol, normalized evidence, or implementation; then rerun the independent audit.",
        "verification": f"Rerun rule {rule_id} and confirm the finding is absent in a new fingerprint-bound record.",
    }


def numeric(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise ValueError(f"{label} must be a finite number")
    return float(value)


def compare_numeric(actual: float, operator: str, expected: float) -> bool:
    return {
        "<": actual < expected,
        "<=": actual <= expected,
        "==": actual == expected,
        ">=": actual >= expected,
        ">": actual > expected,
    }.get(operator, False)


def literal_or_path(rule: dict[str, Any], observations: dict[str, Any], prefix: str) -> tuple[Any, str]:
    path_key = f"{prefix}_path"
    value_key = f"{prefix}_value"
    has_path = path_key in rule
    has_value = value_key in rule
    if has_path == has_value:
        raise ValueError(f"rule {rule.get('id')} must declare exactly one of {path_key} or {value_key}")
    if has_path:
        path = rule[path_key]
        return get_observation(observations, path), str(path)
    return rule[value_key], value_key


def validate_shape(value: Any, label: str) -> list[int]:
    if not isinstance(value, list) or any(isinstance(item, bool) or not isinstance(item, int) or item < 0 for item in value):
        raise ValueError(f"{label} must be an array of non-negative integers")
    return value


def evaluate_rules(
    profile: dict[str, Any],
    observations: dict[str, Any],
    phases: set[str],
) -> list[dict[str, Any]]:
    rules = profile.get("rules")
    if not isinstance(rules, list):
        raise ValueError("domain profile rules must be an array")
    seen: set[str] = set()
    findings: list[dict[str, Any]] = []
    for rule in rules:
        if not isinstance(rule, dict):
            raise ValueError("every domain profile rule must be an object")
        rule_id = rule.get("id")
        rule_type = rule.get("type")
        phase = rule.get("phase", "design")
        if not isinstance(rule_id, str) or not rule_id or rule_id in seen:
            raise ValueError("domain profile rule IDs must be unique non-empty strings")
        seen.add(rule_id)
        if rule_type not in RULE_TYPES or phase not in {"design", "runtime"}:
            raise ValueError(f"rule {rule_id} has an unsupported type or phase")
        if phase not in phases:
            continue
        code = rule.get("code", "domain-rule-violation")
        if not isinstance(code, str) or not code:
            raise ValueError(f"rule {rule_id} needs a non-empty code")
        try:
            if rule_type == "numeric-bound":
                path = rule.get("input_path")
                operator = rule.get("operator")
                actual = numeric(get_observation(observations, path), f"rule {rule_id} observation")
                expected = numeric(rule.get("expected"), f"rule {rule_id} expected value")
                if operator not in {"<", "<=", "==", ">=", ">"}:
                    raise ValueError(f"rule {rule_id} has an unsupported numeric operator")
                passed = compare_numeric(actual, operator, expected)
                expected_display: Any = {"operator": operator, "value": expected}
                actual_display: Any = actual
                obj = str(path)
            elif rule_type == "equality":
                left, left_label = literal_or_path(rule, observations, "left")
                right, right_label = literal_or_path(rule, observations, "right")
                passed = left == right
                expected_display, actual_display, obj = right, left, f"{left_label} == {right_label}"
            elif rule_type == "shape-equality":
                left, left_label = literal_or_path(rule, observations, "left")
                right, right_label = literal_or_path(rule, observations, "right")
                left = validate_shape(left, f"rule {rule_id} left shape")
                right = validate_shape(right, f"rule {rule_id} right shape")
                passed = left == right
                expected_display, actual_display, obj = right, left, f"{left_label} shape == {right_label} shape"
            elif rule_type == "set-equality":
                left, left_label = literal_or_path(rule, observations, "left")
                right, right_label = literal_or_path(rule, observations, "right")
                if not isinstance(left, list) or not isinstance(right, list):
                    raise ValueError(f"rule {rule_id} set operands must be arrays")
                if len({json.dumps(item, sort_keys=True) for item in left}) != len(left) or len({json.dumps(item, sort_keys=True) for item in right}) != len(right):
                    raise ValueError(f"rule {rule_id} set operands must not contain duplicates")
                passed = {json.dumps(item, sort_keys=True) for item in left} == {json.dumps(item, sort_keys=True) for item in right}
                expected_display, actual_display, obj = right, left, f"{left_label} set == {right_label} set"
            elif rule_type == "cardinality":
                path = rule.get("input_path")
                value = get_observation(observations, path)
                if not isinstance(value, list):
                    raise ValueError(f"rule {rule_id} cardinality input must be an array")
                operator = rule.get("operator")
                expected_int = rule.get("expected")
                if isinstance(expected_int, bool) or not isinstance(expected_int, int) or expected_int < 0:
                    raise ValueError(f"rule {rule_id} expected cardinality must be a non-negative integer")
                passed = compare_numeric(float(len(value)), str(operator), float(expected_int))
                expected_display, actual_display, obj = {"operator": operator, "value": expected_int}, len(value), str(path)
            else:
                path = rule.get("input_path")
                allowed = rule.get("allowed")
                actual_value = get_observation(observations, path)
                if not isinstance(actual_value, str) or not isinstance(allowed, list) or not allowed or any(not isinstance(item, str) for item in allowed):
                    raise ValueError(f"rule {rule_id} allowed-transform needs a string observation and string allow-list")
                passed = actual_value in allowed
                expected_display, actual_display, obj = allowed, actual_value, str(path)
        except KeyError as exc:
            findings.append(finding(
                "missing-observation", rule_id, str(exc.args[0]), "declared observation", None,
                "The declared validation rule cannot be evaluated against the supplied evidence.",
            ))
            continue
        if not passed:
            findings.append(finding(
                code, rule_id, obj, expected_display, actual_display,
                "The observed project state violates an explicitly reviewed domain constraint.",
            ))
    return findings


def validate_profile_protocol(profile: dict[str, Any], protocol: dict[str, Any]) -> bool:
    profile_schema = profile.get("schema_version")
    protocol_schema = protocol.get("schema_version")
    supported_pairs = {
        (PROFILE_SCHEMA_V1, PROTOCOL_SCHEMA_V1),
        (PROFILE_SCHEMA_V2, PROTOCOL_SCHEMA_V2),
    }
    if (profile_schema, protocol_schema) not in supported_pairs:
        raise ValueError("profile and protocol must use one matching supported schema generation")
    for obj, fields, label in (
        (profile, ("profile_id", "version"), "profile"),
        (protocol, ("protocol_id", "version", "profile_id"), "protocol"),
    ):
        for field in fields:
            if not isinstance(obj.get(field), str) or not obj[field].strip():
                raise ValueError(f"{label} needs {field}")
    if protocol["profile_id"] != profile["profile_id"]:
        raise ValueError("protocol profile_id does not match the supplied profile")
    owner = protocol.get("owner")
    if not isinstance(owner, dict) or owner.get("kind") not in {"skill", "human"} or not isinstance(owner.get("id"), str) or not owner["id"].strip():
        raise ValueError("protocol needs a named skill or human owner")
    if protocol.get("claim_ceiling") not in CLAIM_LEVELS:
        raise ValueError("protocol claim_ceiling is invalid")
    sources = protocol.get("source_paths")
    if not isinstance(sources, list) or not sources or any(not isinstance(item, str) or not item for item in sources) or len(sources) != len(set(sources)):
        raise ValueError("protocol source_paths must be a non-empty unique string array")
    contract_aware = protocol_schema == PROTOCOL_SCHEMA_V2
    if contract_aware:
        bindings = protocol.get("contract_bindings")
        if not isinstance(bindings, list):
            raise ValueError("v2 protocol contract_bindings must be an array")
        seen: set[str] = set()
        for index, binding in enumerate(bindings):
            if not isinstance(binding, dict):
                raise ValueError(f"contract_bindings[{index}] must be an object")
            unknown_binding = set(binding) - {
                "instance_id", "applicability", "rule_ids", "audit_checks",
                "required_scopes", "manual_review_ref",
            }
            if unknown_binding:
                raise ValueError(f"contract_bindings[{index}] has unsupported fields")
            instance_id = binding.get("instance_id")
            if not isinstance(instance_id, str) or not instance_id.strip() or instance_id.casefold() in seen:
                raise ValueError("contract binding instance IDs must be unique non-empty strings")
            seen.add(instance_id.casefold())
            if binding.get("applicability") not in {"required", "optional"}:
                raise ValueError(f"contract binding {instance_id} applicability must be required or optional")
            rule_ids = binding.get("rule_ids")
            checks = binding.get("audit_checks")
            scopes = binding.get("required_scopes")
            if not isinstance(rule_ids, list) or any(not isinstance(item, str) or not item for item in rule_ids) or len(rule_ids) != len(set(rule_ids)):
                raise ValueError(f"contract binding {instance_id} rule_ids must be a unique string array")
            if not isinstance(checks, list) or any(item not in {"manifest-identity", "runtime-completeness"} for item in checks) or len(checks) != len(set(checks)):
                raise ValueError(f"contract binding {instance_id} audit_checks are invalid")
            if not isinstance(scopes, list) or not scopes or any(item not in {"design", "manifest", "runtime"} for item in scopes) or len(scopes) != len(set(scopes)):
                raise ValueError(f"contract binding {instance_id} required_scopes are invalid")
            manual = binding.get("manual_review_ref")
            if manual is not None:
                if not isinstance(manual, dict) or set(manual) != MANUAL_REVIEW_FIELDS:
                    raise ValueError(f"contract binding {instance_id} manual_review_ref is invalid")
                if any(not isinstance(manual.get(field), str) or not manual[field].strip() for field in ("id", "reviewer_ref")):
                    raise ValueError(f"contract binding {instance_id} manual review needs stable IDs")
                if manual["id"].casefold() == manual["reviewer_ref"].casefold():
                    raise ValueError(f"contract binding {instance_id} manual review must name an independent reviewer")
                if manual.get("decision") not in {"pass", "fail"}:
                    raise ValueError(f"contract binding {instance_id} manual review decision is invalid")
                manual_scopes = manual.get("scopes")
                if not isinstance(manual_scopes, list) or not manual_scopes or any(item not in {"design", "manifest", "runtime"} for item in manual_scopes) or len(manual_scopes) != len(set(manual_scopes)):
                    raise ValueError(f"contract binding {instance_id} manual review scopes are invalid")
                review_path = manual.get("path")
                if not isinstance(review_path, str) or not review_path or Path(review_path).is_absolute() or ".." in Path(review_path).parts:
                    raise ValueError(f"contract binding {instance_id} manual review path is invalid")
                digest = manual.get("sha256")
                if not isinstance(digest, str) or len(digest) != 64 or any(character not in "0123456789abcdefABCDEF" for character in digest):
                    raise ValueError(f"contract binding {instance_id} manual review sha256 is invalid")
    return contract_aware


def evaluate_contract_coverage(
    profile: dict[str, Any],
    protocol: dict[str, Any],
    scope: list[str],
    findings: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    bindings = protocol.get("contract_bindings", [])
    if not bindings:
        return [], [{
            "code": "contract-coverage-empty",
            "severity": "incomplete",
            "rule_id": "contract-coverage",
            "object": "contract_bindings",
            "risk": "A contract-aware protocol declares no auditable contract coverage.",
            "minimum_fix": "Bind each applicable machine-auditable contract to explicit rules or built-in audit checks.",
            "verification": "Rerun the v2 audit and confirm required bindings are covered.",
        }]
    rule_ids = {rule.get("id") for rule in profile.get("rules", []) if isinstance(rule, dict)}
    failed_rule_ids = {item.get("rule_id") for item in findings if item.get("severity") == "blocker"}
    current_scope = set(scope)
    coverage: list[dict[str, Any]] = []
    coverage_findings: list[dict[str, Any]] = []
    for binding in bindings:
        instance_id = binding["instance_id"]
        required_scopes = set(binding["required_scopes"])
        manual = binding.get("manual_review_ref")
        manual_scopes = set(manual["scopes"]) if manual else set()
        missing_rules = sorted(set(binding["rule_ids"]) - rule_ids)
        if missing_rules:
            status = "failed"
            coverage_findings.append({
                "code": "unknown-contract-rule",
                "severity": "blocker",
                "rule_id": "contract-coverage",
                "object": instance_id,
                "risk": f"The binding names unknown profile rules: {', '.join(missing_rules)}.",
                "minimum_fix": "Correct the binding or add reviewed rules to the Domain Profile.",
                "verification": "Rerun the audit and confirm every bound rule ID exists.",
            })
        elif not required_scopes <= current_scope:
            status = "not_in_scope"
        elif not binding["rule_ids"] and not binding["audit_checks"]:
            if manual and manual["decision"] == "pass" and required_scopes <= manual_scopes:
                status = "covered"
            elif manual and manual["decision"] == "fail":
                status = "failed"
            else:
                status = "incomplete"
        else:
            failed = bool(set(binding["rule_ids"]) & failed_rule_ids)
            if "manifest-identity" in binding["audit_checks"]:
                failed = failed or any(str(item.get("code", "")).startswith(("manifest-", "inactive-manifest")) for item in findings)
            if "runtime-completeness" in binding["audit_checks"]:
                failed = failed or any(str(item.get("code", "")).startswith("runtime-") for item in findings)
            failed = failed or bool(manual and manual["decision"] == "fail")
            status = "failed" if failed else "covered"
        coverage.append({
            "instance_id": instance_id,
            "applicability": binding["applicability"],
            "required_scopes": binding["required_scopes"],
            "rule_ids": binding["rule_ids"],
            "audit_checks": binding["audit_checks"],
            "manual_review_ref": manual,
            "status": status,
        })
        if binding["applicability"] == "required" and status == "incomplete":
            coverage_findings.append({
                "code": "required-contract-uncovered",
                "severity": "incomplete",
                "rule_id": "contract-coverage",
                "object": instance_id,
                "risk": "A required contract has no machine-auditable rule or built-in check.",
                "minimum_fix": "Add explicit reviewed coverage or record the required expert review through Governance.",
                "verification": "Rerun the audit and confirm the contract is covered or intentionally routed to Governance review.",
            })
    return coverage, coverage_findings


def manifest_cells(manifest: dict[str, Any], label: str) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    if manifest.get("schema_version") != MANIFEST_SCHEMA:
        raise ValueError(f"unsupported {label} manifest schema")
    cells = manifest.get("cells")
    if not isinstance(cells, list):
        raise ValueError(f"{label} manifest cells must be an array")
    mapping: dict[str, dict[str, Any]] = {}
    outputs: set[str] = set()
    for cell in cells:
        if not isinstance(cell, dict):
            raise ValueError(f"{label} manifest cells must be objects")
        cell_id = cell.get("id")
        output = cell.get("output_path")
        active = cell.get("active")
        if not isinstance(cell_id, str) or not cell_id or cell_id in mapping:
            raise ValueError(f"{label} manifest cell IDs must be unique non-empty strings")
        if not isinstance(output, str) or not output or output in outputs:
            raise ValueError(f"{label} manifest output paths must be unique non-empty strings")
        output_path = Path(output)
        if output_path.is_absolute() or ".." in output_path.parts:
            raise ValueError(f"{label} manifest output paths must be project-relative and traversal-free")
        if not isinstance(active, bool):
            raise ValueError(f"{label} manifest cells need boolean active")
        mapping[cell_id] = cell
        outputs.add(output)
    return cells, mapping


def compare_manifests(
    requested: dict[str, Any], generated: dict[str, Any], approved: dict[str, Any]
) -> list[dict[str, Any]]:
    _, requested_map = manifest_cells(requested, "requested")
    _, generated_map = manifest_cells(generated, "generated")
    _, approved_map = manifest_cells(approved, "approved")
    findings: list[dict[str, Any]] = []
    expected_ids = sorted(requested_map)
    for label, mapping in (("generated", generated_map), ("approved", approved_map)):
        actual_ids = sorted(mapping)
        if actual_ids != expected_ids:
            findings.append(finding(
                "manifest-set-mismatch", f"manifest-{label}-identity", label,
                expected_ids, actual_ids,
                "Requested work may have been silently removed, added, or substituted.",
            ))
        for cell_id in sorted(set(requested_map) & set(mapping)):
            if mapping[cell_id] != requested_map[cell_id]:
                findings.append(finding(
                    "manifest-cell-drift", f"manifest-{label}-{cell_id}", cell_id,
                    requested_map[cell_id], mapping[cell_id],
                    "The generated or approved cell no longer matches the reviewed request.",
                ))
        inactive = sorted(cell_id for cell_id, cell in mapping.items() if not cell["active"])
        if inactive:
            findings.append(finding(
                "inactive-manifest-cell", f"manifest-{label}-active", label,
                "all cells active", inactive,
                "A generated or approved manifest contains work that will not run.",
            ))
    return findings


def check_runtime(approved: dict[str, Any], runtime: dict[str, Any]) -> list[dict[str, Any]]:
    if runtime.get("schema_version") != RUNTIME_SCHEMA:
        raise ValueError("unsupported runtime evidence schema")
    _, approved_map = manifest_cells(approved, "approved")
    cells = runtime.get("cells")
    if not isinstance(cells, list):
        raise ValueError("runtime evidence cells must be an array")
    runtime_map: dict[str, dict[str, Any]] = {}
    for cell in cells:
        if not isinstance(cell, dict) or not isinstance(cell.get("id"), str) or not cell["id"] or cell["id"] in runtime_map:
            raise ValueError("runtime evidence cell IDs must be unique non-empty strings")
        runtime_map[cell["id"]] = cell
    findings: list[dict[str, Any]] = []
    if sorted(runtime_map) != sorted(approved_map):
        findings.append(finding(
            "runtime-set-mismatch", "runtime-approved-identity", "runtime cells",
            sorted(approved_map), sorted(runtime_map),
            "Runtime evidence does not cover exactly the approved work.",
        ))
    for cell_id in sorted(set(runtime_map) & set(approved_map)):
        item = runtime_map[cell_id]
        expected_output = approved_map[cell_id]["output_path"]
        if item.get("output_path") != expected_output or item.get("status") != "complete":
            findings.append(finding(
                "runtime-evidence-incomplete", f"runtime-{cell_id}", cell_id,
                {"output_path": expected_output, "status": "complete"},
                {"output_path": item.get("output_path"), "status": item.get("status")},
                "An approved cell lacks matching completed runtime evidence.",
            ))
    return findings


def fingerprint(root: Path, path: Path, *, kind: str | None = None) -> dict[str, str]:
    item = {"path": relative(root, path), "sha256": sha256_file(path)}
    if kind is not None:
        item["kind"] = kind
    return item


def write_output(root: Path, raw: str, payload: dict[str, Any], compact: bool) -> None:
    supplied = Path(raw).expanduser()
    if ".." in supplied.parts:
        raise ValueError("output must not contain parent traversal")
    candidate = supplied if supplied.is_absolute() else root / supplied
    unresolved = candidate.absolute()
    try:
        unresolved.relative_to(root.absolute())
    except ValueError as exc:
        raise ValueError("output must stay inside the project root") from exc
    if linked_component_below(root, unresolved.parent) is not None:
        raise ValueError("output parent must not traverse a link or junction")
    if not unresolved.parent.is_dir():
        raise ValueError("output parent must already exist")
    if unresolved.exists() or unresolved.is_symlink():
        raise FileExistsError("refusing to overwrite an existing audit record")
    rendered = json.dumps(payload, ensure_ascii=False, indent=None if compact else 2, separators=(",", ":") if compact else None) + "\n"
    temporary = unresolved.with_name(unresolved.name + ".tmp")
    if temporary.exists() or temporary.is_symlink():
        raise FileExistsError("temporary output already exists")
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(rendered)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, unresolved)
    finally:
        temporary.unlink(missing_ok=True)


def audit(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    root = project_root(args.project)
    profile_path, profile = load_json(root, args.profile, "domain profile")
    protocol_path, protocol = load_json(root, args.protocol, "project protocol")
    observations_path, observation_document = load_json(root, args.observations, "normalized observations")
    contract_aware = validate_profile_protocol(profile, protocol)
    if observation_document.get("schema_version") != OBSERVATION_SCHEMA or not isinstance(observation_document.get("observations"), dict):
        raise ValueError("unsupported normalized observation schema")
    source_paths = [contained_file(root, raw, "protocol source") for raw in protocol["source_paths"]]
    manual_review_paths: list[Path] = []
    if contract_aware:
        for binding in protocol["contract_bindings"]:
            manual = binding.get("manual_review_ref")
            if not manual:
                continue
            review_path = contained_file(root, manual["path"], "manual review reference")
            if sha256_file(review_path).casefold() != manual["sha256"].casefold():
                raise ValueError(f"manual review reference hash mismatch for {binding['instance_id']}")
            if review_path not in manual_review_paths:
                manual_review_paths.append(review_path)
    scope = ["design"]
    phases = {"design"}
    evidence = [fingerprint(root, observations_path, kind="normalized_observations")]
    evidence.extend(fingerprint(root, path, kind="manual_review") for path in manual_review_paths)
    findings = evaluate_rules(profile, observation_document["observations"], phases)

    approved_document: dict[str, Any] | None = None
    if args.command in {"audit-manifest", "audit-runtime"}:
        requested_path, requested = load_json(root, args.requested, "requested manifest")
        generated_path, generated = load_json(root, args.generated, "generated manifest")
        approved_path, approved_document = load_json(root, args.approved, "approved manifest")
        findings.extend(compare_manifests(requested, generated, approved_document))
        scope.append("manifest")
        evidence.extend([
            fingerprint(root, requested_path, kind="requested_manifest"),
            fingerprint(root, generated_path, kind="generated_manifest"),
            fingerprint(root, approved_path, kind="approved_manifest"),
        ])
    if args.command == "audit-runtime":
        runtime_path, runtime = load_json(root, args.runtime_evidence, "runtime evidence")
        assert approved_document is not None
        findings.extend(check_runtime(approved_document, runtime))
        findings.extend(evaluate_rules(profile, observation_document["observations"], {"runtime"}))
        scope.append("runtime")
        evidence.append(fingerprint(root, runtime_path, kind="runtime_evidence"))

    contract_coverage: list[dict[str, Any]] = []
    if contract_aware:
        contract_coverage, coverage_findings = evaluate_contract_coverage(
            profile, protocol, scope, findings
        )
        findings.extend(coverage_findings)
    status = (
        "failed"
        if any(item.get("severity") == "blocker" for item in findings)
        else "incomplete"
        if any(item.get("severity") == "incomplete" for item in findings)
        else "verified"
    )
    result_schema = RESULT_SCHEMA_V2 if contract_aware else RESULT_SCHEMA_V1
    result = {
        "schema_version": result_schema,
        "document_type": "domain-validation-record",
        "status": status,
        "owner": {"kind": protocol["owner"]["kind"], "id": protocol["owner"]["id"]},
        "validator": {
            "id": VALIDATOR_ID,
            "version": VALIDATOR_VERSION,
            "sha256": sha256_file(Path(__file__).resolve()),
        },
        "profile": {
            "id": profile["profile_id"],
            "version": profile["version"],
            "path": relative(root, profile_path),
            "sha256": sha256_file(profile_path),
        },
        "scope": scope,
        "protocol_fingerprints": [fingerprint(root, protocol_path)],
        "source_fingerprints": [fingerprint(root, path) for path in source_paths],
        "evidence": evidence,
        "claim_ceiling": protocol["claim_ceiling"] if status == "verified" else "unsupported",
        "findings": findings,
        "unvalidated": [
            "Research-question choice, undeclared domain assumptions, and claims above the protocol ceiling.",
            "Project onboarding, Agent configuration, governance migration, and authorization to execute work.",
        ],
    }
    if contract_aware:
        result["contract_coverage"] = contract_coverage
    if args.output:
        write_output(root, args.output, result, args.compact)
    print(json.dumps(result, ensure_ascii=False, indent=None if args.compact else 2, separators=(",", ":") if args.compact else None))
    return result, 0 if status == "verified" else 1


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("audit-design", "audit-manifest", "audit-runtime"):
        command = subparsers.add_parser(name)
        command.add_argument("project")
        command.add_argument("--profile", required=True)
        command.add_argument("--protocol", required=True)
        command.add_argument("--observations", required=True)
        if name in {"audit-manifest", "audit-runtime"}:
            command.add_argument("--requested", required=True)
            command.add_argument("--generated", required=True)
            command.add_argument("--approved", required=True)
        if name == "audit-runtime":
            command.add_argument("--runtime-evidence", required=True)
        command.add_argument("--output")
        command.add_argument("--compact", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        _, exit_code = audit(parse_args(argv))
        return exit_code
    except (FileExistsError, KeyError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({
            "schema_version": RESULT_SCHEMA_V2,
            "document_type": "domain-validation-record",
            "status": "invalid",
            "error": str(exc),
        }, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
