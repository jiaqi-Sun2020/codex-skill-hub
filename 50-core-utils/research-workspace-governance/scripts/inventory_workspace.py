#!/usr/bin/env python3
"""Create a read-only, metadata-only inventory of a research workspace."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys


SCHEMA_VERSION = "research-workspace-inventory/v2"
PROJECT_CONTRACT_SCHEMA = "research-project-contract/v2"
LEGACY_PROJECT_CONTRACT_SCHEMA = "research-project-contract/v1"
GOVERNANCE_STATE_SCHEMA = "research-governance-state/v1"
RELOCATION_MAP_SCHEMA = "research-path-relocation-map/v1"
DEFAULT_MAX_FILES = 20_000
HARD_MAX_FILES = 100_000
MAX_REPORTED_PATHS_PER_ROLE = 80
MAX_TEMPORARY_CANDIDATES = 100
MAX_CONTRACT_BYTES = 1024 * 1024
STABLE_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/#-]{0,255}$")
ENV_REFERENCE = re.compile(r"^(?:[$][A-Za-z_][A-Za-z0-9_]*|[$][{][A-Za-z_][A-Za-z0-9_]*[}]|%[A-Za-z_][A-Za-z0-9_]*%)$")
SENSITIVE_ASSIGNMENT = re.compile(
    r"(?i)(?:^|[\s;&])(?:token|password|passwd|secret|api[_-]?key|credential|credentials|cookie|authorization)\s*[:=]\s*([^\s,;]+)"
)
BEARER_VALUE = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{8,}")
HIGH_RISK_SECRET = re.compile(
    r"(?:gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|AKIA[A-Z0-9]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|https?://[^\s/:]+:[^\s/@]+@)",
    re.IGNORECASE,
)
SENSITIVE_OPTION_VALUE = re.compile(
    r"(?i)(?:^|\s)(?:--token|--password|--passwd|--secret|--api-key|--apikey|--credential|--credentials|--cookie|--authorization)\s+([^\s]+)"
)
SENSITIVE_COMMAND_OPTIONS = {
    "--token", "--password", "--passwd", "--secret", "--api-key", "--apikey",
    "--credential", "--credentials", "--cookie", "--authorization",
}

SKIP_DIRECTORIES = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".next",
    ".turbo",
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
    "session",
    "sessions",
    "private",
    "id_rsa",
}
SENSITIVE_SUFFIXES = {".pem", ".p12", ".pfx", ".key", ".keystore"}

ROLE_HINTS = {
    "agent_context": {".agents", ".agent", ".codex"},
    "governance": {"governance", "admin", "decisions"},
    "protocols": {
        "protocol", "protocols", "study", "studies", "design", "designs",
        "preregistration", "preregistrations",
    },
    "source_records": {
        "raw", "original", "originals", "source", "sources", "input", "inputs",
        "acquisition", "acquisitions", "field-notes",
    },
    "external_references": {
        "external", "reference", "references", "vendor", "benchmarks",
    },
    "derived_data": {
        "derived", "processed", "preprocessed", "prepared", "cleaned", "interim",
        "features", "coded", "calibrated",
    },
    "methods": {"src", "code", "lib", "libs", "method", "methods", "procedures"},
    "work_units": {
        "work", "works", "task", "tasks", "analysis", "analyses", "workflow",
        "workflows", "pipeline", "pipelines", "notebook", "notebooks",
    },
    "evidence": {
        "run", "runs", "output", "outputs", "result", "results", "artifact",
        "artifacts", "evidence", "logs",
    },
    "reports": {"report", "reports", "docs", "documentation"},
    "deliverables": {
        "publication", "publications", "paper", "papers", "manuscript", "manuscripts",
        "figure", "figures", "figs", "presentation", "presentations", "release", "releases",
    },
    "archive": {"archive", "archives", "archived"},
    "temporary": {".tmp", "tmp", "temp", "temporary", "cache", "caches", "scratch"},
    "data_container": {"data", "dataset", "datasets"},
    "tests": {"test", "tests", "testing", "validation", "validations"},
    "automation": {
        "automation", "automations", "script", "scripts", "job", "jobs",
        "scheduler", "schedulers", "hook", "hooks",
    },
}

CONTRACT_ROOT_ROLES = {
    "source",
    "method",
    "working",
    "evidence",
    "deliverable",
    "automation",
    "archive",
    "temporary",
    "protected",
}
CONTRACT_FIELDS = {
    "schema_version",
    "governance_profile",
    "method_profile_ids",
    "roots",
    "identifier_fields",
    "lifecycle_extensions",
    "required_deliverables",
    "governance_state_path",
    "relocation_map_paths",
    "automations",
    "deletion_policy",
}

LEGACY_CONTRACT_FIELDS = {
    "schema_version",
    "governance_profile",
    "method_profile_ids",
    "roots",
    "identifier_fields",
    "lifecycle_stages",
    "required_deliverables",
    "deletion_policy",
}

AUTOMATION_FIELDS = {
    "logical_id",
    "path",
    "scope",
    "working_directory",
    "command",
    "trigger",
    "inputs",
    "outputs",
    "side_effects",
    "owner",
    "concurrency_control",
    "failure_recovery",
    "verification_method",
    "retirement_condition",
}

WORK_STATES = {"not_started", "active", "blocked", "completed", "abandoned"}
CLAIM_STATES = {
    "not_applicable",
    "unreviewed",
    "unsupported",
    "supported",
    "contradicted",
    "rejected",
}
STATUS_FIELDS = {
    "scope_type",
    "scope_id",
    "status_record_id",
    "work_state",
    "claim_state",
    "evidence_refs",
}

TEMPORARY_FILE_PATTERNS = (
    re.compile(r"(?i)(^|[.])(tmp|temp)([.]|$)"),
    re.compile(r"(?i)[.]staging$"),
    re.compile(r"(?i)[.](bak|swp|swo)$"),
)


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


def inspect_governance_layout(root: Path) -> dict[str, object]:
    canonical = root / ".agents" / "governance"
    legacy = root / "governance"
    candidates = []
    unsafe = []
    agents_container = root / ".agents"
    if (
        (agents_container.exists() or agents_container.is_symlink())
        and (
            first_link_component(agents_container.absolute()) is not None
            or not agents_container.is_dir()
        )
        and not canonical.exists()
        and not canonical.is_symlink()
    ):
        unsafe.append({"kind": "canonical_parent", "path": ".agents"})
    for label, path in (("canonical", canonical), ("legacy", legacy)):
        if not path.exists() and not path.is_symlink():
            continue
        relative = path.relative_to(root).as_posix()
        if first_link_component(path.absolute()) is not None or not path.is_dir():
            unsafe.append({"kind": label, "path": relative})
        else:
            candidates.append({"kind": label, "path": relative})

    if unsafe:
        status = "unsafe"
        active_path = None
        write_allowed = False
        finding_code = "unsafe-governance-location"
    elif len(candidates) > 1:
        status = "ambiguous"
        active_path = None
        write_allowed = False
        finding_code = "multiple-governance-locations"
    elif candidates:
        status = str(candidates[0]["kind"])
        active_path = str(candidates[0]["path"])
        write_allowed = True
        finding_code = None
    else:
        status = "absent"
        active_path = None
        write_allowed = False
        finding_code = "governance-location-absent"

    findings = []
    if finding_code:
        findings.append({
            "code": finding_code,
            "severity": "blocker" if status in {"unsafe", "ambiguous"} else "non_blocker",
            "object": "governance_location",
            "candidate_interpretations": [item["path"] for item in candidates + unsafe],
            "risk": (
                "a write could target an unsafe or non-authoritative location"
                if status in {"unsafe", "ambiguous"}
                else "governance data has not been initialized"
            ),
            "minimum_fix": (
                "owner selects one regular project-contained authority"
                if status in {"unsafe", "ambiguous"}
                else "use the Generator to create .agents before governance initialization"
            ),
            "verification": "rerun metadata inventory and confirm exactly one regular candidate",
        })
    return {
        "status": status,
        "canonical_path": ".agents/governance",
        "legacy_path": "governance",
        "active_path": active_path,
        "candidates": candidates,
        "unsafe_candidates": unsafe,
        "write_allowed": write_allowed,
        "generator_prerequisite": status == "absent" and not (root / ".agents").is_dir(),
        "findings": findings,
    }


def valid_string_list(value: object) -> bool:
    return (
        isinstance(value, list)
        and all(isinstance(item, str) and bool(item.strip()) for item in value)
        and len(value) == len(set(value))
    )


def governance_finding(
    code: str,
    message: str,
    *,
    severity: str = "blocker",
    **details: object,
) -> dict[str, object]:
    return {"code": code, "message": message, "severity": severity, **details}


def is_stable_identifier(value: object) -> bool:
    return isinstance(value, str) and bool(STABLE_IDENTIFIER.fullmatch(value))


def text_contains_inline_secret(value: str) -> bool:
    if BEARER_VALUE.search(value) or HIGH_RISK_SECRET.search(value):
        return True
    match = SENSITIVE_ASSIGNMENT.search(value)
    if match and not ENV_REFERENCE.fullmatch(match.group(1)):
        return True
    option_match = SENSITIVE_OPTION_VALUE.search(value)
    return bool(option_match and not ENV_REFERENCE.fullmatch(option_match.group(1)))


def nested_text_contains_inline_secret(value: object) -> bool:
    if isinstance(value, str):
        return text_contains_inline_secret(value)
    if isinstance(value, list):
        return any(nested_text_contains_inline_secret(item) for item in value)
    if isinstance(value, dict):
        return any(nested_text_contains_inline_secret(item) for item in value.values())
    return False


def command_contains_inline_secret(value: object) -> bool:
    if not isinstance(value, list):
        return False
    for index, item in enumerate(value):
        if not isinstance(item, str):
            continue
        lowered = item.casefold()
        if lowered in SENSITIVE_COMMAND_OPTIONS and index + 1 < len(value):
            next_value = value[index + 1]
            if isinstance(next_value, str) and not ENV_REFERENCE.fullmatch(next_value):
                return True
        for option in SENSITIVE_COMMAND_OPTIONS:
            prefix = option + "="
            if lowered.startswith(prefix):
                supplied = item[len(prefix):]
                if supplied and not ENV_REFERENCE.fullmatch(supplied):
                    return True
        if text_contains_inline_secret(item):
            return True
    return False


def validate_contract_path(root: Path, raw: str) -> str | None:
    relative = Path(raw)
    if relative.is_absolute() or relative.drive or not relative.parts or ".." in relative.parts:
        return "path must be non-empty, project-relative, and contain no '..'"
    candidate = (root / relative).absolute()
    linked = first_link_component(candidate)
    if linked is not None:
        return "path traverses a link or junction"
    if not is_relative_to(candidate.resolve(strict=False), root):
        return "path escapes the project root"
    return None


def contract_path_identity(root: Path, raw: str) -> str:
    return os.path.normcase(str((root / Path(raw)).resolve(strict=False)))


def validate_automations(
    root: Path,
    value: object,
    findings: list[dict[str, object]],
) -> list[dict[str, object]]:
    if value is None:
        return []
    if not isinstance(value, list):
        findings.append(governance_finding("invalid-automations", "automations must be an array"))
        return []

    normalized: list[dict[str, object]] = []
    identifiers: dict[str, int] = {}
    path_identities: dict[str, tuple[int, str]] = {}
    scalar_fields = {
        "logical_id",
        "scope",
        "trigger",
        "owner",
        "concurrency_control",
        "failure_recovery",
        "verification_method",
        "retirement_condition",
    }
    list_fields = {"command", "inputs", "outputs", "side_effects"}
    for index, raw in enumerate(value):
        if not isinstance(raw, dict):
            findings.append(governance_finding("invalid-automation", f"automations[{index}] must be an object"))
            continue
        if command_contains_inline_secret(raw.get("command")) or nested_text_contains_inline_secret(raw):
            findings.append(governance_finding(
                "sensitive-automation-value",
                f"automations[{index}] contains an inline sensitive value and was excluded from inventory output",
            ))
            continue
        finding_start = len(findings)
        missing = sorted(AUTOMATION_FIELDS - set(raw))
        unknown = sorted(set(raw) - AUTOMATION_FIELDS)
        if missing:
            findings.append(governance_finding("missing-automation-fields", f"automations[{index}] missing: {', '.join(missing)}"))
        if unknown:
            findings.append(governance_finding("unknown-automation-fields", f"automations[{index}] unknown: {', '.join(unknown)}"))
        for field in scalar_fields:
            if not isinstance(raw.get(field), str) or not str(raw.get(field)).strip():
                findings.append(governance_finding("invalid-automation-field", f"automations[{index}].{field} must be a non-empty string"))
        for field in list_fields:
            if not valid_string_list(raw.get(field)) or (field == "command" and not raw.get(field)):
                findings.append(governance_finding("invalid-automation-field", f"automations[{index}].{field} must be a unique string array"))

        logical_id = raw.get("logical_id")
        if isinstance(logical_id, str) and logical_id.strip():
            identity = logical_id.casefold()
            if identity in identifiers:
                findings.append(governance_finding(
                    "duplicate-automation-id",
                    f"duplicate automation logical_id: {logical_id}",
                    object=f"automation logical_id {logical_id}",
                    candidate_interpretations=[f"automations[{identifiers[identity]}]", f"automations[{index}]"],
                    risk="automation status, ownership, and evidence cannot be assigned uniquely",
                    minimum_fix="give each automation a distinct stable logical_id",
                    verification="rerun inventory and confirm each logical_id resolves to one declaration",
                ))
            else:
                identifiers[identity] = index

        raw_path = raw.get("path")
        working_directory = raw.get("working_directory")
        for field, candidate in (("path", raw_path), ("working_directory", working_directory)):
            if not isinstance(candidate, str):
                findings.append(governance_finding("invalid-automation-path", f"automations[{index}].{field} must be project-relative"))
                continue
            error = validate_contract_path(root, candidate)
            if error:
                findings.append(governance_finding("unsafe-automation-path", f"automations[{index}].{field} {candidate!r}: {error}"))
        if isinstance(raw_path, str) and validate_contract_path(root, raw_path) is None:
            identity = contract_path_identity(root, raw_path)
            if identity in path_identities:
                prior_index, prior_path = path_identities[identity]
                findings.append(governance_finding(
                    "ambiguous-automation-path",
                    f"multiple automation declarations resolve to {raw_path!r}",
                    object="automation physical path",
                    candidate_interpretations=[f"automations[{prior_index}]:{prior_path}", f"automations[{index}]:{raw_path}"],
                    risk="a command, owner, or side effect could be attributed to the wrong automation",
                    minimum_fix="use one declaration per physical path or assign distinct project-contained paths",
                    verification="rerun inventory and confirm each physical automation path has one declaration",
                ))
            else:
                path_identities[identity] = (index, raw_path)
        if not any(
            item.get("severity") == "blocker" for item in findings[finding_start:]
        ):
            normalized.append({field: raw[field] for field in sorted(AUTOMATION_FIELDS)})
    return normalized


def inspect_project_contract(root: Path, layout: dict[str, object]) -> dict[str, object]:
    active = layout.get("active_path")
    if not isinstance(active, str):
        return {"status": "not_checked", "path": None, "findings": []}
    governance_root = root / Path(active)
    canonical = governance_root / "project_contract.json"
    legacy = governance_root / "project_contract.yaml"
    candidates = [
        path for path in (canonical, legacy)
        if path.exists() or path.is_symlink()
    ]
    canonical_relative = canonical.relative_to(root).as_posix()
    if not candidates:
        return {"status": "absent", "path": canonical_relative, "findings": []}
    if len(candidates) > 1:
        return {
            "status": "invalid",
            "path": None,
            "findings": [governance_finding(
                "ambiguous-project-contract",
                "both project_contract.json and legacy project_contract.yaml exist",
                candidate_interpretations=[path.relative_to(root).as_posix() for path in candidates],
                risk="contract authority cannot be determined without guessing",
                minimum_fix="owner selects one authoritative contract and separately approves treatment of the other",
                verification="rerun inventory and confirm exactly one contract candidate",
            )],
        }
    path = candidates[0]
    relative = path.relative_to(root).as_posix()
    legacy_format = path.name == "project_contract.yaml"
    findings: list[dict[str, object]] = []
    if first_link_component(path.absolute()) is not None or not path.is_file():
        findings.append(governance_finding("unsafe-project-contract", "contract must be a regular non-linked file"))
        return {"status": "invalid", "path": relative, "findings": findings}
    try:
        if path.stat().st_size > MAX_CONTRACT_BYTES:
            raise ValueError("contract exceeds 1 MiB")
        document = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        message = (
            "legacy .yaml contracts are accepted only when they contain the historical JSON subset; "
            "no YAML parser is installed or implied"
            if legacy_format
            else str(exc)
        )
        findings.append(governance_finding("unreadable-project-contract", message))
        return {"status": "invalid", "path": relative, "findings": findings}
    if not isinstance(document, dict):
        findings.append(governance_finding("invalid-project-contract", "contract must be a JSON object"))
        return {"status": "invalid", "path": relative, "findings": findings}

    schema_version = document.get("schema_version")
    is_legacy_schema = schema_version == LEGACY_PROJECT_CONTRACT_SCHEMA
    if schema_version not in {PROJECT_CONTRACT_SCHEMA, LEGACY_PROJECT_CONTRACT_SCHEMA}:
        findings.append(governance_finding("unsupported-project-contract-schema", f"unsupported schema_version: {schema_version!r}"))
    if legacy_format and not is_legacy_schema:
        findings.append(governance_finding("invalid-project-contract-format", "project contract v2 must use project_contract.json"))
    if is_legacy_schema:
        findings.append(governance_finding(
            "legacy-project-contract",
            "project contract v1 is readable but should be migrated to project_contract.json v2",
            severity="non_blocker",
        ))

    allowed_fields = LEGACY_CONTRACT_FIELDS if is_legacy_schema else CONTRACT_FIELDS
    unknown = sorted(set(document) - allowed_fields)
    if unknown:
        findings.append(governance_finding("unknown-project-contract-fields", ", ".join(unknown)))
    profile = document.get("governance_profile")
    if profile is not None and profile not in {"minimal", "collaborative", "controlled"}:
        findings.append(governance_finding("invalid-governance-profile", "governance_profile is invalid"))
    method_profiles = document.get("method_profile_ids", [])
    if not valid_string_list(method_profiles):
        findings.append(governance_finding("invalid-method-profile-ids", "method_profile_ids must be a unique string array"))
        method_profiles = []
    roots = document.get("roots", {})
    safe_roots: dict[str, list[str]] = {}
    if not isinstance(roots, dict):
        findings.append(governance_finding("invalid-contract-roots", "roots must be an object"))
    else:
        unknown_roles = sorted(set(roots) - CONTRACT_ROOT_ROLES)
        if unknown_roles:
            findings.append(governance_finding("unknown-contract-root-roles", ", ".join(unknown_roles)))
        for role, values in roots.items():
            if role not in CONTRACT_ROOT_ROLES:
                continue
            if not valid_string_list(values):
                findings.append(governance_finding("invalid-contract-root-list", f"roots.{role} must be a unique string array"))
                continue
            safe_roots[role] = []
            identities: dict[str, str] = {}
            for raw in values:
                error = validate_contract_path(root, raw)
                if error:
                    findings.append(governance_finding("unsafe-contract-root", f"roots.{role} {raw!r}: {error}"))
                else:
                    identity = contract_path_identity(root, raw)
                    if identity in identities:
                        findings.append(governance_finding(
                            "ambiguous-contract-root",
                            f"roots.{role} contains paths that resolve to the same location: {raw!r}",
                            object=f"roots.{role}",
                            candidate_interpretations=[identities[identity], raw],
                            risk="the same physical asset root has more than one undeclared path identity",
                            minimum_fix="retain one canonical project-relative spelling and remove the alias through an approved contract edit",
                            verification=f"rerun inventory and confirm roots.{role} contains one identity per physical path",
                        ))
                    else:
                        identities[identity] = raw
                    safe_roots[role].append(Path(raw).as_posix())
    lifecycle_field = "lifecycle_stages" if is_legacy_schema else "lifecycle_extensions"
    for field in ("identifier_fields", lifecycle_field, "required_deliverables"):
        if field in document and not valid_string_list(document[field]):
            findings.append(governance_finding(f"invalid-{field.replace('_', '-')}", f"{field} must be a unique string array"))

    governance_state_path = document.get("governance_state_path")
    if governance_state_path is not None:
        if not isinstance(governance_state_path, str):
            findings.append(governance_finding("invalid-governance-state-path", "governance_state_path must be project-relative"))
        else:
            error = validate_contract_path(root, governance_state_path)
            if error:
                findings.append(governance_finding("unsafe-governance-state-path", f"governance_state_path {governance_state_path!r}: {error}"))
            elif not is_relative_to((root / governance_state_path).resolve(strict=False), governance_root.resolve(strict=False)):
                findings.append(governance_finding("governance-state-outside-authority", "governance_state_path must stay inside the active governance root"))

    relocation_map_paths = document.get("relocation_map_paths", [])
    if relocation_map_paths and not valid_string_list(relocation_map_paths):
        findings.append(governance_finding("invalid-relocation-map-paths", "relocation_map_paths must be a unique string array"))
        relocation_map_paths = []
    elif isinstance(relocation_map_paths, list):
        seen_relocations: dict[str, str] = {}
        for raw in relocation_map_paths:
            error = validate_contract_path(root, raw)
            if error:
                findings.append(governance_finding("unsafe-relocation-map-path", f"relocation map {raw!r}: {error}"))
                continue
            identity = contract_path_identity(root, raw)
            if identity in seen_relocations:
                findings.append(governance_finding(
                    "ambiguous-relocation-map-path",
                    f"duplicate normalized relocation map: {raw!r}",
                    object="relocation map path",
                    candidate_interpretations=[seen_relocations[identity], raw],
                    risk="historical paths could resolve through two aliases for one map",
                    minimum_fix="retain one canonical project-relative relocation map path",
                    verification="rerun inventory and confirm each physical relocation map has one path identity",
                ))
            else:
                seen_relocations[identity] = raw

    automations = validate_automations(root, document.get("automations"), findings)
    deletion_policy = document.get("deletion_policy")
    if deletion_policy is not None and deletion_policy != "explicit-exact-target-approval":
        findings.append(governance_finding("unsafe-deletion-policy", "deletion_policy cannot weaken exact-target approval"))
    blockers = [item for item in findings if item.get("severity") == "blocker"]
    return {
        "status": "invalid" if blockers else "legacy" if is_legacy_schema else "valid",
        "path": relative,
        "schema_version": schema_version,
        "contract_format": "legacy-json-in-yaml" if legacy_format else "json",
        "governance_profile": profile,
        "method_profile_ids": method_profiles,
        "roots": safe_roots,
        "identifier_fields": document.get("identifier_fields", []),
        "lifecycle_extensions": document.get(lifecycle_field, []),
        "required_deliverables": document.get("required_deliverables", []),
        "governance_state_path": governance_state_path,
        "relocation_map_paths": relocation_map_paths,
        "automations": automations,
        "findings": findings,
        "content_treated_as_data": True,
        "recursive_loading": False,
    }


def inspect_relocation_maps(
    root: Path,
    layout: dict[str, object],
    contract: dict[str, object],
) -> dict[str, object]:
    if contract.get("status") not in {"valid", "legacy"}:
        return {
            "status": "not_checked",
            "maps": [],
            "resolved_mappings": [],
            "findings": [],
            "content_treated_as_data": True,
        }
    declared = contract.get("relocation_map_paths", [])
    if not declared:
        return {
            "status": "not_declared",
            "maps": [],
            "resolved_mappings": [],
            "findings": [],
            "content_treated_as_data": True,
        }
    if not isinstance(declared, list):
        return {
            "status": "invalid",
            "maps": [],
            "resolved_mappings": [],
            "findings": [governance_finding("invalid-relocation-map-declaration", "relocation map paths must be an array")],
            "content_treated_as_data": True,
        }

    active = layout.get("active_path")
    if not isinstance(active, str):
        return {
            "status": "invalid",
            "maps": [],
            "resolved_mappings": [],
            "findings": [governance_finding("missing-relocation-map-authority", "relocation maps require one active governance authority")],
            "content_treated_as_data": True,
        }
    governance_root = (root / active).resolve(strict=False)
    findings: list[dict[str, object]] = []
    map_summaries: list[dict[str, object]] = []
    resolved_mappings: list[dict[str, str]] = []
    map_ids: dict[str, str] = {}
    mapping_ids: dict[str, str] = {}
    historical_targets: dict[str, tuple[str, str, str]] = {}
    allowed_map_fields = {"schema_version", "map_id", "mappings"}
    allowed_mapping_fields = {
        "mapping_id", "historical_path", "current_path", "approval_ref",
    }

    for map_index, raw_path in enumerate(declared):
        if not isinstance(raw_path, str) or validate_contract_path(root, raw_path):
            findings.append(governance_finding("unsafe-relocation-map", f"relocation map [{map_index}] has an unsafe project path"))
            continue
        path = root / raw_path
        if (
            is_sensitive_path(path, root)
            or first_link_component(path.absolute()) is not None
            or not path.is_file()
            or not is_relative_to(path.resolve(strict=True), governance_root)
        ):
            findings.append(governance_finding("unsafe-relocation-map", f"relocation map [{map_index}] must be a regular non-sensitive file inside the active governance root"))
            continue
        try:
            if path.stat().st_size > MAX_CONTRACT_BYTES:
                raise ValueError("relocation map exceeds 1 MiB")
            document = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, ValueError, json.JSONDecodeError):
            findings.append(governance_finding("unreadable-relocation-map", f"relocation map [{map_index}] is not bounded UTF-8 JSON"))
            continue
        if not isinstance(document, dict):
            findings.append(governance_finding("invalid-relocation-map", f"relocation map [{map_index}] must be a JSON object"))
            continue
        unknown_map_fields = sorted(set(document) - allowed_map_fields)
        if unknown_map_fields:
            findings.append(governance_finding("unknown-relocation-map-fields", f"relocation map [{map_index}] has unsupported fields: {', '.join(unknown_map_fields)}"))
        if document.get("schema_version") != RELOCATION_MAP_SCHEMA:
            findings.append(governance_finding("unsupported-relocation-map-schema", f"relocation map [{map_index}] must use {RELOCATION_MAP_SCHEMA}"))
            continue
        map_id = document.get("map_id")
        if not is_stable_identifier(map_id):
            findings.append(governance_finding("invalid-relocation-map-id", f"relocation map [{map_index}] needs a stable non-prose map_id"))
            continue
        map_identity = map_id.casefold()
        relative_map_path = path.relative_to(root).as_posix()
        if map_identity in map_ids:
            findings.append(governance_finding(
                "duplicate-relocation-map-id",
                f"relocation map_id is not unique: {map_id}",
                object=f"relocation map_id {map_id}",
                candidate_interpretations=[map_ids[map_identity], relative_map_path],
                risk="historical resolution cannot identify one authoritative map",
                minimum_fix="assign a distinct immutable map_id to each approved map",
                verification="rerun inventory and confirm every map_id resolves to one file",
            ))
        else:
            map_ids[map_identity] = relative_map_path
        mappings = document.get("mappings")
        if not isinstance(mappings, list) or not mappings:
            findings.append(governance_finding("invalid-relocation-mappings", f"relocation map [{map_index}].mappings must be a non-empty array"))
            continue
        accepted_count = 0
        for mapping_index, mapping in enumerate(mappings):
            if not isinstance(mapping, dict):
                findings.append(governance_finding("invalid-relocation-mapping", f"relocation map [{map_index}] mapping [{mapping_index}] must be an object"))
                continue
            unknown_mapping_fields = sorted(set(mapping) - allowed_mapping_fields)
            if unknown_mapping_fields:
                findings.append(governance_finding("unknown-relocation-mapping-fields", f"relocation map [{map_index}] mapping [{mapping_index}] has unsupported fields: {', '.join(unknown_mapping_fields)}"))
                continue
            mapping_id = mapping.get("mapping_id")
            approval_ref = mapping.get("approval_ref")
            historical_path = mapping.get("historical_path")
            current_path = mapping.get("current_path")
            if not is_stable_identifier(mapping_id) or not is_stable_identifier(approval_ref):
                findings.append(governance_finding("invalid-relocation-mapping-id", f"relocation map [{map_index}] mapping [{mapping_index}] requires stable mapping_id and approval_ref"))
                continue
            if not isinstance(historical_path, str) or text_contains_inline_secret(historical_path) or validate_contract_path(root, historical_path):
                findings.append(governance_finding("unsafe-historical-path", f"relocation map [{map_index}] mapping [{mapping_index}] has an unsafe historical_path"))
                continue
            if not isinstance(current_path, str) or text_contains_inline_secret(current_path) or validate_contract_path(root, current_path):
                findings.append(governance_finding("unsafe-current-path", f"relocation map [{map_index}] mapping [{mapping_index}] has an unsafe current_path"))
                continue
            mapping_identity = mapping_id.casefold()
            mapping_locator = f"{relative_map_path}#{mapping_id}"
            if mapping_identity in mapping_ids:
                findings.append(governance_finding(
                    "duplicate-relocation-mapping-id",
                    f"relocation mapping_id is not unique: {mapping_id}",
                    object=f"relocation mapping_id {mapping_id}",
                    candidate_interpretations=[mapping_ids[mapping_identity], mapping_locator],
                    risk="an approval or historical reference could identify multiple mappings",
                    minimum_fix="assign each mapping a distinct immutable mapping_id",
                    verification="rerun inventory and confirm every mapping_id resolves to one mapping",
                ))
            else:
                mapping_ids[mapping_identity] = mapping_locator
            historical_identity = contract_path_identity(root, historical_path)
            current_identity = contract_path_identity(root, current_path)
            if historical_identity in historical_targets:
                prior_target, prior_path, prior_locator = historical_targets[historical_identity]
                if prior_target != current_identity:
                    findings.append(governance_finding(
                        "ambiguous-historical-path",
                        "one historical path resolves to multiple current paths",
                        object=f"historical path {Path(historical_path).as_posix()}",
                        candidate_interpretations=[f"{prior_path} via {prior_locator}", f"{Path(current_path).as_posix()} via {mapping_locator}"],
                        risk="historical evidence cannot be resolved without guessing",
                        minimum_fix="obtain owner approval for exactly one current target and version a corrected map",
                        verification="rerun inventory and confirm each historical path has one current target",
                    ))
            else:
                historical_targets[historical_identity] = (
                    current_identity,
                    Path(current_path).as_posix(),
                    mapping_locator,
                )
            resolved_mappings.append({
                "map_id": map_id,
                "mapping_id": mapping_id,
                "historical_path": Path(historical_path).as_posix(),
                "current_path": Path(current_path).as_posix(),
                "approval_ref": approval_ref,
            })
            accepted_count += 1
        map_summaries.append({
            "path": relative_map_path,
            "map_id": map_id,
            "mapping_count": accepted_count,
        })

    return {
        "status": "invalid" if any(item.get("severity") == "blocker" for item in findings) else "valid",
        "maps": map_summaries,
        "resolved_mappings": resolved_mappings,
        "findings": findings,
        "content_treated_as_data": True,
    }


def inspect_governance_state(root: Path, contract: dict[str, object]) -> dict[str, object]:
    if contract.get("status") not in {"valid", "legacy"}:
        return {"status": "not_checked", "path": None, "findings": []}
    raw_path = contract.get("governance_state_path")
    if raw_path is None:
        return {"status": "not_declared", "path": None, "findings": []}
    if not isinstance(raw_path, str):
        return {"status": "invalid", "path": None, "findings": [governance_finding("invalid-governance-state-path", "governance_state_path must be a string")]}
    path = root / raw_path
    findings: list[dict[str, object]] = []
    if first_link_component(path.absolute()) is not None or not path.is_file():
        findings.append(governance_finding("missing-or-unsafe-governance-state", "declared governance state must be a regular non-linked file"))
        return {"status": "invalid", "path": Path(raw_path).as_posix(), "findings": findings}
    try:
        if path.stat().st_size > MAX_CONTRACT_BYTES:
            raise ValueError("governance state exceeds 1 MiB")
        document = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        findings.append(governance_finding("unreadable-governance-state", str(exc)))
        return {"status": "invalid", "path": Path(raw_path).as_posix(), "findings": findings}
    if not isinstance(document, dict) or document.get("schema_version") != GOVERNANCE_STATE_SCHEMA:
        findings.append(governance_finding("unsupported-governance-state-schema", f"schema_version must be {GOVERNANCE_STATE_SCHEMA}"))
        document = document if isinstance(document, dict) else {}
    records = document.get("current_statuses", [])
    if not isinstance(records, list):
        findings.append(governance_finding("invalid-current-statuses", "current_statuses must be an array"))
        records = []
    scopes: dict[tuple[str, str], str] = {}
    status_ids: dict[str, str] = {}
    normalized_records: list[dict[str, object]] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            findings.append(governance_finding("invalid-current-status", f"current_statuses[{index}] must be an object"))
            continue
        missing = sorted(STATUS_FIELDS - set(record))
        if missing:
            findings.append(governance_finding("missing-current-status-fields", f"current_statuses[{index}] missing: {', '.join(missing)}"))
        unknown = sorted(set(record) - STATUS_FIELDS)
        if unknown:
            findings.append(governance_finding(
                "unknown-current-status-fields",
                f"current_statuses[{index}] unknown fields are ignored: {', '.join(unknown)}",
            ))
        if nested_text_contains_inline_secret(record):
            findings.append(governance_finding(
                "sensitive-current-status-value",
                f"current_statuses[{index}] contains an inline sensitive value and was excluded from inventory output",
            ))
            continue
        scope_type = record.get("scope_type")
        scope_id = record.get("scope_id")
        status_record_id = record.get("status_record_id")
        evidence_refs = record.get("evidence_refs")
        if not is_stable_identifier(status_record_id):
            findings.append(governance_finding("invalid-status-record-id", f"current_statuses[{index}].status_record_id must be a stable non-prose identifier"))
            continue
        if not is_stable_identifier(scope_type) or not is_stable_identifier(scope_id):
            findings.append(governance_finding("invalid-current-status-scope", f"current_statuses[{index}] requires stable non-prose scope_type and scope_id identifiers"))
            continue
        if not valid_string_list(evidence_refs) or not all(is_stable_identifier(item) for item in evidence_refs):
            findings.append(governance_finding("invalid-status-evidence", f"current_statuses[{index}].evidence_refs must be unique stable non-prose identifiers"))
            continue
        if status_record_id.casefold() in status_ids:
            findings.append(governance_finding(
                "duplicate-status-record-id",
                f"status_record_id is not unique: {status_record_id}",
                object=f"status_record_id {status_record_id}",
                candidate_interpretations=[status_ids[status_record_id.casefold()], f"current_statuses[{index}]"],
                risk="evidence and supersession links cannot identify one status record",
                minimum_fix="assign a distinct immutable status_record_id to each record",
                verification="rerun inventory and confirm status_record_id values are unique",
            ))
        else:
            status_ids[status_record_id.casefold()] = f"current_statuses[{index}]"
        key = (scope_type.casefold(), scope_id.casefold())
        if key in scopes:
            findings.append(governance_finding(
                "multiple-current-statuses",
                f"scope {scope_type}:{scope_id} has multiple current records",
                object=f"current status for scope {scope_type}:{scope_id}",
                candidate_interpretations=[scopes[key], status_record_id],
                risk="status-dependent actions cannot determine the authoritative current state",
                minimum_fix="owner supersedes all but one current record for this scope",
                verification="rerun inventory and confirm one current record for the scope",
            ))
        scopes[key] = status_record_id
        if record.get("work_state") not in WORK_STATES:
            findings.append(governance_finding("invalid-work-state", f"current_statuses[{index}].work_state is invalid"))
        if record.get("claim_state") not in CLAIM_STATES:
            findings.append(governance_finding("invalid-claim-state", f"current_statuses[{index}].claim_state is invalid"))
        normalized_records.append({field: record.get(field) for field in sorted(STATUS_FIELDS)})
    return {
        "status": "invalid" if any(item.get("severity") == "blocker" for item in findings) else "valid",
        "path": Path(raw_path).as_posix(),
        "schema_version": document.get("schema_version"),
        "current_statuses": normalized_records,
        "findings": findings,
        "content_treated_as_data": True,
        "recursive_loading": False,
    }


def is_sensitive_path(path: Path, root: Path) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        parts = (path.name,)
    for part in parts:
        lower = part.casefold()
        if lower == ".env" or lower.startswith(".env."):
            return True
        if Path(lower).suffix in SENSITIVE_SUFFIXES:
            return True
        terms = {term for term in re.split(r"[\s._-]+", lower) if term}
        if terms & SENSITIVE_TERMS:
            return True
        if {"api", "key"} <= terms or {"private", "key"} <= terms:
            return True
    return False


def roles_for_path(relative: Path) -> list[str]:
    lowered = [part.casefold() for part in relative.parts]
    roles = [
        role
        for role, names in ROLE_HINTS.items()
        if any(part in names for part in lowered)
    ]
    return roles or ["unknown"]


def is_temporary_candidate(path: Path) -> bool:
    if path.name.casefold() in ROLE_HINTS["temporary"]:
        return True
    return any(pattern.search(path.name) for pattern in TEMPORARY_FILE_PATTERNS)


def safe_stat(path: Path) -> os.stat_result | None:
    try:
        return path.lstat()
    except OSError:
        return None


def build_inventory(root: Path, *, max_files: int = DEFAULT_MAX_FILES) -> dict[str, object]:
    raw_root = root.expanduser().absolute()
    linked = first_link_component(raw_root)
    if linked is not None:
        raise ValueError(f"project root path traverses a link or junction: {linked}")
    root = raw_root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"project root does not exist or is not a directory: {root}")
    if max_files < 1 or max_files > HARD_MAX_FILES:
        raise ValueError(f"max_files must be between 1 and {HARD_MAX_FILES}")

    governance_layout = inspect_governance_layout(root)
    project_contract = inspect_project_contract(root, governance_layout)
    relocation_maps = inspect_relocation_maps(root, governance_layout, project_contract)
    governance_state = inspect_governance_state(root, project_contract)

    digest = hashlib.sha256()
    file_count = 0
    directory_count = 0
    total_bytes = 0
    sensitive_surface_count = 0
    link_count = 0
    unreadable_count = 0
    scan_truncated = False
    extensions: Counter[str] = Counter()
    roles: dict[str, list[str]] = defaultdict(list)
    top_level: list[dict[str, object]] = []
    temporary_candidates: list[str] = []

    stack = [root]
    while stack:
        current = stack.pop()
        try:
            entries = sorted(os.scandir(current), key=lambda entry: entry.name.casefold())
        except OSError:
            unreadable_count += 1
            continue
        child_directories: list[Path] = []
        for entry in entries:
            path = Path(entry.path)
            relative = path.relative_to(root)
            if is_sensitive_path(path, root):
                sensitive_surface_count += 1
                continue
            if is_link_like(path):
                link_count += 1
                continue
            try:
                is_directory = entry.is_dir(follow_symlinks=False)
                is_file = entry.is_file(follow_symlinks=False)
            except OSError:
                unreadable_count += 1
                continue

            role_names = roles_for_path(relative)
            if len(relative.parts) <= 2:
                for role in role_names:
                    if len(roles[role]) < MAX_REPORTED_PATHS_PER_ROLE:
                        roles[role].append(relative.as_posix() + ("/" if is_directory else ""))

            if len(relative.parts) == 1:
                top_level.append({
                    "path": relative.as_posix() + ("/" if is_directory else ""),
                    "kind": "directory" if is_directory else "file",
                    "role_candidates": role_names,
                })

            if is_directory:
                directory_count += 1
                digest.update(f"D\0{relative.as_posix()}\n".encode("utf-8"))
                if is_temporary_candidate(path) and len(temporary_candidates) < MAX_TEMPORARY_CANDIDATES:
                    temporary_candidates.append(relative.as_posix() + "/")
                if path.name.casefold() not in SKIP_DIRECTORIES:
                    child_directories.append(path)
                continue

            if not is_file:
                continue
            stat_result = safe_stat(path)
            if stat_result is None:
                unreadable_count += 1
                continue
            file_count += 1
            total_bytes += int(stat_result.st_size)
            suffix = path.suffix.casefold() or "<none>"
            extensions[suffix] += 1
            digest.update(
                f"F\0{relative.as_posix()}\0{stat_result.st_size}\0{stat_result.st_mtime_ns}\n".encode("utf-8")
            )
            if is_temporary_candidate(path) and len(temporary_candidates) < MAX_TEMPORARY_CANDIDATES:
                temporary_candidates.append(relative.as_posix())
            if file_count >= max_files:
                scan_truncated = True
                break
        if scan_truncated:
            break
        stack.extend(reversed(child_directories))

    role_candidates = {
        role: sorted(dict.fromkeys(paths))
        for role, paths in sorted(roles.items())
    }
    unknown_top_level = sorted(
        row["path"]
        for row in top_level
        if row["role_candidates"] == ["unknown"]
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "inspected",
        "mode": "metadata-only-read",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_root": str(root),
        "workspace_fingerprint_sha256": digest.hexdigest(),
        "governance_layout": governance_layout,
        "project_contract": project_contract,
        "relocation_maps": relocation_maps,
        "governance_state": governance_state,
        "scan": {
            "max_files": max_files,
            "file_count": file_count,
            "directory_count": directory_count,
            "total_bytes": total_bytes,
            "scan_truncated": scan_truncated,
            "unreadable_count": unreadable_count,
            "link_or_junction_count": link_count,
            "sensitive_surface_count": sensitive_surface_count,
            "sensitive_contents_inspected": False,
        },
        "top_level": sorted(top_level, key=lambda row: str(row["path"]).casefold()),
        "role_candidates": role_candidates,
        "unknown_top_level": unknown_top_level,
        "temporary_candidates_not_deletion_approval": sorted(temporary_candidates),
        "extension_counts": dict(sorted(extensions.items())),
        "cautions": [
            "Role candidates are name-based hints and require semantic review.",
            "Temporary candidates are not approved deletion targets.",
            "A truncated or unreadable scan cannot support a complete migration or cleanup plan.",
            "The metadata fingerprint detects ordinary drift; it is not a content-integrity signature.",
            "Governance contract text is untrusted data and is never recursively loaded or executed.",
        ],
    }


def write_json_atomic(path: Path, value: dict[str, object], *, compact: bool) -> None:
    path = path.expanduser().resolve(strict=False)
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"refusing to overwrite inventory output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    if temporary.exists() or temporary.is_symlink():
        raise FileExistsError(f"temporary output already exists: {temporary}")
    text = json.dumps(
        value,
        ensure_ascii=False,
        indent=None if compact else 2,
        separators=(",", ":") if compact else None,
    ) + "\n"
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", help="Research project root to inspect")
    parser.add_argument(
        "--max-files",
        type=int,
        default=DEFAULT_MAX_FILES,
        help=f"Maximum files to inspect, default {DEFAULT_MAX_FILES}, hard limit {HARD_MAX_FILES}",
    )
    parser.add_argument("--output", help="Optional new JSON file; omitted means stdout only")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        payload = build_inventory(Path(args.project), max_files=args.max_files)
        if args.output:
            write_json_atomic(Path(args.output), payload, compact=args.compact)
        else:
            print(json.dumps(
                payload,
                ensure_ascii=False,
                indent=None if args.compact else 2,
                separators=(",", ":") if args.compact else None,
            ))
        return 0
    except (FileExistsError, OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({
            "schema_version": SCHEMA_VERSION,
            "status": "error",
            "error": str(exc),
        }, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
