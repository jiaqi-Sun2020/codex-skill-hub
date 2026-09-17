#!/usr/bin/env python3
"""Plan, create missing agent context, or verify a research project pipeline."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


PIPELINE_PLAN_SCHEMA = "research-project-pipeline-plan/v4"
PIPELINE_RESULT_SCHEMA = "research-project-pipeline-result/v2"
LEGACY_PIPELINE_SCHEMAS = {
    "research-project-pipeline/v1",
    "research-project-pipeline/v2",
    "research-project-pipeline-plan/v3",
}
GENERATOR_SCHEMA = "project-agent-generator/v1"
INVENTORY_SCHEMA = "research-workspace-inventory/v2"
LEGACY_INVENTORY_SCHEMA = "research-workspace-inventory/v1"
COMPARISON_SCHEMA = "research-comparison-record/v2"
DOMAIN_RECORD_SCHEMA = "experiment-protocol-audit-result/v1"
DOMAIN_HANDOFF_SCHEMA = "research-domain-validation-handoff/v1"
MAX_PLAN_BYTES = 5 * 1024 * 1024
MAX_DOMAIN_RECORD_BYTES = 5 * 1024 * 1024
SHA256_PATTERN = re.compile(r"^[A-Fa-f0-9]{64}$")
STABLE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/#-]{0,255}$")
HUMAN_SUMMARY_FIELDS = (
    "what_is_reviewed",
    "why_review_is_required",
    "evidence_to_review",
    "pass_conditions",
    "reject_conditions",
    "after_pass",
    "minimum_repair",
    "what_has_not_been_validated",
)
AGENT_BUNDLE_NAMES = (".agents", ".agent")
REQUIRED_AGENT_FILES = (
    "AGENTS.md",
    "PROJECT_CONTEXT.md",
    "ARCHITECTURE.md",
    "CONFIG_SPEC.md",
    "RUNBOOK.md",
    "DECISIONS.md",
    "README.md",
    "memory/MEMORY.md",
    "memory/maintenance-rules.md",
)


class ComponentError(RuntimeError):
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
        current = current / part
        if current.exists() and is_link_like(current):
            return current
    return None


def resolve_project_root(raw: str) -> Path:
    candidate = Path(raw).expanduser().absolute()
    linked = first_link_component(candidate)
    if linked is not None:
        raise ValueError(f"project root path traverses a link or junction: {linked}")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_dir():
        raise ValueError(f"project root does not exist or is not a directory: {resolved}")
    return resolved


def existing_context_bundles(project: Path) -> list[Path]:
    return [
        project / name
        for name in AGENT_BUNDLE_NAMES
        if (project / name).exists() or (project / name).is_symlink()
    ]


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def canonical_hash(value: dict[str, Any]) -> str:
    content = {key: item for key, item in value.items() if key != "plan_sha256"}
    encoded = json.dumps(
        content,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def component_bindings(components: dict[str, Path | None]) -> dict[str, dict[str, Any]]:
    bindings: dict[str, dict[str, Any]] = {}
    for name, required in (
        ("generator", True),
        ("inventory", True),
        ("knowledge", False),
        ("comparison_validator", False),
        ("domain_validator", False),
    ):
        value = components.get(name)
        available = isinstance(value, Path) and value.is_file()
        bindings[name] = {
            "required": required,
            "available": available,
            "path": str(value.resolve(strict=True)) if available else None,
            "sha256": sha256_file(value) if available else None,
        }
    return bindings


def result_document(outcome: str, **fields: Any) -> dict[str, Any]:
    return {
        "schema_version": PIPELINE_RESULT_SCHEMA,
        "document_type": "pipeline-command-result",
        "command_status": "error" if outcome == "error" else "ok",
        "outcome": outcome,
        **fields,
    }


def resolve_components(args: argparse.Namespace) -> dict[str, Path | None]:
    default_project_build_root = Path(__file__).resolve().parents[2]
    legacy_root = (
        Path(args.core_utils_root).expanduser().resolve()
        if args.core_utils_root
        else None
    )
    project_build_root = (
        Path(args.project_build_root).expanduser().resolve()
        if args.project_build_root
        else legacy_root or default_project_build_root
    )
    reusable_core_root = (
        Path(args.reusable_core_root).expanduser().resolve()
        if args.reusable_core_root
        else legacy_root or default_project_build_root.parent / "50-core-utils"
    )
    generator = (
        Path(args.generator_script).expanduser().resolve()
        if args.generator_script
        else project_build_root / "project-agent-generator-skill" / "scripts" / "generate_project_agents.py"
    )
    inventory = (
        Path(args.inventory_script).expanduser().resolve()
        if args.inventory_script
        else project_build_root / "research-workspace-governance" / "scripts" / "inventory_workspace.py"
    )
    knowledge = (
        Path(args.knowledge_script).expanduser().resolve()
        if args.knowledge_script
        else reusable_core_root / "neat-freak" / "scripts" / "manage_project_knowledge.py"
    )
    comparison_validator = (
        Path(args.comparison_validator_script).expanduser().resolve()
        if args.comparison_validator_script
        else project_build_root
        / "research-workspace-governance"
        / "scripts"
        / "validate_equivalence_records.py"
    )
    domain_validator = (
        Path(args.domain_validator_script).expanduser().resolve()
        if args.domain_validator_script
        else project_build_root
        / "experiment-protocol-audit"
        / "scripts"
        / "audit_experiment_protocol.py"
    )
    for label, path in (("generator", generator), ("inventory", inventory)):
        if not path.is_file():
            raise ComponentError(f"{label} interface not found: {path}")
    return {
        "project_build_root": project_build_root,
        "reusable_core_root": reusable_core_root,
        "generator": generator,
        "inventory": inventory,
        "knowledge": knowledge if knowledge.is_file() else None,
        "comparison_validator": (
            comparison_validator if comparison_validator.is_file() else None
        ),
        "domain_validator": domain_validator if domain_validator.is_file() else None,
    }


def run_process(command: list[str], *, accepted_codes: set[int] | None = None) -> subprocess.CompletedProcess[str]:
    accepted_codes = accepted_codes or {0}
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    process = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=environment,
    )
    if process.returncode not in accepted_codes:
        detail = process.stderr.strip() or process.stdout.strip() or "no diagnostic output"
        raise ComponentError(
            f"component exited with {process.returncode}: {' '.join(command[:3])}: {detail}"
        )
    return process


def parse_component_json(process: subprocess.CompletedProcess[str], label: str) -> dict[str, Any]:
    try:
        payload = json.loads(process.stdout)
    except json.JSONDecodeError as exc:
        raise ComponentError(f"{label} did not emit valid JSON") from exc
    if not isinstance(payload, dict):
        raise ComponentError(f"{label} emitted a non-object JSON payload")
    return payload


def inspect_generator(project: Path, generator: Path) -> dict[str, Any]:
    process = run_process([
        sys.executable,
        "-B",
        "-X",
        "utf8",
        str(generator),
        str(project),
        "--inspect-only",
        "--json",
    ])
    payload = parse_component_json(process, "project-agent generator")
    if payload.get("schema_version") != GENERATOR_SCHEMA or payload.get("status") != "inspected":
        raise ComponentError("unsupported or unsuccessful project-agent inspection")
    return payload


def inspect_workspace(project: Path, inventory: Path) -> dict[str, Any]:
    process = run_process([
        sys.executable,
        "-B",
        "-X",
        "utf8",
        str(inventory),
        str(project),
        "--compact",
    ])
    payload = parse_component_json(process, "research workspace inventory")
    if payload.get("status") != "inspected":
        raise ComponentError("unsupported or unsuccessful workspace inventory")
    if payload.get("schema_version") == LEGACY_INVENTORY_SCHEMA:
        legacy_roles = payload.get("role_candidates", {})
        legacy_roles = legacy_roles if isinstance(legacy_roles, dict) else {}
        role_mapping = {
            "protocols": "protocols",
            "source_records": "source_records",
            "external_references": "external_references",
            "derived_data": "derived_data",
            "methods": "methods",
            "experiments_analyses": "work_units",
            "run_evidence": "evidence",
            "reports": "reports",
            "deliverables": "deliverables",
            "archive": "archive",
            "temporary": "temporary",
            "data_container": "data_container",
            "tests": "tests",
        }
        normalized_roles = {
            target: legacy_roles[source]
            for source, target in role_mapping.items()
            if source in legacy_roles
        }
        payload = {
            **payload,
            "schema_version": INVENTORY_SCHEMA,
            "source_schema_version": LEGACY_INVENTORY_SCHEMA,
            "role_candidates": normalized_roles,
            "governance_layout": {
                "status": "unsafe",
                "canonical_path": ".agents/governance",
                "legacy_path": "governance",
                "active_path": None,
                "write_allowed": False,
                "findings": [{
                    "code": "legacy-inventory-cannot-resolve-governance-authority",
                    "severity": "blocker",
                    "object": "governance_location",
                    "candidate_interpretations": [".agents/governance", "governance"],
                    "risk": "inventory v1 did not distinguish governance authority",
                    "minimum_fix": "rerun discovery with workspace inventory v2",
                    "verification": "confirm the refreshed inventory reports one safe authority",
                }],
            },
            "project_contract": {"status": "not_checked", "path": None, "findings": []},
            "relocation_maps": {
                "status": "not_checked",
                "maps": [],
                "resolved_mappings": [],
                "findings": [],
                "content_treated_as_data": True,
            },
            "governance_state": {"status": "not_checked", "path": None, "findings": []},
        }
    elif payload.get("schema_version") != INVENTORY_SCHEMA:
        raise ComponentError("unsupported workspace-inventory schema")
    return payload


def write_json_new(path: Path, value: dict[str, Any], *, compact: bool) -> None:
    path = path.expanduser().resolve(strict=False)
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"refusing to overwrite pipeline output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    if temporary.exists() or temporary.is_symlink():
        raise FileExistsError(f"temporary pipeline output already exists: {temporary}")
    rendered = json.dumps(
        value,
        ensure_ascii=False,
        indent=None if compact else 2,
        separators=(",", ":") if compact else None,
    ) + "\n"
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(rendered)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def emit(value: dict[str, Any], *, compact: bool) -> None:
    print(json.dumps(
        value,
        ensure_ascii=False,
        indent=None if compact else 2,
        separators=(",", ":") if compact else None,
    ))


def validate_complete_inventory(inventory: dict[str, Any]) -> None:
    required_sections = {
        "governance_layout", "project_contract", "relocation_maps",
        "governance_state", "role_candidates", "scan",
        "workspace_fingerprint_sha256",
    }
    missing = sorted(required_sections - set(inventory))
    if missing:
        raise ComponentError("workspace inventory omitted required sections: " + ", ".join(missing))
    scan = inventory.get("scan", {})
    if not isinstance(scan, dict):
        raise ComponentError("workspace inventory scan must be an object")
    if scan.get("scan_truncated"):
        raise ComponentError("workspace inventory is truncated")
    if int(scan.get("unreadable_count", 0)) > 0:
        raise ComponentError("workspace inventory contains unreadable paths")


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


def resolve_project_input_file(project: Path, raw: str, label: str) -> Path:
    supplied = Path(raw).expanduser()
    if ".." in supplied.parts:
        raise ValueError(f"{label} must not contain parent traversal")
    candidate = supplied if supplied.is_absolute() else project / supplied
    unresolved = candidate.absolute()
    if not is_relative_to(unresolved, project.absolute()):
        raise ValueError(f"{label} must stay inside the target project")
    if linked_component_below(project, unresolved) is not None:
        raise ValueError(f"{label} must not traverse a link or junction")
    resolved = unresolved.resolve(strict=True)
    if not is_relative_to(resolved, project) or not resolved.is_file() or is_link_like(resolved):
        raise ValueError(f"{label} must be a regular project-contained file")
    return resolved


def policy_topology_handoff(project: Path, manifest_arg: str | None) -> dict[str, Any]:
    if not manifest_arg:
        return {
            "schema_version": "agent-loading-audit-handoff/v1",
            "status": "not_declared",
            "owner": "neat-freak",
            "manifest_path": None,
        }
    manifest_path = resolve_project_input_file(project, manifest_arg, "policy topology")
    return {
        "schema_version": "agent-loading-audit-handoff/v1",
        "status": "pending_neat_freak_audit",
        "owner": "neat-freak",
        "manifest_path": manifest_path.relative_to(project).as_posix(),
    }


def findings_from(*sections: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    blockers: list[dict[str, Any]] = []
    non_blockers: list[dict[str, Any]] = []
    for section in sections:
        if not isinstance(section, dict):
            continue
        findings = section.get("findings", [])
        if not isinstance(findings, list):
            continue
        for finding in findings:
            if not isinstance(finding, dict):
                continue
            blocked_scopes = finding.get("blocks", [])
            scoped_only = (
                isinstance(blocked_scopes, list)
                and bool(blocked_scopes)
                and "context_creation" not in blocked_scopes
                and "workspace_onboarding" not in blocked_scopes
            )
            if finding.get("severity") in {"non_blocker", "finding"} or scoped_only:
                non_blockers.append(finding)
            else:
                blockers.append(finding)
    return blockers, non_blockers


def review_gate_inputs(
    *,
    blockers: list[dict[str, Any]],
    non_blockers: list[dict[str, Any]],
    evidence: list[str],
    unvalidated: list[str] | None = None,
) -> dict[str, Any]:
    suggested_actions = [
        "Resolve the first blocker and rerun read-only discovery."
        if blockers
        else "Review the exact component actions and workspace fingerprint."
    ]
    return {
        "result": "fail" if blockers else "conditional",
        "scope": {"type": "project", "id": "research-project-integration"},
        "blockers": blockers,
        "non_blockers": non_blockers,
        "evidence": evidence,
        "suggested_actions": suggested_actions,
        "allowed_actions": ["human_review"],
        "forbidden_actions": [
            "migration",
            "overwrite",
            "deletion",
            "unreviewed_agent_context_change",
        ],
        "human_summary_required": True,
        "human_summary_language": "current-user-language",
        "human_summary_source": {
            "what_is_reviewed": [
                "The proposed component actions, governance authority, current state, and evidence boundaries."
            ],
            "why_review_is_required": [
                "Approval is the boundary between read-only discovery and any controlled change."
            ],
            "evidence_to_review": list(evidence),
            "pass_conditions": [
                "No blocker remains, the evidence matches the intended project, and the named owner is authorized."
            ],
            "reject_conditions": [
                "Reject when any blocker, ambiguous authority, unsafe path, stale component, or unsupported action remains."
            ],
            "after_pass": [
                "Only the explicitly listed action may proceed through its named owning component."
            ],
            "minimum_repair": suggested_actions,
            "what_has_not_been_validated": (
                unvalidated
                if unvalidated is not None
                else [
                    "Domain methods, experiment validity, and scientific claims are outside this gate unless a current domain-validation handoff says otherwise."
                ]
            ),
            "render_language": "current-user-language",
            "render_required": True,
        },
    }


def run_comparison_validation(project: Path, script: Path | None, records_arg: str | None) -> dict[str, Any]:
    if not records_arg:
        return {
            "schema_version": COMPARISON_SCHEMA,
            "status": "not_declared",
            "records_path": None,
            "findings": [],
            "records": [],
            "summary": {"exit_code": 0, "record_count": 0, "verified_count": 0, "finding_count": 0},
        }
    if script is None:
        raise ComponentError("comparison validator interface is unavailable")
    records_path = resolve_project_input_file(project, records_arg, "comparison records")
    process = run_process(
        [sys.executable, "-B", "-X", "utf8", str(script), str(records_path), "--project-root", str(project), "--compact"],
        accepted_codes={0, 1, 2},
    )
    payload = parse_component_json(process, "comparison validator")
    if payload.get("schema_version") != COMPARISON_SCHEMA:
        raise ComponentError("unsupported comparison-validator schema")
    if not isinstance(payload.get("summary"), dict):
        raise ComponentError("comparison validator omitted its summary")
    payload["records_path"] = records_path.relative_to(project).as_posix()
    payload["summary"]["exit_code"] = process.returncode
    return payload


def scoped_domain_finding(
    code: str,
    risk: str,
    minimum_fix: str,
    verification: str,
) -> dict[str, Any]:
    return {
        "code": code,
        "severity": "scoped_blocker",
        "blocks": ["experiment_execution", "claim_support"],
        "does_not_block": ["context_creation", "workspace_onboarding"],
        "risk": risk,
        "minimum_fix": minimum_fix,
        "verification": verification,
    }


def domain_requirement(raw: str) -> str:
    return raw.replace("-", "_")


def validate_fingerprint_entries(
    project: Path,
    entries: Any,
    label: str,
    *,
    require_kind: bool = False,
) -> tuple[list[dict[str, str]], bool]:
    if not isinstance(entries, list):
        raise ValueError(f"domain validation {label} must be an array")
    normalized: list[dict[str, str]] = []
    stale = False
    for index, item in enumerate(entries):
        if not isinstance(item, dict):
            raise ValueError(f"domain validation {label}[{index}] must be an object")
        raw_path = item.get("path")
        expected_hash = item.get("sha256")
        kind = item.get("kind") if require_kind else None
        if not isinstance(raw_path, str) or not raw_path.strip():
            raise ValueError(f"domain validation {label}[{index}] needs a path")
        if not isinstance(expected_hash, str) or not SHA256_PATTERN.fullmatch(expected_hash):
            raise ValueError(f"domain validation {label}[{index}] needs SHA-256")
        if require_kind and (not isinstance(kind, str) or not kind.strip()):
            raise ValueError(f"domain validation {label}[{index}] needs a kind")
        path = resolve_project_input_file(project, raw_path, f"domain validation {label}")
        relative = path.relative_to(project).as_posix()
        actual_hash = sha256_file(path)
        stale = stale or actual_hash.casefold() != expected_hash.casefold()
        normalized_item = {"path": relative, "sha256": expected_hash.casefold()}
        if require_kind:
            normalized_item["kind"] = str(kind)
        normalized.append(normalized_item)
    return normalized, stale


def build_domain_validation_handoff(
    project: Path,
    components: dict[str, Path | None],
    record_arg: str | None,
    requirement_raw: str,
    owner_override: str | None = None,
) -> dict[str, Any]:
    requirement = domain_requirement(requirement_raw)
    allowed_requirements = {"required", "optional", "not_applicable", "review_required"}
    if requirement not in allowed_requirements:
        raise ValueError("unsupported domain-validation requirement")
    if not record_arg:
        if owner_override is not None and (not owner_override.strip() or requirement != "not_applicable"):
            raise ValueError("--domain-validation-owner is only valid with a non-empty not-applicable declaration")
        if requirement == "not_applicable" and owner_override:
            return {
                "schema_version": DOMAIN_HANDOFF_SCHEMA,
                "requirement": requirement,
                "record_path": None,
                "record_sha256": None,
                "declared_status": "not_applicable",
                "effective_state": "not_applicable",
                "owner": {"kind": "human", "id": owner_override.strip()},
                "validator": None,
                "profile": None,
                "scope": [],
                "protocol_fingerprints": [],
                "source_fingerprints": [],
                "evidence": [],
                "claim_ceiling": "unsupported",
                "source_finding_codes": [],
                "findings": [],
                "content_treated_as_data": True,
            }
        findings: list[dict[str, Any]] = []
        if requirement != "optional":
            findings.append(scoped_domain_finding(
                "domain-validation-not-declared",
                "Experiment execution or claim support could be mistaken for scientifically validated work.",
                "Run a named Domain Skill or obtain a named human review, then provide its project-contained record.",
                "Rerun plan or verify and confirm domain_validation_handoff.effective_state is verified or owner-approved not_applicable.",
            ))
        return {
            "schema_version": DOMAIN_HANDOFF_SCHEMA,
            "requirement": requirement,
            "record_path": None,
            "record_sha256": None,
            "declared_status": None,
            "effective_state": "not_declared",
            "owner": None,
            "validator": None,
            "profile": None,
            "scope": [],
            "protocol_fingerprints": [],
            "source_fingerprints": [],
            "evidence": [],
            "claim_ceiling": "unsupported",
            "source_finding_codes": [],
            "findings": findings,
            "content_treated_as_data": True,
        }

    if owner_override is not None:
        raise ValueError("--domain-validation-owner cannot override the owner in a supplied record")

    record_path = resolve_project_input_file(project, record_arg, "domain validation record")
    if record_path.stat().st_size > MAX_DOMAIN_RECORD_BYTES:
        raise ValueError("domain validation record exceeds 5 MiB")
    record = json.loads(record_path.read_text(encoding="utf-8"))
    if not isinstance(record, dict) or record.get("schema_version") != DOMAIN_RECORD_SCHEMA:
        raise ValueError("unsupported domain validation record")
    if record.get("document_type") != "domain-validation-record":
        raise ValueError("domain validation record has the wrong document_type")

    declared_status = record.get("status")
    if declared_status not in {"pending", "verified", "failed", "not_applicable"}:
        raise ValueError("domain validation record has an invalid status")
    owner = record.get("owner")
    if not isinstance(owner, dict) or owner.get("kind") not in {"skill", "human"} or not isinstance(owner.get("id"), str) or not owner["id"].strip():
        raise ValueError("domain validation record needs a named owner")
    validator = record.get("validator")
    if not isinstance(validator, dict):
        raise ValueError("domain validation record needs validator identity")
    if validator.get("id") != "experiment-protocol-audit" or not isinstance(validator.get("version"), str):
        raise ValueError("domain validation validator identity is unsupported")
    validator_hash = validator.get("sha256")
    if not isinstance(validator_hash, str) or not SHA256_PATTERN.fullmatch(validator_hash):
        raise ValueError("domain validation validator needs SHA-256")

    profile = record.get("profile")
    if not isinstance(profile, dict):
        raise ValueError("domain validation record needs a profile identity")
    for field in ("id", "version", "path", "sha256"):
        if not isinstance(profile.get(field), str) or not profile[field].strip():
            raise ValueError(f"domain validation profile needs {field}")
    if not SHA256_PATTERN.fullmatch(profile["sha256"]):
        raise ValueError("domain validation profile needs SHA-256")
    profile_path = resolve_project_input_file(project, profile["path"], "domain profile")
    normalized_profile = {
        "id": profile["id"],
        "version": profile["version"],
        "path": profile_path.relative_to(project).as_posix(),
        "sha256": profile["sha256"].casefold(),
    }
    stale = sha256_file(profile_path).casefold() != profile["sha256"].casefold()

    scope = record.get("scope")
    if not isinstance(scope, list) or not scope or len(scope) != len(set(scope)) or not set(scope) <= {"design", "manifest", "runtime"}:
        raise ValueError("domain validation scope must contain unique supported scopes")
    protocol_fingerprints, protocol_stale = validate_fingerprint_entries(
        project, record.get("protocol_fingerprints"), "protocol_fingerprints"
    )
    source_fingerprints, source_stale = validate_fingerprint_entries(
        project, record.get("source_fingerprints"), "source_fingerprints"
    )
    evidence, evidence_stale = validate_fingerprint_entries(
        project, record.get("evidence"), "evidence", require_kind=True
    )
    stale = stale or protocol_stale or source_stale or evidence_stale

    source_findings = record.get("findings", [])
    if not isinstance(source_findings, list):
        raise ValueError("domain validation findings must be an array")
    if any(not isinstance(item, dict) or not isinstance(item.get("code"), str) for item in source_findings):
        raise ValueError("domain validation findings must be structured objects with codes")
    source_finding_codes = sorted({
        str(item.get("code"))
        for item in source_findings
        if isinstance(item, dict) and isinstance(item.get("code"), str)
    })
    claim_ceiling = record.get("claim_ceiling")
    if claim_ceiling not in {"unsupported", "diagnostic_only", "conditionally_supported", "supported"}:
        raise ValueError("domain validation claim_ceiling is invalid")

    findings: list[dict[str, Any]] = []
    validator_path = components.get("domain_validator")
    if not isinstance(validator_path, Path):
        findings.append(scoped_domain_finding(
            "domain-validator-unavailable",
            "The validator implementation named by the record cannot be independently bound.",
            "Restore the central experiment-protocol-audit Skill or pass its reviewed script path explicitly.",
            "Confirm the validator binding exists and its SHA-256 matches the record.",
        ))
        effective_state = "invalid"
    elif sha256_file(validator_path).casefold() != validator_hash.casefold():
        findings.append(scoped_domain_finding(
            "domain-validator-stale",
            "The validator implementation changed after the scientific decision was recorded.",
            "Rerun the domain audit with the current validator and produce a new record.",
            "Confirm the current validator SHA-256 matches the new record.",
        ))
        effective_state = "stale"
    elif stale:
        findings.append(scoped_domain_finding(
            "domain-validation-evidence-stale",
            "A profile, protocol, source, or evidence file changed after validation.",
            "Rerun the domain audit against the current files instead of rewriting the old record.",
            "Confirm every recorded fingerprint matches the current project-contained file.",
        ))
        effective_state = "stale"
    else:
        effective_state = str(declared_status)

    if declared_status == "verified" and (not evidence or not protocol_fingerprints or not source_fingerprints):
        raise ValueError("verified domain validation needs protocol, source, and evidence fingerprints")
    if declared_status == "verified" and any(item.get("severity") in {"blocker", "scoped_blocker"} for item in source_findings):
        effective_state = "invalid"
        findings.append(scoped_domain_finding(
            "domain-validation-status-conflict",
            "The record declares verified while retaining a blocking source finding.",
            "Resolve the source finding or mark the record failed; never relabel a failing record as verified.",
            "Confirm a new record has a status consistent with all structured findings.",
        ))
    if declared_status == "failed":
        findings.append(scoped_domain_finding(
            "domain-validation-failed",
            "The named domain review found blocking scientific or protocol defects.",
            "Resolve the Domain Skill findings and produce a new versioned validation record.",
            "Rerun the domain audit and confirm the new record is verified.",
        ))
    elif declared_status == "pending":
        findings.append(scoped_domain_finding(
            "domain-validation-pending",
            "The domain review has not reached a scientific decision.",
            "Complete the declared review scopes and produce evidence-bound results.",
            "Confirm the effective state becomes verified.",
        ))
    if requirement == "required" and declared_status == "not_applicable":
        effective_state = "invalid"
        findings.append(scoped_domain_finding(
            "domain-validation-requirement-conflict",
            "The project requires domain validation but the supplied record declares it not applicable.",
            "Resolve the requirement with the project owner and produce a consistent record.",
            "Confirm requirement and declared status no longer conflict.",
        ))
    if requirement == "not_applicable" and declared_status != "not_applicable":
        effective_state = "invalid"
        findings.append(scoped_domain_finding(
            "domain-validation-requirement-conflict",
            "The invocation declares validation not applicable but the record declares another state.",
            "Use the correct explicit requirement or obtain an owner-reviewed not-applicable record.",
            "Confirm requirement and declared status match.",
        ))

    effective_claim = claim_ceiling if effective_state == "verified" else "unsupported"
    return {
        "schema_version": DOMAIN_HANDOFF_SCHEMA,
        "requirement": requirement,
        "record_path": record_path.relative_to(project).as_posix(),
        "record_sha256": sha256_file(record_path),
        "declared_status": declared_status,
        "effective_state": effective_state,
        "owner": {"kind": owner["kind"], "id": owner["id"]},
        "validator": {
            "id": validator["id"],
            "version": validator["version"],
            "sha256": validator_hash.casefold(),
        },
        "profile": normalized_profile,
        "scope": list(scope),
        "protocol_fingerprints": protocol_fingerprints,
        "source_fingerprints": source_fingerprints,
        "evidence": evidence,
        "claim_ceiling": effective_claim,
        "source_finding_codes": source_finding_codes,
        "findings": findings,
        "content_treated_as_data": True,
    }


def readiness_axes(
    *,
    onboarding_state: str,
    agent_context_state: str,
    governance_state: str,
    domain_handoff: dict[str, Any],
    execution_ready: bool = False,
) -> dict[str, str]:
    domain_state = str(domain_handoff["effective_state"])
    claim_state = str(domain_handoff["claim_ceiling"]) if domain_state == "verified" else "unsupported"
    execution_state = (
        "ready_for_authorization"
        if execution_ready and domain_state in {"verified", "not_applicable"}
        else "blocked"
        if domain_state in {"failed", "stale", "invalid"}
        else "not_authorized"
    )
    return {
        "onboarding_state": onboarding_state,
        "agent_context_state": agent_context_state,
        "governance_state": governance_state,
        "domain_validation_state": domain_state,
        "execution_state": execution_state,
        "claim_state": claim_state,
    }


def build_plan(
    project: Path,
    profile: str,
    components: dict[str, Path | None],
    *,
    policy_topology: str | None = None,
    comparison_records: str | None = None,
    domain_validation_record: str | None = None,
    domain_validation_requirement: str = "review-required",
    domain_validation_owner: str | None = None,
) -> dict[str, Any]:
    generator = inspect_generator(project, components["generator"])  # type: ignore[arg-type]
    inventory = inspect_workspace(project, components["inventory"])  # type: ignore[arg-type]
    validate_complete_inventory(inventory)
    roles = inventory.get("role_candidates", {})
    governance_layout = inventory.get("governance_layout", {})
    project_contract = inventory.get("project_contract", {})
    relocation_maps = inventory.get("relocation_maps", {})
    governance_state = inventory.get("governance_state", {})
    governance_status = governance_layout.get("status") if isinstance(governance_layout, dict) else None
    contract_status = project_contract.get("status") if isinstance(project_contract, dict) else None
    state_status = governance_state.get("status") if isinstance(governance_state, dict) else None
    relocation_status = relocation_maps.get("status") if isinstance(relocation_maps, dict) else None
    context_bundles = existing_context_bundles(project)
    context_exists = bool(context_bundles)
    loading_handoff = policy_topology_handoff(project, policy_topology)
    comparison = run_comparison_validation(
        project,
        components["comparison_validator"],  # type: ignore[arg-type]
        comparison_records,
    )
    domain_handoff = build_domain_validation_handoff(
        project,
        components,
        domain_validation_record,
        domain_validation_requirement,
        domain_validation_owner,
    )
    blockers, non_blockers = findings_from(
        governance_layout,
        project_contract,
        relocation_maps,
        governance_state,
        comparison,
        domain_handoff,
    )
    governance_blocked = (
        governance_status in {"ambiguous", "unsafe"}
        or contract_status == "invalid"
        or relocation_status == "invalid"
        or state_status == "invalid"
        or comparison.get("status") == "invalid"
    )
    fingerprint = str(inventory["workspace_fingerprint_sha256"])
    pipeline_id = hashlib.sha256(
        (
            f"{project}|{fingerprint}|{profile}|"
            f"{domain_handoff['requirement']}|{domain_handoff['record_sha256']}|{domain_handoff['owner']}"
        ).encode("utf-8")
    ).hexdigest()[:16]
    readiness = readiness_axes(
        onboarding_state="blocked" if governance_blocked else "review_required",
        agent_context_state="preserved" if context_exists else "pending_generation",
        governance_state="blocked" if governance_blocked else "review_required",
        domain_handoff=domain_handoff,
    )
    plan: dict[str, Any] = {
        "schema_version": PIPELINE_PLAN_SCHEMA,
        "document_type": "pipeline-plan",
        "pipeline_id": pipeline_id,
        "plan_sha256": "",
        "status": "review_required",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_root": str(project),
        "workspace_fingerprint_sha256": fingerprint,
        "profile": profile,
        "context_action": "preserve_and_audit" if context_exists else "create_after_framework",
        "context_locations": [path.name for path in context_bundles],
        "component_interfaces": {
            "project_agent_generator": generator["schema_version"],
            "research_workspace_inventory": inventory["schema_version"],
            "knowledge_auditor_available": components["knowledge"] is not None,
            "agent_loading_auditor": "neat-freak",
            "comparison_validator": comparison["schema_version"],
            "domain_validator_available": components["domain_validator"] is not None,
            "domain_validation_handoff": DOMAIN_HANDOFF_SCHEMA,
        },
        "component_bindings": component_bindings(components),
        "governance_layout": governance_layout,
        "project_contract": project_contract,
        "relocation_maps": relocation_maps,
        "governance_state": governance_state,
        "agent_loading_audit_handoff": loading_handoff,
        "comparison_contracts": comparison,
        "domain_validation_handoff": domain_handoff,
        "readiness": readiness,
        "role_hints_for_semantic_review": roles,
        "review_gate_inputs": review_gate_inputs(
            blockers=blockers,
            non_blockers=non_blockers,
            evidence=[
                "governance_layout",
                "project_contract",
                "relocation_maps",
                "governance_state",
                "comparison_contracts",
                "domain_validation_handoff",
                "readiness",
                "workspace_fingerprint_sha256",
                "component_actions",
            ],
            unvalidated=(
                [
                    "Validation remains limited to the declared Profile, scopes, evidence fingerprints, and claim ceiling; undeclared assumptions are not validated."
                ]
                if domain_handoff["effective_state"] == "verified"
                else [
                    "Scientific validity and claim support remain unvalidated; this does not block project onboarding or Agent-context creation."
                ]
            ),
        ),
        "stages": [
            {"name": "discover", "status": "complete", "mutation": False},
            {"name": "design", "status": "blocked" if governance_blocked else "review_required", "mutation": False},
            {"name": "human_review", "status": "required", "mutation": False},
            {"name": "controlled_change", "status": "blocked_by_review", "mutation": True},
            {"name": "verify", "status": "pending", "mutation": False},
            {"name": "handoff_or_archive", "status": "pending", "mutation": False},
        ],
        "component_actions": [
            {
                "component": "project-agent-generator-skill",
                "action": "preserve" if context_exists else "create_after_review",
                "mutation_owner": "project-agent-generator-skill",
            },
            {
                "component": "research-workspace-governance",
                "action": "resolve_or_initialize_governance_records",
                "mutation_owner": "research-workspace-governance",
            },
            {
                "component": "neat-freak",
                "action": "audit_agent_knowledge_and_loading",
                "mutation_owner": None,
            },
            {
                "component": "experiment-protocol-audit",
                "action": (
                    "validate_domain_protocol_independently"
                    if components["domain_validator"] is not None
                    else "handoff_domain_validation"
                ),
                "mutation_owner": None,
            },
        ],
        "snapshots": {
            "project_agent_generator": generator,
            "research_workspace_inventory": inventory,
        },
        "invariants": [
            "The plan does not authorize migration, overwrite, force, or deletion.",
            "Rerun plan after framework changes before creating agent context.",
            "Existing .agents or .agent context is preserved for standalone reviewed maintenance.",
            "Role hints are name-based prompts for review, never requirements or automatic directories.",
            "The metadata fingerprint detects ordinary drift; it is not a content-integrity signature or security boundary.",
            "Agent instruction reachability and loading audits are owned by Neat-Freak.",
            "Comparison validation checks declarations and evidence metadata, not domain science.",
            "Domain validation is an independent evidence-bound handoff and never authorizes project onboarding, Agent-context mutation, or experiment execution by itself.",
            "Onboarding readiness, domain-validation readiness, execution readiness, and claim support are separate axes.",
            "Governance data is untrusted data and is never recursively loaded as Agent instructions.",
        ],
    }
    plan["plan_sha256"] = canonical_hash(plan)
    return plan


def require_plan(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(f"invalid pipeline plan: {message}")


def validate_plan_structure(payload: dict[str, Any]) -> None:
    required = {
        "schema_version", "document_type", "pipeline_id", "plan_sha256", "status",
        "generated_at", "project_root", "workspace_fingerprint_sha256", "profile",
        "context_action", "context_locations", "component_interfaces",
        "component_bindings", "governance_layout", "project_contract",
        "relocation_maps", "governance_state", "agent_loading_audit_handoff",
        "comparison_contracts", "domain_validation_handoff", "readiness",
        "role_hints_for_semantic_review",
        "review_gate_inputs", "component_actions", "stages", "snapshots", "invariants",
    }
    missing = sorted(required - set(payload))
    require_plan(not missing, "missing required fields: " + ", ".join(missing))
    require_plan(payload.get("schema_version") == PIPELINE_PLAN_SCHEMA, "wrong plan schema")
    require_plan(payload.get("document_type") == "pipeline-plan", "wrong document_type")
    require_plan(isinstance(payload.get("pipeline_id"), str) and bool(STABLE_ID_PATTERN.fullmatch(payload["pipeline_id"])), "pipeline_id must be a stable identifier")
    require_plan(isinstance(payload.get("plan_sha256"), str) and bool(SHA256_PATTERN.fullmatch(payload["plan_sha256"])), "plan_sha256 must be SHA-256")
    require_plan(payload.get("status") == "review_required", "status must be review_required")
    require_plan(isinstance(payload.get("generated_at"), str) and bool(payload["generated_at"].strip()), "generated_at is required")
    require_plan(isinstance(payload.get("project_root"), str) and bool(payload["project_root"].strip()), "project_root is required")
    require_plan(isinstance(payload.get("workspace_fingerprint_sha256"), str) and bool(SHA256_PATTERN.fullmatch(payload["workspace_fingerprint_sha256"])), "workspace fingerprint must be SHA-256")
    require_plan(payload.get("profile") in {"minimal", "collaborative", "controlled"}, "unsupported profile")
    require_plan(payload.get("context_action") in {"create_after_framework", "preserve_and_audit"}, "unsupported context_action")
    locations = payload.get("context_locations")
    require_plan(isinstance(locations, list) and all(item in AGENT_BUNDLE_NAMES for item in locations) and len(locations) == len(set(locations)), "context_locations must contain unique supported bundle names")
    require_plan((payload["context_action"] == "create_after_framework" and not locations) or (payload["context_action"] == "preserve_and_audit" and bool(locations)), "context_action conflicts with context_locations")

    interfaces = payload.get("component_interfaces")
    interface_fields = {
        "project_agent_generator", "research_workspace_inventory",
        "knowledge_auditor_available", "agent_loading_auditor", "comparison_validator",
        "domain_validator_available", "domain_validation_handoff",
    }
    require_plan(isinstance(interfaces, dict) and interface_fields <= set(interfaces), "component_interfaces is incomplete")
    require_plan(interfaces.get("project_agent_generator") == GENERATOR_SCHEMA, "generator interface mismatch")
    require_plan(interfaces.get("research_workspace_inventory") == INVENTORY_SCHEMA, "inventory interface mismatch")
    require_plan(isinstance(interfaces.get("knowledge_auditor_available"), bool), "knowledge auditor availability must be boolean")
    require_plan(interfaces.get("agent_loading_auditor") == "neat-freak", "Agent loading audit owner must be neat-freak")
    require_plan(interfaces.get("comparison_validator") == COMPARISON_SCHEMA, "comparison interface mismatch")
    require_plan(isinstance(interfaces.get("domain_validator_available"), bool), "domain validator availability must be boolean")
    require_plan(interfaces.get("domain_validation_handoff") == DOMAIN_HANDOFF_SCHEMA, "domain-validation handoff interface mismatch")

    bindings = payload.get("component_bindings")
    expected_bindings = {"generator", "inventory", "knowledge", "comparison_validator", "domain_validator"}
    require_plan(isinstance(bindings, dict) and expected_bindings == set(bindings), "component_bindings must identify all five interfaces")
    for name in sorted(expected_bindings):
        binding = bindings.get(name)
        require_plan(isinstance(binding, dict), f"component binding {name} must be an object")
        require_plan(set(binding) == {"required", "available", "path", "sha256"}, f"component binding {name} has unexpected fields")
        expected_required = name in {"generator", "inventory"}
        require_plan(binding.get("required") is expected_required, f"component binding {name} has wrong required flag")
        require_plan(isinstance(binding.get("available"), bool), f"component binding {name} availability must be boolean")
        require_plan(not expected_required or binding.get("available") is True, f"required component {name} is unavailable")
        if binding.get("available"):
            binding_path = binding.get("path")
            require_plan(isinstance(binding_path, str) and Path(binding_path).is_absolute(), f"component binding {name} needs an absolute path")
            require_plan(isinstance(binding.get("sha256"), str) and bool(SHA256_PATTERN.fullmatch(binding["sha256"])), f"component binding {name} needs SHA-256")
        else:
            require_plan(binding.get("path") is None and binding.get("sha256") is None, f"unavailable component {name} must not carry path or hash")
    require_plan(
        interfaces.get("knowledge_auditor_available") is bindings["knowledge"]["available"],
        "knowledge auditor interface conflicts with its component binding",
    )
    require_plan(
        interfaces.get("domain_validator_available") is bindings["domain_validator"]["available"],
        "domain validator interface conflicts with its component binding",
    )

    section_statuses = {
        "governance_layout": {"canonical", "legacy", "absent", "ambiguous", "unsafe"},
        "project_contract": {"valid", "legacy", "invalid", "absent", "not_checked"},
        "relocation_maps": {"valid", "invalid", "not_declared", "not_checked"},
        "governance_state": {"valid", "invalid", "not_declared", "not_checked"},
    }
    for name, statuses in section_statuses.items():
        section = payload.get(name)
        require_plan(isinstance(section, dict), f"{name} must be an object")
        require_plan(section.get("status") in statuses, f"{name} has an invalid status")
        require_plan(isinstance(section.get("findings"), list), f"{name}.findings must be an array")
    layout = payload["governance_layout"]
    require_plan(layout.get("canonical_path") == ".agents/governance" and layout.get("legacy_path") == "governance", "governance path contract changed")
    require_plan(isinstance(layout.get("write_allowed"), bool), "governance write_allowed must be boolean")
    relocation = payload["relocation_maps"]
    require_plan(isinstance(relocation.get("maps"), list) and isinstance(relocation.get("resolved_mappings"), list), "relocation map resolution is incomplete")
    require_plan(relocation.get("content_treated_as_data") is True, "relocation maps must be treated as data")

    handoff = payload.get("agent_loading_audit_handoff")
    require_plan(isinstance(handoff, dict), "agent loading handoff must be an object")
    require_plan(handoff.get("schema_version") == "agent-loading-audit-handoff/v1" and handoff.get("owner") == "neat-freak", "Agent loading handoff owner or schema changed")
    require_plan(handoff.get("status") in {"not_declared", "pending_neat_freak_audit"}, "invalid Agent loading handoff status")
    require_plan(isinstance(handoff.get("manifest_path"), str) or handoff.get("manifest_path") is None, "invalid Agent loading manifest path")
    comparison = payload.get("comparison_contracts")
    require_plan(isinstance(comparison, dict) and comparison.get("schema_version") == COMPARISON_SCHEMA, "comparison contract schema mismatch")
    require_plan(comparison.get("status") in {"not_declared", "verified", "unverified", "invalid"}, "invalid comparison status")
    require_plan(all(isinstance(comparison.get(field), expected) for field, expected in (("records", list), ("findings", list), ("summary", dict))), "comparison contract is incomplete")

    domain_handoff = payload.get("domain_validation_handoff")
    require_plan(isinstance(domain_handoff, dict), "domain-validation handoff must be an object")
    domain_fields = {
        "schema_version", "requirement", "record_path", "record_sha256",
        "declared_status", "effective_state", "owner", "validator", "profile",
        "scope", "protocol_fingerprints", "source_fingerprints", "evidence",
        "claim_ceiling", "source_finding_codes", "findings", "content_treated_as_data",
    }
    require_plan(domain_fields <= set(domain_handoff), "domain-validation handoff is incomplete")
    require_plan(domain_handoff.get("schema_version") == DOMAIN_HANDOFF_SCHEMA, "domain-validation handoff schema mismatch")
    require_plan(domain_handoff.get("requirement") in {"required", "optional", "not_applicable", "review_required"}, "invalid domain-validation requirement")
    require_plan(domain_handoff.get("effective_state") in {"not_declared", "pending", "verified", "failed", "not_applicable", "stale", "invalid"}, "invalid effective domain-validation state")
    require_plan(domain_handoff.get("claim_ceiling") in {"unsupported", "diagnostic_only", "conditionally_supported", "supported"}, "invalid domain-validation claim ceiling")
    require_plan(domain_handoff.get("content_treated_as_data") is True, "domain-validation content must be treated as data")
    for field in ("scope", "protocol_fingerprints", "source_fingerprints", "evidence", "source_finding_codes", "findings"):
        require_plan(isinstance(domain_handoff.get(field), list), f"domain-validation {field} must be an array")
    if domain_handoff.get("record_path") is None:
        require_plan(domain_handoff.get("record_sha256") is None, "missing domain record must not carry a hash")
    else:
        require_plan(isinstance(domain_handoff.get("record_path"), str), "domain record path must be a string")
        require_plan(isinstance(domain_handoff.get("record_sha256"), str) and bool(SHA256_PATTERN.fullmatch(domain_handoff["record_sha256"])), "domain record hash must be SHA-256")
    if domain_handoff.get("effective_state") != "verified":
        require_plan(domain_handoff.get("claim_ceiling") == "unsupported", "unverified domain work cannot support claims")

    readiness = payload.get("readiness")
    readiness_fields = {
        "onboarding_state", "agent_context_state", "governance_state",
        "domain_validation_state", "execution_state", "claim_state",
    }
    require_plan(isinstance(readiness, dict) and set(readiness) == readiness_fields, "readiness axes are incomplete")
    require_plan(readiness.get("onboarding_state") in {"review_required", "ready", "conditional", "blocked"}, "invalid onboarding readiness")
    require_plan(readiness.get("agent_context_state") in {"pending_generation", "preserved", "ready", "blocked"}, "invalid Agent-context readiness")
    require_plan(readiness.get("governance_state") in {"review_required", "ready", "conditional", "blocked"}, "invalid governance readiness")
    require_plan(readiness.get("domain_validation_state") == domain_handoff.get("effective_state"), "domain readiness conflicts with handoff")
    require_plan(readiness.get("execution_state") in {"not_authorized", "ready_for_authorization", "blocked"}, "invalid execution readiness")
    require_plan(readiness.get("claim_state") == domain_handoff.get("claim_ceiling"), "claim readiness conflicts with handoff")
    require_plan(isinstance(payload.get("role_hints_for_semantic_review"), dict), "role hints must be an object")

    gate = payload.get("review_gate_inputs")
    gate_fields = {
        "result", "scope", "blockers", "non_blockers", "evidence",
        "suggested_actions", "allowed_actions", "forbidden_actions",
        "human_summary_required", "human_summary_language", "human_summary_source",
    }
    require_plan(isinstance(gate, dict) and gate_fields <= set(gate), "review_gate_inputs is incomplete")
    require_plan(gate.get("result") in {"conditional", "fail"}, "invalid review gate result")
    require_plan(isinstance(gate.get("scope"), dict) and gate["scope"].get("type") == "project", "review gate scope must be project")
    for field in ("blockers", "non_blockers", "evidence", "suggested_actions", "allowed_actions", "forbidden_actions"):
        require_plan(isinstance(gate.get(field), list), f"review gate {field} must be an array")
    expected_blockers, expected_non_blockers = findings_from(
        payload["governance_layout"],
        payload["project_contract"],
        payload["relocation_maps"],
        payload["governance_state"],
        comparison,
        domain_handoff,
    )
    require_plan(gate["blockers"] == expected_blockers, "review gate blockers do not match component findings")
    require_plan(gate["non_blockers"] == expected_non_blockers, "review gate non-blockers do not match component findings")
    require_plan((bool(gate["blockers"]) and gate["result"] == "fail") or (not gate["blockers"] and gate["result"] == "conditional"), "review gate result conflicts with blocker state")
    require_plan(gate.get("human_summary_required") is True and gate.get("human_summary_language") == "current-user-language", "human summary rendering contract changed")
    summary_source = gate.get("human_summary_source")
    require_plan(isinstance(summary_source, dict), "human_summary_source must be an object")
    require_plan(set(HUMAN_SUMMARY_FIELDS) <= set(summary_source), "human_summary_source is missing required review facts")
    for field in HUMAN_SUMMARY_FIELDS:
        require_plan(isinstance(summary_source.get(field), list) and all(isinstance(item, str) and item.strip() for item in summary_source[field]), f"human summary field {field} must contain reviewable facts")
    require_plan(summary_source.get("render_language") == "current-user-language" and summary_source.get("render_required") is True, "human summary must be rendered in the current user language")

    stages = payload.get("stages")
    expected_stage_names = ["discover", "design", "human_review", "controlled_change", "verify", "handoff_or_archive"]
    expected_mutations = [False, False, False, True, False, False]
    require_plan(isinstance(stages, list) and len(stages) == 6, "exactly six lifecycle stages are required")
    for index, (stage, name, mutation) in enumerate(zip(stages, expected_stage_names, expected_mutations)):
        require_plan(isinstance(stage, dict) and stage.get("name") == name, f"stage {index} must be {name}")
        require_plan(isinstance(stage.get("status"), str) and bool(stage["status"].strip()), f"stage {name} needs a status")
        require_plan(stage.get("mutation") is mutation, f"stage {name} has the wrong mutation boundary")

    actions = payload.get("component_actions")
    expected_owners = {
        "project-agent-generator-skill": "project-agent-generator-skill",
        "research-workspace-governance": "research-workspace-governance",
        "neat-freak": None,
        "experiment-protocol-audit": None,
    }
    require_plan(isinstance(actions, list) and len(actions) == len(expected_owners), "component_actions must preserve the unique responsibility table")
    seen_components: set[str] = set()
    for action in actions:
        require_plan(isinstance(action, dict) and {"component", "action", "mutation_owner"} <= set(action), "component action is incomplete")
        component = action.get("component")
        require_plan(component in expected_owners and component not in seen_components, "component action owner is missing or duplicated")
        seen_components.add(component)
        require_plan(action.get("mutation_owner") == expected_owners[component], f"component {component} has an ownership conflict")
        require_plan(isinstance(action.get("action"), str) and bool(action["action"].strip()), f"component {component} needs an action")
        expected_action = {
            "project-agent-generator-skill": "preserve" if payload["context_action"] == "preserve_and_audit" else "create_after_review",
            "research-workspace-governance": "resolve_or_initialize_governance_records",
            "neat-freak": "audit_agent_knowledge_and_loading",
            "experiment-protocol-audit": (
                "validate_domain_protocol_independently"
                if bindings["domain_validator"]["available"]
                else "handoff_domain_validation"
            ),
        }[component]
        require_plan(action["action"] == expected_action, f"component {component} has an unsupported action")
    snapshots = payload.get("snapshots")
    require_plan(isinstance(snapshots, dict) and {"project_agent_generator", "research_workspace_inventory"} <= set(snapshots), "component snapshots are incomplete")
    generator_snapshot = snapshots["project_agent_generator"]
    inventory_snapshot = snapshots["research_workspace_inventory"]
    require_plan(isinstance(generator_snapshot, dict) and generator_snapshot.get("schema_version") == GENERATOR_SCHEMA, "generator snapshot is invalid")
    require_plan(isinstance(inventory_snapshot, dict) and inventory_snapshot.get("schema_version") == INVENTORY_SCHEMA, "inventory snapshot is invalid")
    require_plan(inventory_snapshot.get("workspace_fingerprint_sha256") == payload["workspace_fingerprint_sha256"], "inventory snapshot fingerprint conflicts with the plan")
    for section_name in (
        "governance_layout", "project_contract", "relocation_maps", "governance_state",
    ):
        require_plan(inventory_snapshot.get(section_name) == payload[section_name], f"inventory snapshot {section_name} conflicts with the plan")
    invariants = payload.get("invariants")
    require_plan(isinstance(invariants, list) and bool(invariants) and all(isinstance(item, str) and item.strip() for item in invariants), "invariants must be a non-empty string array")


def validate_component_binding(
    plan: dict[str, Any],
    name: str,
    current: Path,
) -> None:
    binding = plan["component_bindings"][name]
    current_path = current.resolve(strict=True)
    if os.path.normcase(str(current_path)) != os.path.normcase(str(binding["path"])):
        raise ValueError(f"component {name} differs from the reviewed plan; rerun plan")
    if sha256_file(current_path).casefold() != str(binding["sha256"]).casefold():
        raise ValueError(f"component {name} changed since the reviewed plan; rerun plan")


def load_and_validate_plan(path: Path, project: Path, confirmed_hash: str) -> dict[str, Any]:
    requested = path.expanduser().absolute()
    if first_link_component(requested) is not None or is_link_like(requested):
        raise ValueError("reviewed pipeline plan must be a regular non-linked file")
    path = requested.resolve(strict=True)
    if is_relative_to(path, project):
        raise ValueError("reviewed pipeline plan must be outside the target project")
    if not path.is_file() or path.stat().st_size > MAX_PLAN_BYTES:
        raise ValueError("reviewed pipeline plan must be a regular JSON file no larger than 5 MiB")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("unsupported pipeline plan")
    if payload.get("schema_version") in LEGACY_PIPELINE_SCHEMAS:
        raise ValueError("legacy pipeline plan is recognized but cannot authorize mutation; rerun plan to create v4")
    if payload.get("schema_version") != PIPELINE_PLAN_SCHEMA:
        raise ValueError("unsupported pipeline plan")
    validate_plan_structure(payload)
    embedded_hash = str(payload.get("plan_sha256", "")).casefold()
    calculated_hash = canonical_hash(payload).casefold()
    if embedded_hash != calculated_hash:
        raise ValueError("pipeline plan content does not match its embedded hash")
    if confirmed_hash.casefold() != embedded_hash:
        raise ValueError("confirmation hash does not match the reviewed pipeline plan")
    if os.path.normcase(str(Path(payload["project_root"]).resolve())) != os.path.normcase(str(project)):
        raise ValueError("pipeline plan targets a different project root")
    return payload


def command_plan(args: argparse.Namespace, components: dict[str, Path | None]) -> int:
    project = resolve_project_root(args.project)
    profile = "minimal" if args.profile == "lightweight" else args.profile
    plan = build_plan(
        project,
        profile,
        components,
        policy_topology=args.policy_topology,
        comparison_records=args.comparison_records,
        domain_validation_record=args.domain_validation_record,
        domain_validation_requirement=args.domain_validation,
        domain_validation_owner=args.domain_validation_owner,
    )
    if args.output:
        output = Path(args.output).expanduser().resolve(strict=False)
        if is_relative_to(output, project):
            raise ValueError("pipeline plan output must be outside the target project")
        write_json_new(output, plan, compact=args.compact)
        emit(result_document(
            "plan_written",
            path=str(output),
            plan_sha256=plan["plan_sha256"],
            pipeline_id=plan["pipeline_id"],
        ), compact=args.compact)
    else:
        emit(plan, compact=args.compact)
    return 0


def command_bootstrap(args: argparse.Namespace, components: dict[str, Path | None]) -> int:
    project = resolve_project_root(args.project)
    context_bundles = existing_context_bundles(project)
    agents_dir = project / ".agents"
    if context_bundles:
        emit(result_document(
            "existing_context_preserved",
            project_root=str(project),
            context_locations=[path.name for path in context_bundles],
            maintenance_owner="neat-freak",
            message=(
                "Initial Agent context already exists. Use Neat-Freak for reviewed "
                "project-information maintenance."
            ),
        ), compact=args.compact)
        return 0 if not args.apply else 1

    generator_path = components["generator"]
    assert isinstance(generator_path, Path)
    if not args.apply:
        process = run_process([
            sys.executable,
            "-B",
            "-X",
            "utf8",
            str(generator_path),
            str(project),
            "--dry-run",
            "--json",
        ])
        preview = parse_component_json(process, "project-agent generator dry-run")
        emit(result_document(
            "context_preview",
            project_root=str(project),
            generator_preview=preview,
        ), compact=args.compact)
        return 0

    if not args.plan or not args.confirm_plan_sha256:
        raise ValueError("--apply requires --plan and --confirm-plan-sha256")
    plan = load_and_validate_plan(
        Path(args.plan),
        project,
        args.confirm_plan_sha256,
    )
    governance_layout = plan.get("governance_layout", {})
    project_contract = plan.get("project_contract", {})
    relocation_maps = plan.get("relocation_maps", {})
    governance_state = plan.get("governance_state", {})
    comparison_contracts = plan.get("comparison_contracts", {})
    if isinstance(governance_layout, dict) and governance_layout.get("status") in {"ambiguous", "unsafe"}:
        raise ValueError("reviewed plan contains a blocking governance-location finding")
    if isinstance(project_contract, dict) and project_contract.get("status") == "invalid":
        raise ValueError("reviewed plan contains an invalid project contract")
    if isinstance(relocation_maps, dict) and relocation_maps.get("status") == "invalid":
        raise ValueError("reviewed plan contains an invalid relocation map")
    if isinstance(governance_state, dict) and governance_state.get("status") == "invalid":
        raise ValueError("reviewed plan contains an invalid governance state")
    if isinstance(comparison_contracts, dict) and comparison_contracts.get("status") == "invalid":
        raise ValueError("reviewed plan contains an invalid comparison contract")
    review_gate = plan.get("review_gate_inputs", {})
    if not isinstance(review_gate, dict) or review_gate.get("result") == "fail":
        raise ValueError("reviewed plan contains unresolved blocking findings")
    if plan.get("context_action") != "create_after_framework":
        raise ValueError("reviewed plan does not authorize creating a missing .agents bundle")
    inventory_path = components["inventory"]
    assert isinstance(inventory_path, Path)
    validate_component_binding(plan, "generator", generator_path)
    validate_component_binding(plan, "inventory", inventory_path)
    current_inventory = inspect_workspace(project, inventory_path)
    validate_complete_inventory(current_inventory)
    if current_inventory["workspace_fingerprint_sha256"] != plan["workspace_fingerprint_sha256"]:
        raise ValueError("project changed since the reviewed plan; rerun plan")
    for section_name in (
        "governance_layout", "project_contract", "relocation_maps", "governance_state",
    ):
        if current_inventory.get(section_name) != plan.get(section_name):
            raise ValueError(f"project {section_name} changed since the reviewed plan; rerun plan")

    process = run_process([
        sys.executable,
        "-B",
        "-X",
        "utf8",
        str(generator_path),
        str(project),
    ])
    missing = [name for name in REQUIRED_AGENT_FILES if not (agents_dir / name).is_file()]
    if missing:
        raise ComponentError(f"agent context creation incomplete: {missing}")
    emit(result_document(
        "context_created",
        project_root=str(project),
        initialization_status="complete",
        maintenance_owner="neat-freak",
        plan_sha256=plan["plan_sha256"],
        generator_output=process.stdout.strip().splitlines(),
    ), compact=args.compact)
    return 0


def run_knowledge_audit(
    project: Path,
    script: Path,
    mode: str,
    memory_directory: str,
    policy_topology: str | None = None,
) -> dict[str, Any]:
    command = [
        sys.executable,
        "-B",
        "-X",
        "utf8",
        str(script),
        "--compact",
        "--memory-dir",
        memory_directory,
        str(project),
        mode,
    ]
    if mode == "bootstrap-audit" and policy_topology:
        command.extend(["--policy-topology", policy_topology])
    process = run_process(command, accepted_codes={0, 1, 2})
    payload = parse_component_json(process, f"knowledge {mode}")
    return {"exit_code": process.returncode, "result": payload}


def command_verify(args: argparse.Namespace, components: dict[str, Path | None]) -> int:
    project = resolve_project_root(args.project)
    generator_path = components["generator"]
    inventory_path = components["inventory"]
    assert isinstance(generator_path, Path)
    assert isinstance(inventory_path, Path)
    generator = inspect_generator(project, generator_path)
    inventory = inspect_workspace(project, inventory_path)
    loading_handoff = policy_topology_handoff(project, args.policy_topology)
    comparison = run_comparison_validation(
        project,
        components["comparison_validator"],  # type: ignore[arg-type]
        args.comparison_records,
    )
    domain_handoff = build_domain_validation_handoff(
        project,
        components,
        args.domain_validation_record,
        args.domain_validation,
        args.domain_validation_owner,
    )
    comparison_code = int(comparison["summary"]["exit_code"])
    governance_layout = inventory.get("governance_layout", {})
    project_contract = inventory.get("project_contract", {})
    relocation_maps = inventory.get("relocation_maps", {})
    governance_state = inventory.get("governance_state", {})
    governance_status = governance_layout.get("status") if isinstance(governance_layout, dict) else None
    contract_status = project_contract.get("status") if isinstance(project_contract, dict) else None
    state_status = governance_state.get("status") if isinstance(governance_state, dict) else None
    relocation_status = relocation_maps.get("status") if isinstance(relocation_maps, dict) else None
    if governance_status in {"ambiguous", "unsafe"} or contract_status == "invalid" or relocation_status == "invalid" or state_status == "invalid":
        governance_code = 2
    elif governance_status == "absent":
        governance_code = 1
    else:
        governance_code = 0
    context_bundles = existing_context_bundles(project)
    context_ambiguity = len(context_bundles) > 1
    agents_dir = context_bundles[0] if context_bundles else project / ".agents"
    context_link_detected = bool(context_bundles and is_link_like(agents_dir))
    missing = [
        f"{agents_dir.name}/{name}"
        for name in REQUIRED_AGENT_FILES
        if context_link_detected or not (agents_dir / name).is_file()
    ]
    knowledge_results: dict[str, Any] = {"status": "unavailable"}
    worst_code = 0
    knowledge_script = components["knowledge"]
    if context_ambiguity:
        knowledge_results = {"status": "skipped_context_ambiguity"}
    elif isinstance(knowledge_script, Path) and not context_link_detected:
        memory_directory = f"{agents_dir.name}/memory"
        audit: dict[str, Any] = {"status": "skipped_missing_context"}
        if (agents_dir / "memory").is_dir():
            audit = run_knowledge_audit(project, knowledge_script, "audit", memory_directory)
        neat_topology = loading_handoff.get("manifest_path")
        bootstrap = run_knowledge_audit(
            project,
            knowledge_script,
            "bootstrap-audit",
            memory_directory,
            neat_topology,
        )
        knowledge_results = {
            "status": "executed",
            "audit": audit,
            "bootstrap_audit": bootstrap,
            "policy_topology_audit": (
                "executed" if neat_topology else (
                    "not_requested"
                )
            ),
        }
        worst_code = int(bootstrap["exit_code"])
        if "exit_code" in audit:
            worst_code = max(int(audit["exit_code"]), worst_code)

    scan = inventory.get("scan", {})
    loading_code = worst_code
    if args.policy_topology and knowledge_results["status"] != "executed":
        loading_code = 2
    if missing or loading_code == 2 or context_link_detected or comparison_code == 2 or governance_code == 2:
        onboarding_state = "blocked"
        exit_code = 2
    elif context_ambiguity:
        onboarding_state = "conditional"
        exit_code = 1
    elif scan.get("scan_truncated") or int(scan.get("unreadable_count", 0)) > 0:
        onboarding_state = "conditional"
        exit_code = 1
    elif knowledge_results["status"] == "unavailable" or loading_code == 1 or comparison_code == 1 or governance_code == 1:
        onboarding_state = "conditional"
        exit_code = 1
    else:
        onboarding_state = "ready"
        exit_code = 0
    blockers, non_blockers = findings_from(
        governance_layout,
        project_contract,
        relocation_maps,
        governance_state,
        comparison,
        domain_handoff,
    )
    if missing:
        blockers.append({"code": "missing-agent-files", "severity": "blocker", "paths": missing})
    if context_ambiguity:
        blockers.append({"code": "context-ambiguity", "severity": "blocker", "candidate_interpretations": [path.name for path in context_bundles]})
    if args.policy_topology and knowledge_results["status"] != "executed":
        blockers.append({"code": "agent-loading-audit-not-executed", "severity": "blocker", "owner": "neat-freak"})
    gate = review_gate_inputs(
        blockers=blockers,
        non_blockers=non_blockers,
        evidence=[
            "workspace_inventory",
            "relocation_maps",
            "project_agent_inspection",
            "knowledge_and_bootstrap",
            "comparison_contracts",
            "domain_validation_handoff",
            "readiness",
        ],
        unvalidated=(
            [
                "Validation remains limited to the declared Profile, scopes, evidence fingerprints, and claim ceiling; undeclared assumptions are not validated."
            ]
            if domain_handoff["effective_state"] == "verified"
            else [
                "Scientific validity and claim support remain unvalidated; this verification only reports onboarding and governance readiness."
            ]
        ),
    )
    domain_state = str(domain_handoff["effective_state"])
    if exit_code < 2 and domain_state in {"failed", "stale", "invalid"}:
        exit_code = 1
    elif exit_code == 0 and domain_state == "not_declared" and domain_handoff["requirement"] != "optional":
        exit_code = 1
    elif exit_code == 0 and domain_state == "pending":
        exit_code = 1
    readiness = readiness_axes(
        onboarding_state=onboarding_state,
        agent_context_state=(
            "blocked"
            if missing or context_ambiguity or context_link_detected
            else "ready"
        ),
        governance_state=(
            "blocked" if governance_code == 2 else "conditional" if governance_code == 1 else "ready"
        ),
        domain_handoff=domain_handoff,
    )
    emit(result_document(
        "verification_complete",
        mode="read-only-verification",
        project_root=str(project),
        context_locations=[path.name for path in context_bundles],
        context_ambiguity=context_ambiguity,
        context_link_detected=context_link_detected,
        missing_agent_files=missing,
        project_agent_inspection=generator,
        workspace_inventory=inventory,
        agent_loading_audit_handoff=loading_handoff,
        comparison_contracts=comparison,
        domain_validation_handoff=domain_handoff,
        readiness=readiness,
        knowledge_and_bootstrap=knowledge_results,
        review_gate_inputs=gate,
        next_action=(
            "Run research-workspace-governance adversarial review against the approved architecture plan."
            if onboarding_state != "blocked"
            else "Resolve blocking context or audit failures before continuing."
        ),
    ), compact=args.compact)
    return exit_code


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-build-root",
        help="Override the project-build Skill directory containing Generator and Governance",
    )
    parser.add_argument(
        "--reusable-core-root",
        help="Override the reusable-core Skill directory containing Neat-Freak",
    )
    parser.add_argument(
        "--core-utils-root",
        help="Legacy override for layouts where every component shares one sibling directory",
    )
    parser.add_argument("--generator-script", help="Override project-agent generator script")
    parser.add_argument("--inventory-script", help="Override governance inventory script")
    parser.add_argument("--knowledge-script", help="Override optional neat-freak script")
    parser.add_argument(
        "--comparison-validator-script",
        "--equivalence-validator-script",
        dest="comparison_validator_script",
        help="Override optional domain-neutral comparison validator script",
    )
    parser.add_argument(
        "--domain-validator-script",
        help="Override optional independent experiment-protocol auditor script",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan = subparsers.add_parser("plan", help="Create a read-only pipeline plan")
    plan.add_argument("project")
    plan.add_argument(
        "--profile",
        choices=("minimal", "lightweight", "collaborative", "controlled"),
        default="minimal",
    )
    plan.add_argument("--output", help="Optional new plan file outside the project")
    plan.add_argument(
        "--policy-topology",
        help="Project-contained Agent loading manifest to hand off to Neat-Freak; Pipeline does not parse it",
    )
    plan.add_argument(
        "--comparison-records",
        "--equivalence-records",
        dest="comparison_records",
        help="Project-contained domain-reviewed comparison JSON",
    )
    plan.add_argument(
        "--domain-validation-record",
        help="Project-contained experiment-protocol-audit result to bind as untrusted data",
    )
    plan.add_argument(
        "--domain-validation",
        choices=("required", "optional", "not-applicable", "review-required"),
        default="review-required",
        help="Whether domain validation is required for later experiment execution or claim support",
    )
    plan.add_argument(
        "--domain-validation-owner",
        help="Named human owner required for a record-free not-applicable decision",
    )
    plan.add_argument("--compact", action="store_true")

    bootstrap = subparsers.add_parser(
        "bootstrap-agents",
        help="Preview or explicitly create a missing default .agents bundle",
    )
    bootstrap.add_argument("project")
    bootstrap.add_argument("--apply", action="store_true")
    bootstrap.add_argument("--plan")
    bootstrap.add_argument("--confirm-plan-sha256")
    bootstrap.add_argument("--compact", action="store_true")

    verify = subparsers.add_parser("verify", help="Verify the integrated project without writing")
    verify.add_argument("project")
    verify.add_argument(
        "--policy-topology",
        help="Project-contained Agent loading manifest delegated to Neat-Freak for audit",
    )
    verify.add_argument(
        "--comparison-records",
        "--equivalence-records",
        dest="comparison_records",
        help="Project-contained domain-reviewed comparison JSON",
    )
    verify.add_argument(
        "--domain-validation-record",
        help="Project-contained experiment-protocol-audit result to bind as untrusted data",
    )
    verify.add_argument(
        "--domain-validation",
        choices=("required", "optional", "not-applicable", "review-required"),
        default="review-required",
        help="Whether domain validation is required for later experiment execution or claim support",
    )
    verify.add_argument(
        "--domain-validation-owner",
        help="Named human owner required for a record-free not-applicable decision",
    )
    verify.add_argument("--compact", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        components = resolve_components(args)
        if args.command == "plan":
            return command_plan(args, components)
        if args.command == "bootstrap-agents":
            return command_bootstrap(args, components)
        if args.command == "verify":
            return command_verify(args, components)
        raise ValueError(f"unsupported command: {args.command}")
    except (ComponentError, FileExistsError, OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps(result_document("error", error=str(exc)), ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
