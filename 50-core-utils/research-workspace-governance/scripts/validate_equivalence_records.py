#!/usr/bin/env python3
"""Validate typed research-equivalence declarations without doing domain science."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


SCHEMA_VERSION = "research-equivalence-record/v1"
RELATION_TYPES = {
    "matrix_exact",
    "matrix_global_phase",
    "observational_protocol",
    "metric_only",
}
CLAIMS = {
    "matrix_identity",
    "matrix_equivalence_up_to_global_phase",
    "observational_interchangeability",
    "metric_comparison",
    "deduplicate_operator_evidence",
    "deduplicate_observation_evidence",
}
SAFE_ALLOWED = {
    "matrix_exact": {
        "matrix_identity",
        "matrix_equivalence_up_to_global_phase",
        "deduplicate_operator_evidence",
    },
    "matrix_global_phase": {
        "matrix_equivalence_up_to_global_phase",
        "deduplicate_operator_evidence",
    },
    "observational_protocol": {
        "observational_interchangeability",
        "metric_comparison",
        "deduplicate_observation_evidence",
    },
    "metric_only": {"metric_comparison"},
}
REQUIRED_FORBIDDEN = {
    "matrix_exact": {
        "observational_interchangeability",
        "metric_comparison",
        "deduplicate_observation_evidence",
    },
    "matrix_global_phase": {
        "matrix_identity",
        "observational_interchangeability",
        "metric_comparison",
        "deduplicate_observation_evidence",
    },
    "observational_protocol": {
        "matrix_identity",
        "matrix_equivalence_up_to_global_phase",
        "deduplicate_operator_evidence",
    },
    "metric_only": {
        "matrix_identity",
        "matrix_equivalence_up_to_global_phase",
        "observational_interchangeability",
        "deduplicate_operator_evidence",
        "deduplicate_observation_evidence",
    },
}
MAX_DOCUMENT_BYTES = 5 * 1024 * 1024


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


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
        current = current / part
        if current.exists() and is_link_like(current):
            return current
    return None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdefABCDEF" for character in value)
    )


def finding(code: str, message: str, *, severity: str = "error") -> dict[str, str]:
    return {"code": code, "message": message, "severity": severity}


def require_nonempty_object(record: dict[str, Any], name: str, findings: list[dict[str, str]]) -> None:
    value = record.get(name)
    if not isinstance(value, dict) or not value:
        findings.append(finding(f"missing-{name.replace('_', '-')}", f"{name} must be a non-empty object"))


def require_string_list(record: dict[str, Any], name: str, findings: list[dict[str, str]], *, nonempty: bool) -> set[str]:
    value = record.get(name)
    if not isinstance(value, list) or (nonempty and not value) or any(not isinstance(item, str) or not item for item in value):
        findings.append(finding(f"invalid-{name.replace('_', '-')}", f"{name} must be a {'non-empty ' if nonempty else ''}string array"))
        return set()
    if len(value) != len(set(value)):
        findings.append(finding(f"duplicate-{name.replace('_', '-')}", f"{name} contains duplicates"))
    unknown = set(value) - CLAIMS
    if unknown:
        findings.append(finding("unknown-inference-claim", "unknown inference claims: " + ", ".join(sorted(unknown))))
    return set(value)


def validate_evidence_path(item: dict[str, Any], project: Path | None, findings: list[dict[str, str]]) -> None:
    raw_path = item.get("path")
    if raw_path is None:
        external_id = item.get("external_id")
        content_hash = item.get("content_sha256")
        if not isinstance(external_id, str) or not external_id or not is_sha256(content_hash):
            findings.append(finding("untraceable-equivalence-evidence", "evidence requires path+sha256 or external_id+content_sha256"))
        return
    if not isinstance(raw_path, str) or not raw_path:
        findings.append(finding("invalid-evidence-path", "evidence path must be a non-empty string"))
        return
    if project is None:
        findings.append(finding("evidence-path-unchecked", f"cannot boundary-check evidence path without --project-root: {raw_path}"))
        return
    relative = Path(raw_path)
    if relative.is_absolute() or ".." in relative.parts:
        findings.append(finding("evidence-path-outside-project", f"evidence path must be project-contained and relative: {raw_path}"))
        return
    unresolved = (project / relative).absolute()
    if first_link_component(unresolved) is not None:
        findings.append(finding("linked-evidence-path", f"evidence path traverses a link or junction: {raw_path}"))
        return
    resolved = unresolved.resolve(strict=False)
    if not is_relative_to(resolved, project):
        findings.append(finding("evidence-path-outside-project", f"evidence path escapes project root: {raw_path}"))
        return
    if not resolved.is_file():
        findings.append(finding("missing-evidence-file", f"evidence file does not exist: {raw_path}"))
        return
    expected = item.get("sha256")
    if not is_sha256(expected):
        findings.append(finding("invalid-evidence-hash", f"project evidence requires SHA-256: {raw_path}"))
    elif sha256_file(resolved).casefold() != expected.casefold():
        findings.append(finding("evidence-hash-mismatch", f"evidence hash does not match: {raw_path}"))


def validate_record(record: Any, current_keys: dict[str, Any], project: Path | None) -> dict[str, Any]:
    if not isinstance(record, dict):
        return {
            "id": None,
            "type": None,
            "declared_status": None,
            "effective_status": "invalid",
            "findings": [finding("invalid-record", "record must be an object")],
        }

    findings: list[dict[str, str]] = []
    record_id = record.get("id")
    if not isinstance(record_id, str) or not record_id.strip():
        findings.append(finding("missing-record-id", "id must be a non-empty string"))
        record_id = None
    relation = record.get("type")
    if relation not in RELATION_TYPES:
        findings.append(finding("unknown-equivalence-type", f"unsupported equivalence type: {relation!r}"))
    require_nonempty_object(record, "scope", findings)
    require_nonempty_object(record, "invalidation_keys", findings)

    evidence = record.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        findings.append(finding("missing-equivalence-evidence", "evidence must be a non-empty array"))
    else:
        for item in evidence:
            if isinstance(item, dict) and item:
                validate_evidence_path(item, project, findings)
            else:
                findings.append(finding("untraceable-equivalence-evidence", "each evidence item must be a structured immutable locator"))

    method = record.get("comparison_method")
    if not isinstance(method, dict) or not isinstance(method.get("name"), str) or not method.get("name"):
        findings.append(finding("invalid-comparison-method", "comparison_method requires a non-empty name"))
        result = None
    else:
        result = method.get("result")
        if result not in {"pass", "fail", "unknown"}:
            findings.append(finding("invalid-comparison-result", "comparison_method.result must be pass, fail, or unknown"))

    if "tolerance" not in record:
        findings.append(finding("missing-tolerance", "tolerance must be explicit; use null for exact comparison"))
    elif isinstance(record["tolerance"], (int, float)) and record["tolerance"] < 0:
        findings.append(finding("invalid-tolerance", "numeric tolerance must be non-negative"))
    elif record["tolerance"] is not None and not isinstance(record["tolerance"], (int, float, dict)):
        findings.append(finding("invalid-tolerance", "tolerance must be null, a non-negative number, or an object"))
    tolerance = record.get("tolerance")
    if relation == "matrix_exact" and tolerance is not None and tolerance != 0:
        findings.append(finding("nonexact-matrix-tolerance", "matrix_exact tolerance must be null or zero"))
    if relation in {"observational_protocol", "metric_only"} and tolerance is None:
        findings.append(finding("missing-operational-tolerance", f"{relation} requires a non-null tolerance"))

    allowed = require_string_list(record, "allowed_use", findings, nonempty=True)
    forbidden = require_string_list(record, "forbidden_inference", findings, nonempty=False)
    overlap = allowed & forbidden
    if overlap:
        findings.append(finding("conflicting-inference-boundary", "claims are both allowed and forbidden: " + ", ".join(sorted(overlap))))
    if relation in RELATION_TYPES:
        unsafe_allowed = allowed - SAFE_ALLOWED[relation]
        if unsafe_allowed:
            findings.append(finding("overstated-equivalence", f"{relation} cannot allow: " + ", ".join(sorted(unsafe_allowed))))
        missing_forbidden = REQUIRED_FORBIDDEN[relation] - forbidden
        if missing_forbidden:
            findings.append(finding("missing-forbidden-inference", f"{relation} must forbid: " + ", ".join(sorted(missing_forbidden))))

    if relation == "matrix_global_phase":
        semantics = record.get("semantics")
        if not isinstance(semantics, dict) or semantics.get("global_phase_physically_irrelevant") is not True:
            findings.append(finding("missing-global-phase-semantics", "matrix_global_phase requires an explicit true global-phase physical-semantics assertion"))
    if relation == "observational_protocol":
        protocol = record.get("protocol")
        if not isinstance(protocol, dict) or not isinstance(protocol.get("id"), str) or not protocol.get("id"):
            findings.append(finding("missing-observational-protocol", "observational_protocol requires protocol.id"))

    declared_status = record.get("status")
    if declared_status not in {"verified", "unverified", "stale", "rejected"}:
        findings.append(finding("invalid-equivalence-status", "status must be verified, unverified, stale, or rejected"))
    if declared_status == "verified" and result != "pass":
        findings.append(finding("verified-without-passing-comparison", "verified status requires comparison_method.result=pass"))

    effective_status = declared_status if declared_status in {"verified", "unverified", "stale", "rejected"} else "invalid"
    if record_id and record_id in current_keys:
        declared_keys = record.get("invalidation_keys")
        if not isinstance(current_keys[record_id], dict):
            findings.append(finding("invalid-current-invalidation-keys", "current invalidation keys must be an object"))
        elif declared_keys != current_keys[record_id]:
            effective_status = "stale"
            findings.append(finding("invalidation-key-drift", "current invalidation keys differ from the verified record", severity="finding"))

    if any(item["severity"] == "error" for item in findings):
        effective_status = "invalid"
    return {
        "id": record_id,
        "type": relation,
        "declared_status": declared_status,
        "effective_status": effective_status,
        "findings": findings,
    }


def validate_document(document: Any, project: Path | None = None) -> dict[str, Any]:
    top_findings: list[dict[str, str]] = []
    if not isinstance(document, dict):
        document = {}
        top_findings.append(finding("invalid-equivalence-document", "document must be a JSON object"))
    if document.get("schema_version") != SCHEMA_VERSION:
        top_findings.append(finding("unsupported-equivalence-schema", f"schema_version must be {SCHEMA_VERSION}"))
    records = document.get("records")
    if not isinstance(records, list):
        top_findings.append(finding("invalid-equivalence-records", "records must be an array"))
        records = []
    elif not records:
        top_findings.append(finding("empty-equivalence-records", "a declared equivalence document must contain at least one record"))
    current = document.get("current_invalidation_keys", {})
    if not isinstance(current, dict):
        top_findings.append(finding("invalid-current-invalidation-keys", "current_invalidation_keys must be an object"))
        current = {}

    validated = [validate_record(record, current, project) for record in records]
    identifiers = [item["id"] for item in validated if item["id"]]
    duplicates = sorted({item for item in identifiers if identifiers.count(item) > 1})
    if duplicates:
        top_findings.append(finding("duplicate-equivalence-record-id", "duplicate record ids: " + ", ".join(duplicates)))

    invalid = bool(top_findings) or any(item["effective_status"] == "invalid" for item in validated)
    nonverified = any(item["effective_status"] != "verified" for item in validated)
    if invalid:
        status, exit_code = "invalid", 2
    elif nonverified:
        status, exit_code = "unverified", 1
    else:
        status, exit_code = "verified", 0
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "project_root": str(project) if project else None,
        "findings": top_findings,
        "records": validated,
        "summary": {
            "exit_code": exit_code,
            "record_count": len(validated),
            "verified_count": sum(item["effective_status"] == "verified" for item in validated),
            "finding_count": len(top_findings) + sum(len(item["findings"]) for item in validated),
        },
    }


def load_document(path: Path) -> Any:
    if path.stat().st_size > MAX_DOCUMENT_BYTES:
        raise ValueError("equivalence document exceeds 5 MiB")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records", help="Equivalence-record JSON document")
    parser.add_argument("--project-root", help="Optional project root for evidence boundary and hash checks")
    parser.add_argument("--compact", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        path = Path(args.records).expanduser().resolve(strict=True)
        if not path.is_file() or is_link_like(path):
            raise ValueError("equivalence document must be a regular non-linked file")
        project = None
        if args.project_root:
            project = Path(args.project_root).expanduser().resolve(strict=True)
            if not project.is_dir() or is_link_like(project):
                raise ValueError("project root must be a regular non-linked directory")
        report = validate_document(load_document(path), project)
        print(json.dumps(report, ensure_ascii=False, indent=None if args.compact else 2, sort_keys=True))
        return int(report["summary"]["exit_code"])
    except (FileNotFoundError, OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"schema_version": SCHEMA_VERSION, "status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
