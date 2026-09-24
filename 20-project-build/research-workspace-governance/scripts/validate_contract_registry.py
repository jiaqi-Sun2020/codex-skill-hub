#!/usr/bin/env python3
"""Validate and derive research-contract registry views without project writes."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from typing import Any


REGISTRY_SCHEMA = "research-contract-registry/v1"
RESULT_SCHEMA = "research-contract-registry-validation/v1"
MATRIX_SCHEMA = "research-contract-traceability/v1"
IMPACT_SCHEMA = "research-contract-impact/v1"
MAX_BYTES = 5 * 1024 * 1024
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/#-]{0,255}$")
CATEGORIES = {"SCI", "STAT", "ENG", "GOV"}
APPLICABILITY = {"required", "optional", "not_applicable", "unresolved"}
DEFINITION_STATES = {"draft", "reviewed", "frozen", "superseded"}
REF_FIELDS = {
    "id", "kind", "schema_version", "path", "selector", "version", "sha256",
    "state", "current", "decision_ref", "ceiling_compatibility",
}
REF_LISTS = {
    "implementation_refs", "verification_refs", "work_refs", "evidence_refs",
    "claim_refs", "authorization_refs", "deliverable_refs",
}
CONTRACT_FIELDS = {
    "instance_id", "catalog_id", "category", "revision", "scope",
    "applicability", "owner_ref", "definition_ref", "depends_on",
    *REF_LISTS, "required_gates", "definition_state",
}
REGISTRY_FIELDS = {
    "schema_version", "registry_id", "revision", "supersedes", "profile_refs",
    "protocol_refs", "contracts", "amendments",
}
AMENDMENT_FIELDS = {
    "change_id", "reason", "old_contract_revision", "new_contract_revision",
    "author", "decision_ref", "changed_assumptions_or_parameters",
    "affected_contracts", "affected_tasks", "affected_evidence",
    "affected_claims", "affected_deliverables", "reuse_policy",
    "invalidation_reason", "required_revalidation", "next_allowed_action",
}


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
        junction = getattr(path, "is_junction", None)
        if junction and junction():
            return True
        return bool(getattr(path.lstat(), "st_file_attributes", 0) & 0x400)
    except OSError:
        return True


def linked_component(root: Path, target: Path) -> Path | None:
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


def resolve_inputs(project_raw: str, registry_raw: str) -> tuple[Path, Path]:
    project_unresolved = Path(project_raw).expanduser().absolute()
    current = Path(project_unresolved.anchor)
    for part in project_unresolved.parts[1:]:
        current = current / part
        if current.exists() and is_link_like(current):
            raise ValueError(f"project root traverses a link or junction: {current}")
    project = project_unresolved.resolve(strict=True)
    if not project.is_dir():
        raise ValueError("project root must be a directory")
    supplied = Path(registry_raw).expanduser()
    if supplied.is_absolute() or ".." in supplied.parts:
        raise ValueError("registry must be a project-relative path without parent traversal")
    unresolved = (project / supplied).absolute()
    if linked_component(project, unresolved) is not None:
        raise ValueError("registry must not traverse a link or junction")
    registry = unresolved.resolve(strict=True)
    try:
        registry.relative_to(project)
    except ValueError as exc:
        raise ValueError("registry escapes the project root") from exc
    if not registry.is_file() or is_link_like(registry):
        raise ValueError("registry must be a regular non-linked file")
    if registry.stat().st_size > MAX_BYTES:
        raise ValueError("registry exceeds 5 MiB")
    return project, registry


def stable(value: Any) -> bool:
    return isinstance(value, str) and bool(ID.fullmatch(value))


def independent_decision(reference: dict[str, Any] | None) -> bool:
    if not reference or not stable(reference.get("decision_ref")):
        return False
    return str(reference["decision_ref"]).casefold() != str(reference.get("id", "")).casefold()


def unique_ids(value: Any) -> bool:
    return (
        isinstance(value, list)
        and all(stable(item) for item in value)
        and len({item.casefold() for item in value}) == len(value)
    )


def finding(code: str, message: str, *, severity: str = "blocker", obj: str = "registry") -> dict[str, str]:
    return {
        "code": code,
        "severity": severity,
        "object": obj,
        "message": message,
        "minimum_fix": "Correct the authoritative registry or referenced owner record, then rerun this validator.",
        "verification": "Rerun the same read-only command and confirm the finding is absent.",
    }


def validate_ref(value: Any, label: str, findings: list[dict[str, str]]) -> dict[str, Any] | None:
    if not isinstance(value, dict) or not stable(value.get("id")):
        findings.append(finding("invalid-reference", f"{label} needs a stable id", obj=label))
        return None
    unknown = sorted(set(value) - REF_FIELDS)
    if unknown:
        findings.append(finding("unknown-reference-fields", f"{label} has unsupported fields: {', '.join(unknown)}", obj=label))
    if "sha256" in value and (not isinstance(value["sha256"], str) or not re.fullmatch(r"[A-Fa-f0-9]{64}", value["sha256"])):
        findings.append(finding("invalid-reference-sha256", f"{label}.sha256 is invalid", obj=label))
    if "path" in value:
        raw = value["path"]
        if not isinstance(raw, str) or not raw or Path(raw).is_absolute() or ".." in Path(raw).parts:
            findings.append(finding("unsafe-reference-path", f"{label}.path must be project-relative and non-escaping", obj=label))
    if value.get("ceiling_compatibility") not in {None, "within", "exceeds", "unresolved"}:
        findings.append(finding("invalid-ceiling-compatibility", f"{label}.ceiling_compatibility is invalid", obj=label))
    return value


def current_ref(refs: list[dict[str, Any]]) -> dict[str, Any] | None:
    current = [item for item in refs if item.get("current") is True]
    if len(current) == 1:
        return current[0]
    if len(refs) == 1 and "current" not in refs[0]:
        return refs[0]
    return None


def standard_catalog_id(category: str, catalog_id: str) -> bool:
    ranges = {"SCI": 9, "STAT": 13, "ENG": 17, "GOV": 14}
    match = re.fullmatch(r"(SCI|STAT|ENG|GOV)-(\d{2})(?:\.[1-6])?", catalog_id)
    if not match or match.group(1) != category:
        return False
    number = int(match.group(2))
    if not 1 <= number <= ranges[category]:
        return False
    return "." not in catalog_id or catalog_id.startswith("ENG-08.")


def validate_registry(document: Any) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    if not isinstance(document, dict):
        raise ValueError("registry must contain one JSON object")
    missing_registry = sorted(REGISTRY_FIELDS - set(document))
    unknown = sorted(set(document) - REGISTRY_FIELDS)
    if missing_registry:
        findings.append(finding("missing-registry-fields", f"missing required fields: {', '.join(missing_registry)}"))
    if unknown:
        findings.append(finding("unknown-registry-fields", f"unsupported fields: {', '.join(unknown)}"))
    if document.get("schema_version") != REGISTRY_SCHEMA:
        findings.append(finding("unsupported-registry-schema", f"schema_version must be {REGISTRY_SCHEMA}"))
    if not stable(document.get("registry_id")):
        findings.append(finding("invalid-registry-id", "registry_id must be a stable identifier"))
    if isinstance(document.get("revision"), bool) or not isinstance(document.get("revision"), int) or document.get("revision", 0) < 1:
        findings.append(finding("invalid-registry-revision", "revision must be a positive integer"))
    if document.get("supersedes") is not None and not stable(document.get("supersedes")):
        findings.append(finding("invalid-registry-supersedes", "supersedes must be null or a stable registry identifier"))
    profile_refs = document.get("profile_refs", [])
    protocol_refs = document.get("protocol_refs", [])
    for group, values in (("profile_refs", profile_refs), ("protocol_refs", protocol_refs)):
        if not isinstance(values, list):
            findings.append(finding("invalid-reference-list", f"{group} must be an array", obj=group))
            continue
        for index, value in enumerate(values):
            validate_ref(value, f"{group}[{index}]", findings)

    contracts_raw = document.get("contracts")
    if not isinstance(contracts_raw, list):
        findings.append(finding("invalid-contract-list", "contracts must be an array"))
        contracts_raw = []
    contracts: list[dict[str, Any]] = []
    identifiers: dict[str, int] = {}
    all_ref_ids: dict[str, str] = {}
    required_undefined: list[str] = []
    defined_unimplemented: list[str] = []
    implemented_unverified: list[str] = []
    evidence_missing_or_stale: list[str] = []
    claims_exceeding: list[str] = []
    claim_review_gaps: list[str] = []
    authorization_gaps: list[str] = []
    affected_gates: set[str] = set()
    matrix: list[dict[str, Any]] = []

    for index, raw in enumerate(contracts_raw):
        label = f"contracts[{index}]"
        if not isinstance(raw, dict):
            findings.append(finding("invalid-contract", f"{label} must be an object", obj=label))
            continue
        unknown_contract = sorted(set(raw) - CONTRACT_FIELDS)
        missing_contract = sorted(CONTRACT_FIELDS - set(raw))
        if unknown_contract:
            findings.append(finding("unknown-contract-fields", f"{label} has unsupported fields: {', '.join(unknown_contract)}", obj=label))
        if missing_contract:
            findings.append(finding("missing-contract-fields", f"{label} missing: {', '.join(missing_contract)}", obj=label))
        instance_id = raw.get("instance_id")
        if not stable(instance_id):
            findings.append(finding("invalid-contract-instance-id", f"{label}.instance_id is invalid", obj=label))
            continue
        identity = instance_id.casefold()
        if identity in identifiers:
            findings.append(finding("duplicate-contract-instance-id", f"{instance_id} also appears at contracts[{identifiers[identity]}]", obj=instance_id))
        else:
            identifiers[identity] = index
        category = raw.get("category")
        catalog_id = raw.get("catalog_id")
        if category not in CATEGORIES or not stable(catalog_id):
            findings.append(finding("invalid-contract-catalog", f"{instance_id} needs a valid category and catalog_id", obj=instance_id))
        elif not standard_catalog_id(category, catalog_id) and not str(catalog_id).startswith("profile:"):
            findings.append(finding("unbound-custom-contract", f"{instance_id} custom catalog_id must use the profile: namespace", obj=instance_id))
        if isinstance(raw.get("revision"), bool) or not isinstance(raw.get("revision"), int) or raw.get("revision", 0) < 1:
            findings.append(finding("invalid-contract-revision", f"{instance_id}.revision must be positive", obj=instance_id))
        scope = raw.get("scope")
        if not isinstance(scope, dict) or set(scope) != {"type", "id"} or not stable(scope.get("type")) or not stable(scope.get("id")):
            findings.append(finding("invalid-contract-scope", f"{instance_id}.scope needs stable type and id", obj=instance_id))
        applicability = raw.get("applicability")
        mode = applicability.get("mode") if isinstance(applicability, dict) else None
        if not isinstance(applicability, dict) or set(applicability) != {"mode", "reason", "decision_ref"} or mode not in APPLICABILITY:
            findings.append(finding("invalid-applicability", f"{instance_id}.applicability is invalid", obj=instance_id))
            mode = "unresolved"
        elif mode == "not_applicable" and (not str(applicability.get("reason", "")).strip() or not stable(applicability.get("decision_ref"))):
            findings.append(finding("unreviewed-not-applicable", f"{instance_id} not_applicable needs reason and decision_ref", obj=instance_id))
        elif mode == "unresolved":
            findings.append(finding("unresolved-applicability", f"{instance_id} applicability is unresolved", severity="incomplete", obj=instance_id))
        owner = raw.get("owner_ref")
        definition = raw.get("definition_ref")
        if owner is not None:
            validate_ref(owner, f"{label}.owner_ref", findings)
        if definition is not None:
            validate_ref(definition, f"{label}.definition_ref", findings)
        definition_state = raw.get("definition_state")
        if definition_state not in DEFINITION_STATES:
            findings.append(finding("invalid-definition-state", f"{instance_id}.definition_state is invalid", obj=instance_id))
        if mode == "required" and (owner is None or definition is None or definition_state == "draft"):
            required_undefined.append(instance_id)
            findings.append(finding("required-contract-undefined", f"{instance_id} is required but not review-ready", severity="incomplete", obj=instance_id))
        dependencies = raw.get("depends_on")
        if not unique_ids(dependencies):
            findings.append(finding("invalid-contract-dependencies", f"{instance_id}.depends_on must contain unique stable IDs", obj=instance_id))
            dependencies = []
        elif instance_id.casefold() in {item.casefold() for item in dependencies}:
            findings.append(finding("self-contract-dependency", f"{instance_id} depends on itself", obj=instance_id))
        gates = raw.get("required_gates")
        if not unique_ids(gates):
            findings.append(finding("invalid-required-gates", f"{instance_id}.required_gates must contain unique stable IDs", obj=instance_id))
            gates = []
        normalized_refs: dict[str, list[dict[str, Any]]] = {}
        for field in sorted(REF_LISTS):
            values = raw.get(field)
            accepted: list[dict[str, Any]] = []
            if not isinstance(values, list):
                findings.append(finding("invalid-reference-list", f"{instance_id}.{field} must be an array", obj=instance_id))
                values = []
            current_count = 0
            for ref_index, value in enumerate(values):
                checked = validate_ref(value, f"{label}.{field}[{ref_index}]", findings)
                if checked is None:
                    continue
                ref_id = checked["id"].casefold()
                locator = f"{instance_id}.{field}[{ref_index}]"
                if ref_id in all_ref_ids:
                    findings.append(finding("duplicate-record-reference-id", f"reference id {checked['id']} appears at {all_ref_ids[ref_id]} and {locator}", obj=checked["id"]))
                else:
                    all_ref_ids[ref_id] = locator
                current_count += checked.get("current") is True
                accepted.append(checked)
            if len(accepted) > 1 and current_count != 1:
                findings.append(finding("ambiguous-current-reference", f"{instance_id}.{field} needs exactly one current reference when history is retained", obj=instance_id))
            normalized_refs[field] = accepted
        implementation = current_ref(normalized_refs["implementation_refs"])
        verification = current_ref(normalized_refs["verification_refs"])
        evidence = current_ref(normalized_refs["evidence_refs"])
        authorization = current_ref(normalized_refs["authorization_refs"])
        claims = normalized_refs["claim_refs"]
        claim = current_ref(claims)
        if mode == "required" and definition_state in {"reviewed", "frozen"} and not implementation:
            defined_unimplemented.append(instance_id)
            findings.append(finding("required-contract-unimplemented", f"{instance_id} is defined but has no current implementation reference", severity="incomplete", obj=instance_id))
        if implementation and implementation.get("state") == "implemented" and (not verification or verification.get("state") != "pass"):
            implemented_unverified.append(instance_id)
            findings.append(finding("implementation-unverified", f"{instance_id} is implemented but lacks a passing current verification", severity="incomplete", obj=instance_id))
        if mode == "required" and (not evidence or evidence.get("state") in {None, "absent", "partial", "invalidated", "stale"}):
            evidence_missing_or_stale.append(instance_id)
            findings.append(finding("evidence-missing-or-stale", f"{instance_id} lacks current admitted evidence", severity="incomplete", obj=instance_id))
        if claim:
            claim_state = claim.get("state")
            if claim_state not in {"unreviewed", "supported", "contradicted", "rejected", "unsupported", "stale"}:
                findings.append(finding("invalid-claim-state", f"{claim['id']} has an unsupported claim state", obj=claim["id"]))
            if claim_state in {"supported", "contradicted", "rejected", "unsupported"} and not independent_decision(claim):
                claim_review_gaps.append(claim["id"])
                findings.append(finding("claim-review-missing", f"{claim['id']} declares a reviewed outcome without an independent review reference", severity="incomplete", obj=claim["id"]))
            if claim_state == "supported" and claim.get("ceiling_compatibility") != "within":
                claims_exceeding.append(claim["id"])
                findings.append(finding("claim-boundary-unreviewed", f"{claim['id']} is marked supported without reviewed ceiling compatibility", obj=claim["id"]))
        if "claim_reviewed" in gates and (
            not claim
            or claim.get("state") in {None, "unreviewed", "stale"}
            or not independent_decision(claim)
        ):
            gap_id = claim["id"] if claim else instance_id
            if gap_id not in claim_review_gaps:
                claim_review_gaps.append(gap_id)
                findings.append(finding("claim-review-missing", f"{instance_id} requires a current independent claim review", severity="incomplete", obj=instance_id))
        if "execution_authorized" in gates and (not authorization or authorization.get("state") != "granted" or not independent_decision(authorization)):
            authorization_gaps.append(instance_id)
            findings.append(finding("authorization-missing", f"{instance_id} has no traceable granted authorization decision", severity="incomplete", obj=instance_id))
        if mode in {"required", "unresolved"} and (instance_id in required_undefined or instance_id in defined_unimplemented or instance_id in implemented_unverified or instance_id in evidence_missing_or_stale):
            affected_gates.update(gates)
        matrix.append({
            "instance_id": instance_id,
            "catalog_id": catalog_id,
            "category": category,
            "scope": scope,
            "applicability": mode,
            "owner_ref": owner,
            "definition_ref": definition,
            "definition_state": definition_state,
            "implementation_refs": normalized_refs["implementation_refs"],
            "verification_refs": normalized_refs["verification_refs"],
            "work_refs": normalized_refs["work_refs"],
            "evidence_refs": normalized_refs["evidence_refs"],
            "claim_refs": claims,
            "authorization_refs": normalized_refs["authorization_refs"],
            "deliverable_refs": normalized_refs["deliverable_refs"],
            "required_gates": gates,
            "gaps": [name for name, present in (
                ("required_but_undefined", instance_id in required_undefined),
                ("defined_but_unimplemented", instance_id in defined_unimplemented),
                ("implemented_but_unverified", instance_id in implemented_unverified),
                ("evidence_missing_or_stale", instance_id in evidence_missing_or_stale),
                ("claim_review_gap", bool(claim and claim["id"] in claim_review_gaps) or (not claim and instance_id in claim_review_gaps)),
                ("authorization_gap", instance_id in authorization_gaps),
            ) if present],
        })
        contracts.append({**raw, "depends_on": dependencies})

    known = {item.get("instance_id", "").casefold() for item in contracts}
    for contract in contracts:
        for dependency in contract.get("depends_on", []):
            if dependency.casefold() not in known:
                findings.append(finding("dangling-contract-dependency", f"{contract['instance_id']} depends on unknown {dependency}", obj=contract["instance_id"]))

    amendments_raw = document.get("amendments")
    if not isinstance(amendments_raw, list):
        findings.append(finding("invalid-amendment-list", "amendments must be an array"))
        amendments_raw = []
    amendments: list[dict[str, Any]] = []
    change_ids: set[str] = set()
    for index, amendment in enumerate(amendments_raw):
        label = f"amendments[{index}]"
        if not isinstance(amendment, dict):
            findings.append(finding("invalid-amendment", f"{label} must be an object", obj=label))
            continue
        missing = sorted(AMENDMENT_FIELDS - set(amendment))
        unknown_amendment = sorted(set(amendment) - AMENDMENT_FIELDS)
        if missing:
            findings.append(finding("missing-amendment-fields", f"{label} missing: {', '.join(missing)}", obj=label))
        if unknown_amendment:
            findings.append(finding("unknown-amendment-fields", f"{label} has unsupported fields: {', '.join(unknown_amendment)}", obj=label))
        change_id = amendment.get("change_id")
        if not stable(change_id) or change_id.casefold() in change_ids:
            findings.append(finding("invalid-or-duplicate-change-id", f"{label}.change_id is invalid or duplicated", obj=label))
        else:
            change_ids.add(change_id.casefold())
        for field in ("affected_contracts", "affected_tasks", "affected_evidence", "affected_claims", "affected_deliverables"):
            if not unique_ids(amendment.get(field)):
                findings.append(finding("invalid-amendment-reference-list", f"{label}.{field} must contain unique stable IDs", obj=label))
        if isinstance(amendment.get("old_contract_revision"), bool) or not isinstance(amendment.get("old_contract_revision"), int) or isinstance(amendment.get("new_contract_revision"), bool) or not isinstance(amendment.get("new_contract_revision"), int) or amendment.get("new_contract_revision", 0) <= amendment.get("old_contract_revision", 0):
            findings.append(finding("invalid-amendment-revision", f"{label} must advance the contract revision", obj=label))
        if amendment.get("decision_ref") is not None and not stable(amendment.get("decision_ref")):
            findings.append(finding("invalid-amendment-decision", f"{label}.decision_ref is invalid", obj=label))
        elif amendment.get("decision_ref") is None:
            findings.append(finding("amendment-decision-unresolved", f"{label} has no approval decision reference", severity="incomplete", obj=label))
        if not stable(amendment.get("author")):
            findings.append(finding("invalid-amendment-author", f"{label}.author must be a stable identifier", obj=label))
        for field in ("reason", "reuse_policy", "invalidation_reason", "next_allowed_action"):
            if not isinstance(amendment.get(field), str) or not amendment[field].strip():
                findings.append(finding("invalid-amendment-text", f"{label}.{field} must be non-empty text", obj=label))
        for field in ("changed_assumptions_or_parameters", "required_revalidation"):
            values = amendment.get(field)
            if not isinstance(values, list) or any(not isinstance(item, str) or not item.strip() for item in values) or len(values) != len(set(values)):
                findings.append(finding("invalid-amendment-text-list", f"{label}.{field} must contain unique non-empty text", obj=label))
        for affected_contract in amendment.get("affected_contracts", []):
            if stable(affected_contract) and affected_contract.casefold() not in known:
                findings.append(finding("unknown-affected-contract", f"{label} names unknown contract {affected_contract}", obj=label))
        amendments.append(amendment)

    category_counts = Counter(item.get("category") for item in contracts if item.get("category") in CATEGORIES)
    blockers = [item for item in findings if item["severity"] == "blocker"]
    incomplete = [item for item in findings if item["severity"] == "incomplete"]
    status = "failed" if blockers else "incomplete" if incomplete else "valid"
    next_action = (
        "Resolve the first blocking finding and rerun validation."
        if blockers else
        "Complete the first incomplete required contract and rerun validation."
        if incomplete else
        "Use an independent gate or claim review before any consequential action."
    )
    return {
        "status": status,
        "schema_result": "pass" if not blockers else "fail",
        "contract_coverage_by_category": {category: category_counts.get(category, 0) for category in sorted(CATEGORIES)},
        "required_but_undefined": required_undefined,
        "defined_but_unimplemented": defined_unimplemented,
        "implemented_but_unverified": implemented_unverified,
        "evidence_missing_or_stale": evidence_missing_or_stale,
        "claims_exceeding_reviewed_support": sorted(set(claims_exceeding)),
        "claim_review_gaps": sorted(set(claim_review_gaps)),
        "authorization_gaps": authorization_gaps,
        "affected_gates": sorted(affected_gates),
        "next_action": next_action,
        "findings": findings,
        "matrix": matrix,
        "contracts": contracts,
        "amendments": amendments,
    }


def impact_for(validation: dict[str, Any], change_id: str) -> dict[str, Any]:
    amendment = next((item for item in validation["amendments"] if item.get("change_id") == change_id), None)
    if amendment is None:
        raise ValueError(f"unknown change_id: {change_id}")
    reverse: dict[str, set[str]] = defaultdict(set)
    for contract in validation["contracts"]:
        for dependency in contract.get("depends_on", []):
            reverse[dependency.casefold()].add(contract["instance_id"])
    queue = deque(amendment.get("affected_contracts", []))
    affected: list[str] = []
    seen: set[str] = set()
    while queue:
        current = queue.popleft()
        identity = current.casefold()
        if identity in seen:
            continue
        seen.add(identity)
        affected.append(current)
        queue.extend(sorted(reverse.get(identity, set())))
    matrix_by_id = {item["instance_id"].casefold(): item for item in validation["matrix"]}
    claims = set(amendment.get("affected_claims", []))
    deliverables = set(amendment.get("affected_deliverables", []))
    gates: set[str] = set()
    for contract_id in affected:
        row = matrix_by_id.get(contract_id.casefold())
        if row:
            claims.update(ref["id"] for ref in row["claim_refs"])
            deliverables.update(ref["id"] for ref in row["deliverable_refs"])
            gates.update(row["required_gates"])
    return {
        "schema_version": IMPACT_SCHEMA,
        "change_id": change_id,
        "directly_affected_contracts": amendment.get("affected_contracts", []),
        "affected_contract_closure": affected,
        "stale_verification_scope": affected,
        "affected_tasks": amendment.get("affected_tasks", []),
        "affected_evidence": amendment.get("affected_evidence", []),
        "affected_claims": sorted(claims),
        "affected_deliverables": sorted(deliverables),
        "affected_gates": sorted(gates),
        "required_revalidation": amendment.get("required_revalidation", []),
        "next_allowed_action": amendment.get("next_allowed_action"),
        "historical_records_modified": False,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("validate", "matrix", "impact"):
        child = subparsers.add_parser(command)
        child.add_argument("project")
        child.add_argument("--registry", required=True)
        if command == "impact":
            child.add_argument("--change-id", required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(sys.argv[1:] if argv is None else argv)
        project, registry_path = resolve_inputs(args.project, args.registry)
        document = json.loads(registry_path.read_text(encoding="utf-8-sig"))
        validation = validate_registry(document)
        snapshot = {
            "project_root": str(project),
            "registry_path": registry_path.relative_to(project).as_posix(),
            "registry_sha256": sha256_file(registry_path),
        }
        if args.command == "matrix":
            payload = {
                "schema_version": MATRIX_SCHEMA,
                "status": validation["status"],
                "checked_scope": "contract-traceability",
                "input_snapshot": snapshot,
                "rows": validation["matrix"],
                "findings": validation["findings"],
                "content_treated_as_data": True,
                "commands_executed": False,
            }
        elif args.command == "impact":
            payload = impact_for(validation, args.change_id)
            payload.update({"input_snapshot": snapshot, "content_treated_as_data": True, "commands_executed": False})
        else:
            payload = {
                "schema_version": RESULT_SCHEMA,
                "checked_scope": "contract-registry",
                "input_snapshot": snapshot,
                **{key: value for key, value in validation.items() if key not in {"contracts", "amendments", "matrix"}},
                "content_treated_as_data": True,
                "commands_executed": False,
            }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if validation["status"] == "valid" else 1
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({
            "schema_version": RESULT_SCHEMA,
            "status": "error",
            "error": str(exc),
            "content_treated_as_data": True,
            "commands_executed": False,
        }, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
