#!/usr/bin/env python3
"""Validate domain-neutral comparison records without doing domain science."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any


SCHEMA_VERSION = "research-comparison-record/v2"
LEGACY_SCHEMA_VERSION = "research-equivalence-record/v1"
MAX_DOCUMENT_BYTES = 5 * 1024 * 1024
RELATION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")
VALID_STATUSES = {"verified", "unverified", "stale", "rejected"}
VALID_RESULTS = {"pass", "fail", "unknown"}
VALID_REVIEWS = {"approved", "pending", "rejected"}
SENSITIVE_NAMES = {
    ".env",
    ".npmrc",
    ".pypirc",
    "credentials",
    "credentials.json",
    "id_rsa",
    "id_ed25519",
}
SENSITIVE_TERMS = {
    "secret",
    "secrets",
    "credential",
    "credentials",
    "token",
    "tokens",
    "password",
    "passwords",
    "passwd",
    "cookie",
    "cookies",
    "private",
}
SENSITIVE_SUFFIXES = {".pem", ".p12", ".pfx", ".key", ".keystore"}


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


def finding(
    code: str,
    message: str,
    *,
    severity: str = "blocker",
    **details: Any,
) -> dict[str, Any]:
    return {"code": code, "message": message, "severity": severity, **details}


def is_sensitive_relative_path(path: Path) -> bool:
    for part in path.parts:
        lower = part.casefold()
        if lower in SENSITIVE_NAMES or Path(lower).suffix in SENSITIVE_SUFFIXES:
            return True
        terms = {term for term in re.split(r"[\s._-]+", lower) if term}
        if terms & SENSITIVE_TERMS or {"api", "key"} <= terms or {"private", "key"} <= terms:
            return True
    return False


def require_nonempty_object(
    record: dict[str, Any], name: str, findings: list[dict[str, Any]]
) -> None:
    value = record.get(name)
    if not isinstance(value, dict) or not value:
        findings.append(
            finding(
                f"missing-{name.replace('_', '-')}",
                f"{name} must be a non-empty object",
            )
        )


def require_string_list(
    record: dict[str, Any],
    name: str,
    findings: list[dict[str, Any]],
    *,
    nonempty: bool,
) -> set[str]:
    value = record.get(name)
    invalid = (
        not isinstance(value, list)
        or (nonempty and not value)
        or any(not isinstance(item, str) or not item.strip() for item in value or [])
    )
    if invalid:
        qualifier = "non-empty " if nonempty else ""
        findings.append(
            finding(
                f"invalid-{name.replace('_', '-')}",
                f"{name} must be a {qualifier}string array",
            )
        )
        return set()
    if len(value) != len(set(value)):
        duplicates = sorted({item for item in value if value.count(item) > 1})
        findings.append(finding(
            f"duplicate-{name.replace('_', '-')}",
            f"{name} contains duplicates",
            object=name,
            candidate_interpretations=[
                f"{item!r} at index {index}"
                for item in duplicates
                for index, value_item in enumerate(value)
                if value_item == item
            ],
            risk="a declared use or boundary cannot be addressed by one stable list identity",
            minimum_fix="retain one occurrence of each value through an approved record edit",
            verification=f"rerun validation and confirm {name} is unique",
        ))
    return set(value)


def validate_evidence_path(
    item: dict[str, Any], project: Path | None, findings: list[dict[str, Any]]
) -> None:
    raw_path = item.get("path")
    if raw_path is None:
        external_id = item.get("external_id")
        content_hash = item.get("content_sha256")
        if not isinstance(external_id, str) or not external_id or not is_sha256(content_hash):
            findings.append(
                finding(
                    "untraceable-comparison-evidence",
                    "evidence requires path+sha256 or external_id+content_sha256",
                )
            )
        return
    if not isinstance(raw_path, str) or not raw_path:
        findings.append(finding("invalid-evidence-path", "evidence path must be a non-empty string"))
        return
    if project is None:
        findings.append(
            finding(
                "evidence-path-unchecked",
                f"cannot boundary-check evidence path without --project-root: {raw_path}",
            )
        )
        return
    relative = Path(raw_path)
    if relative.is_absolute() or ".." in relative.parts:
        findings.append(
            finding(
                "evidence-path-outside-project",
                f"evidence path must be project-contained and relative: {raw_path}",
            )
        )
        return
    if is_sensitive_relative_path(relative):
        findings.append(
            finding(
                "sensitive-evidence-path",
                f"credential-like or sensitive evidence is not opened or hashed: {raw_path}",
            )
        )
        return
    unresolved = (project / relative).absolute()
    if first_link_component(unresolved) is not None:
        findings.append(
            finding("linked-evidence-path", f"evidence path traverses a link or junction: {raw_path}")
        )
        return
    resolved = unresolved.resolve(strict=False)
    if not is_relative_to(resolved, project):
        findings.append(
            finding("evidence-path-outside-project", f"evidence path escapes project root: {raw_path}")
        )
        return
    if not resolved.is_file():
        findings.append(finding("missing-evidence-file", f"evidence file does not exist: {raw_path}"))
        return
    expected = item.get("sha256")
    if not is_sha256(expected):
        findings.append(finding("invalid-evidence-hash", f"project evidence requires SHA-256: {raw_path}"))
    elif sha256_file(resolved).casefold() != expected.casefold():
        findings.append(finding("evidence-hash-mismatch", f"evidence hash does not match: {raw_path}"))


def validate_record(
    record: Any, current_keys: dict[str, Any], project: Path | None
) -> dict[str, Any]:
    if not isinstance(record, dict):
        return {
            "id": None,
            "type": None,
            "declared_status": None,
            "effective_status": "invalid",
            "findings": [finding("invalid-record", "record must be an object")],
        }

    findings: list[dict[str, Any]] = []
    record_id = record.get("id")
    if not isinstance(record_id, str) or not RELATION_ID.fullmatch(record_id):
        findings.append(finding("invalid-record-id", "id must be a stable non-prose identifier"))
        record_id = None

    relation = record.get("type")
    if not isinstance(relation, str) or not RELATION_ID.fullmatch(relation):
        findings.append(
            finding(
                "invalid-comparison-type",
                "type must be a stable domain-defined identifier, not prose",
            )
        )

    require_nonempty_object(record, "scope", findings)
    require_nonempty_object(record, "invalidation_keys", findings)

    evidence = record.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        findings.append(finding("missing-comparison-evidence", "evidence must be a non-empty array"))
    else:
        for item in evidence:
            if isinstance(item, dict) and item:
                validate_evidence_path(item, project, findings)
            else:
                findings.append(
                    finding(
                        "untraceable-comparison-evidence",
                        "each evidence item must be a structured immutable locator",
                    )
                )

    method = record.get("comparison_method")
    if not isinstance(method, dict) or not isinstance(method.get("name"), str) or not method.get("name"):
        findings.append(finding("invalid-comparison-method", "comparison_method requires a non-empty name"))
        result = None
    else:
        result = method.get("result")
        if result not in VALID_RESULTS:
            findings.append(
                finding("invalid-comparison-result", "comparison_method.result must be pass, fail, or unknown")
            )

    if "tolerance" not in record:
        findings.append(finding("missing-tolerance", "tolerance must be explicit; use null when appropriate"))
    else:
        tolerance = record["tolerance"]
        if isinstance(tolerance, (int, float)) and tolerance < 0:
            findings.append(finding("invalid-tolerance", "numeric tolerance must be non-negative"))
        elif tolerance is not None and not isinstance(tolerance, (int, float, dict, str)):
            findings.append(
                finding("invalid-tolerance", "tolerance must be null, a non-negative number, an object, or a string")
            )
        elif isinstance(tolerance, (dict, str)) and not tolerance:
            findings.append(finding("invalid-tolerance", "structured or named tolerance must not be empty"))

    allowed = require_string_list(record, "allowed_use", findings, nonempty=True)
    forbidden = require_string_list(record, "forbidden_inference", findings, nonempty=False)
    overlap = allowed & forbidden
    if overlap:
        findings.append(
            finding(
                "conflicting-inference-boundary",
                "uses are both allowed and forbidden: " + ", ".join(sorted(overlap)),
            )
        )

    review = record.get("domain_review")
    if not isinstance(review, dict) or review.get("status") not in VALID_REVIEWS:
        findings.append(
            finding(
                "invalid-domain-review",
                "domain_review.status must be approved, pending, or rejected",
            )
        )
        review_status = None
    else:
        review_status = review["status"]
        if review_status in {"approved", "rejected"}:
            if not isinstance(review.get("reviewer"), str) or not review.get("reviewer"):
                findings.append(finding("missing-domain-reviewer", "completed domain review requires reviewer"))
            if not isinstance(review.get("reviewed_at"), str) or not review.get("reviewed_at"):
                findings.append(finding("missing-domain-review-date", "completed domain review requires reviewed_at"))

    declared_status = record.get("status")
    if declared_status not in VALID_STATUSES:
        findings.append(
            finding("invalid-comparison-status", "status must be verified, unverified, stale, or rejected")
        )
    if declared_status == "verified" and result != "pass":
        findings.append(
            finding("verified-without-passing-comparison", "verified status requires comparison_method.result=pass")
        )
    if declared_status == "verified" and review_status != "approved":
        findings.append(
            finding("verified-without-domain-approval", "verified status requires domain_review.status=approved")
        )
    if review_status == "rejected" and declared_status != "rejected":
        findings.append(
            finding("rejected-review-status-conflict", "a rejected domain review requires status=rejected")
        )

    effective_status = declared_status if declared_status in VALID_STATUSES else "invalid"
    if record_id and record_id in current_keys:
        declared_keys = record.get("invalidation_keys")
        if not isinstance(current_keys[record_id], dict):
            findings.append(finding("invalid-current-invalidation-keys", "current invalidation keys must be an object"))
        elif declared_keys != current_keys[record_id]:
            effective_status = "stale"
            findings.append(
                finding(
                    "invalidation-key-drift",
                    "current invalidation keys differ from the reviewed record",
                    severity="non_blocker",
                )
            )

    if any(item["severity"] == "blocker" for item in findings):
        effective_status = "invalid"
    return {
        "id": record_id,
        "type": relation,
        "declared_status": declared_status,
        "effective_status": effective_status,
        "findings": findings,
    }


def validate_document(document: Any, project: Path | None = None) -> dict[str, Any]:
    top_findings: list[dict[str, Any]] = []
    if not isinstance(document, dict):
        document = {}
        top_findings.append(finding("invalid-comparison-document", "document must be a JSON object"))
    source_schema = document.get("schema_version")
    if source_schema == LEGACY_SCHEMA_VERSION:
        top_findings.append(
            finding(
                "legacy-comparison-schema-requires-migration",
                f"{LEGACY_SCHEMA_VERSION} is recognized but must be migrated to {SCHEMA_VERSION}; its scientific meanings are not reinterpreted",
            )
        )
        return {
            "schema_version": SCHEMA_VERSION,
            "source_schema_version": LEGACY_SCHEMA_VERSION,
            "status": "invalid",
            "project_root": str(project) if project else None,
            "findings": top_findings,
            "records": [],
            "summary": {"exit_code": 2, "record_count": 0, "verified_count": 0, "finding_count": 1},
        }
    if source_schema != SCHEMA_VERSION:
        top_findings.append(
            finding("unsupported-comparison-schema", f"schema_version must be {SCHEMA_VERSION}")
        )
    records = document.get("records")
    if not isinstance(records, list):
        top_findings.append(finding("invalid-comparison-records", "records must be an array"))
        records = []
    elif not records:
        top_findings.append(
            finding("empty-comparison-records", "a declared comparison document must contain at least one record")
        )
    current = document.get("current_invalidation_keys", {})
    if not isinstance(current, dict):
        top_findings.append(finding("invalid-current-invalidation-keys", "current_invalidation_keys must be an object"))
        current = {}

    validated = [validate_record(record, current, project) for record in records]
    identifiers = [item["id"] for item in validated if item["id"]]
    duplicates = sorted({item for item in identifiers if identifiers.count(item) > 1})
    if duplicates:
        top_findings.append(
            finding(
                "duplicate-comparison-record-id",
                "duplicate record ids: " + ", ".join(duplicates),
                object="comparison record id",
                candidate_interpretations=[
                    f"{record_id!r} at index {index}"
                    for record_id in duplicates
                    for index, item in enumerate(validated)
                    if item["id"] == record_id
                ],
                risk="evidence, review, and invalidation state cannot resolve to one comparison record",
                minimum_fix="assign one distinct stable id to each comparison record",
                verification="rerun validation and confirm record ids are unique",
            )
        )

    invalid = any(item["severity"] == "blocker" for item in top_findings) or any(item["effective_status"] == "invalid" for item in validated)
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
        raise ValueError("comparison document exceeds 5 MiB")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records", help="Comparison-record JSON document")
    parser.add_argument("--project-root", help="Optional project root for evidence boundary and hash checks")
    parser.add_argument("--compact", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        path = Path(args.records).expanduser().absolute()
        linked = first_link_component(path)
        if linked is not None:
            raise ValueError(f"comparison document path traverses a link or junction: {linked}")
        path = path.resolve(strict=True)
        if not path.is_file():
            raise ValueError("comparison document must be a regular file")
        if is_sensitive_relative_path(Path(path.name)):
            raise ValueError("refusing to open a credential-like or sensitive comparison document")
        project = None
        if args.project_root:
            raw_project = Path(args.project_root).expanduser().absolute()
            linked = first_link_component(raw_project)
            if linked is not None:
                raise ValueError(f"project root path traverses a link or junction: {linked}")
            project = raw_project.resolve(strict=True)
            if not project.is_dir():
                raise ValueError("project root must be a regular directory")
        report = validate_document(load_document(path), project)
        print(json.dumps(report, ensure_ascii=False, indent=None if args.compact else 2, sort_keys=True))
        return int(report["summary"]["exit_code"])
    except (FileNotFoundError, OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(
            json.dumps(
                {"schema_version": SCHEMA_VERSION, "status": "error", "error": str(exc)},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
