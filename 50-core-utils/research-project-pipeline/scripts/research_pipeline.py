#!/usr/bin/env python3
"""Plan, create missing agent context, or verify a research project pipeline."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any


PIPELINE_SCHEMA = "research-project-pipeline/v1"
GENERATOR_SCHEMA = "project-agent-generator/v1"
INVENTORY_SCHEMA = "research-workspace-inventory/v1"
POLICY_TOPOLOGY_SCHEMA = "research-policy-topology/v1"
EQUIVALENCE_SCHEMA = "research-equivalence-record/v1"
AGENT_BUNDLE_NAMES = (".agents", ".agent")
POLICY_BINDING_TYPES = {
    "explicit_reference",
    "verified_loader",
    "owner_approved_isolation",
}
POLICY_SCAN_SKIP = {".git", ".hg", ".svn", "__pycache__", "node_modules"}
MAX_POLICY_SCAN_DIRECTORIES = 50_000
MAX_POLICY_TEXT_BYTES = 1024 * 1024
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
REQUIRED_RESEARCH_ROLES = (
    "governance",
    "protocols",
    "source_records",
    "derived_data",
    "methods",
    "experiments_analyses",
    "run_evidence",
    "reports",
    "deliverables",
    "archive",
    "temporary",
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


def resolve_components(args: argparse.Namespace) -> dict[str, Path | None]:
    default_root = Path(__file__).resolve().parents[2]
    core_root = (
        Path(args.core_utils_root).expanduser().resolve()
        if args.core_utils_root
        else default_root
    )
    generator = (
        Path(args.generator_script).expanduser().resolve()
        if args.generator_script
        else core_root / "project-agent-generator-skill" / "scripts" / "generate_project_agents.py"
    )
    inventory = (
        Path(args.inventory_script).expanduser().resolve()
        if args.inventory_script
        else core_root / "research-workspace-governance" / "scripts" / "inventory_workspace.py"
    )
    knowledge = (
        Path(args.knowledge_script).expanduser().resolve()
        if args.knowledge_script
        else core_root / "neat-freak" / "scripts" / "manage_project_knowledge.py"
    )
    equivalence_validator = (
        Path(args.equivalence_validator_script).expanduser().resolve()
        if args.equivalence_validator_script
        else core_root
        / "research-workspace-governance"
        / "scripts"
        / "validate_equivalence_records.py"
    )
    for label, path in (("generator", generator), ("inventory", inventory)):
        if not path.is_file():
            raise ComponentError(f"{label} interface not found: {path}")
    return {
        "core_root": core_root,
        "generator": generator,
        "inventory": inventory,
        "knowledge": knowledge if knowledge.is_file() else None,
        "equivalence_validator": (
            equivalence_validator if equivalence_validator.is_file() else None
        ),
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
        "-X",
        "utf8",
        str(inventory),
        str(project),
        "--compact",
    ])
    payload = parse_component_json(process, "research workspace inventory")
    if payload.get("schema_version") != INVENTORY_SCHEMA or payload.get("status") != "inspected":
        raise ComponentError("unsupported or unsuccessful workspace inventory")
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
    scan = inventory.get("scan", {})
    if scan.get("scan_truncated"):
        raise ComponentError("workspace inventory is truncated")
    if int(scan.get("unreadable_count", 0)) > 0:
        raise ComponentError("workspace inventory contains unreadable paths")


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


def read_json_bounded(path: Path, label: str) -> Any:
    if path.stat().st_size > 5 * 1024 * 1024:
        raise ValueError(f"{label} exceeds 5 MiB")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} is not valid JSON: {exc}") from exc


def policy_finding(
    code: str,
    message: str,
    *,
    severity: str = "error",
    path: str | None = None,
    policy_id: str | None = None,
    execution_root_id: str | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {"code": code, "message": message, "severity": severity}
    if path is not None:
        result["path"] = path
    if policy_id is not None:
        result["policy_id"] = policy_id
    if execution_root_id is not None:
        result["execution_root_id"] = execution_root_id
    return result


def discover_execution_roots(project: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    discovered: dict[str, dict[str, Any]] = {
        ".": {"id": "project-root", "path": ".", "context_bundles": []}
    }
    findings: list[dict[str, Any]] = []
    visited = 0
    for current_raw, directory_names, _file_names in os.walk(project, topdown=True, followlinks=False):
        current = Path(current_raw)
        visited += 1
        if visited > MAX_POLICY_SCAN_DIRECTORIES:
            findings.append(policy_finding(
                "execution-root-scan-truncated",
                f"execution-root discovery exceeded {MAX_POLICY_SCAN_DIRECTORIES} directories",
                severity="error",
            ))
            break
        safe_directories: list[str] = []
        for name in directory_names:
            child = current / name
            if name in POLICY_SCAN_SKIP or name in AGENT_BUNDLE_NAMES or is_link_like(child):
                continue
            safe_directories.append(name)
        directory_names[:] = safe_directories

        bundles = [
            name
            for name in AGENT_BUNDLE_NAMES
            if (current / name / "AGENTS.md").is_file()
            and linked_component_below(project, current / name / "AGENTS.md") is None
        ]
        if not bundles:
            continue
        relative = current.relative_to(project).as_posix() or "."
        entry = discovered.setdefault(
            relative,
            {
                "id": "project-root" if relative == "." else f"execution:{relative}",
                "path": relative,
                "context_bundles": [],
            },
        )
        entry["context_bundles"] = bundles
        if len(bundles) > 1:
            findings.append(policy_finding(
                "context-ambiguity",
                "both .agents and .agent contain AGENTS.md",
                severity="finding",
                path=relative,
                execution_root_id=str(entry["id"]),
            ))
    return sorted(discovered.values(), key=lambda item: str(item["path"])), findings


def safe_manifest_path(project: Path, raw: Any, label: str, findings: list[dict[str, Any]]) -> Path | None:
    if not isinstance(raw, str) or not raw:
        findings.append(policy_finding("invalid-policy-path", f"{label} must be a non-empty project-relative path"))
        return None
    relative = Path(raw)
    if relative.is_absolute() or ".." in relative.parts:
        findings.append(policy_finding("policy-path-outside-project", f"{label} must be project-contained: {raw}", path=raw))
        return None
    unresolved = (project / relative).absolute()
    if linked_component_below(project, unresolved) is not None:
        findings.append(policy_finding("linked-policy-path", f"{label} traverses a link or junction: {raw}", path=raw))
        return None
    resolved = unresolved.resolve(strict=False)
    if not is_relative_to(resolved, project):
        findings.append(policy_finding("policy-path-outside-project", f"{label} escapes the project: {raw}", path=raw))
        return None
    if not resolved.is_file():
        findings.append(policy_finding("broken-policy-reference", f"{label} does not exist: {raw}", path=raw))
        return None
    return resolved


def analyze_policy_topology(project: Path, manifest_arg: str | None) -> dict[str, Any]:
    execution_roots, findings = discover_execution_roots(project)
    if not manifest_arg:
        if len(execution_roots) > 1:
            findings.append(policy_finding(
                "policy-declaration-missing",
                "nested execution roots were discovered but no mandatory-policy topology was declared",
                severity="finding",
            ))
        exit_code = 1 if findings else 0
        return {
            "schema_version": POLICY_TOPOLOGY_SCHEMA,
            "status": "conditional" if exit_code else "undeclared",
            "manifest_path": None,
            "policies": [],
            "execution_roots": execution_roots,
            "bindings": [],
            "findings": findings,
            "summary": {"exit_code": exit_code, "policy_count": 0, "execution_root_count": len(execution_roots), "binding_count": 0, "finding_count": len(findings)},
        }

    manifest_path = resolve_project_input_file(project, manifest_arg, "policy topology")
    document = read_json_bounded(manifest_path, "policy topology")
    if not isinstance(document, dict):
        document = {}
        findings.append(policy_finding("invalid-policy-topology", "policy topology must be a JSON object"))
    if document.get("schema_version") != POLICY_TOPOLOGY_SCHEMA:
        findings.append(policy_finding("unsupported-policy-topology-schema", f"schema_version must be {POLICY_TOPOLOGY_SCHEMA}"))

    declared_roots = document.get("execution_roots", [])
    if not isinstance(declared_roots, list):
        findings.append(policy_finding("invalid-execution-roots", "execution_roots must be an array"))
        declared_roots = []
    roots_by_path = {str(item["path"]): item for item in execution_roots}
    root_ids: set[str] = set()
    declared_paths: set[str] = set()
    for raw_root in declared_roots:
        if not isinstance(raw_root, dict) or not isinstance(raw_root.get("id"), str) or not raw_root.get("id"):
            findings.append(policy_finding("invalid-execution-root", "each declared execution root requires a non-empty id and path"))
            continue
        root_id = raw_root["id"]
        raw_path = raw_root.get("path")
        if not isinstance(raw_path, str) or not raw_path:
            findings.append(policy_finding("invalid-execution-root", f"execution root {root_id} requires a path", execution_root_id=root_id))
            continue
        rel = Path(raw_path)
        if rel.is_absolute() or ".." in rel.parts:
            findings.append(policy_finding("execution-root-outside-project", f"execution root path must be project-contained: {raw_path}", execution_root_id=root_id))
            continue
        root_path = (project / rel).resolve(strict=False)
        if not is_relative_to(root_path, project) or linked_component_below(project, (project / rel).absolute()) is not None:
            findings.append(policy_finding("linked-or-outside-execution-root", f"unsafe execution root: {raw_path}", execution_root_id=root_id))
            continue
        normalized = root_path.relative_to(project).as_posix() or "."
        if not root_path.is_dir():
            findings.append(policy_finding("missing-execution-root", f"declared execution root does not exist: {normalized}", execution_root_id=root_id))
        if normalized in declared_paths:
            findings.append(policy_finding("duplicate-execution-root-path", f"duplicate execution root path: {normalized}", execution_root_id=root_id))
            continue
        declared_paths.add(normalized)
        if root_id in root_ids:
            findings.append(policy_finding("duplicate-execution-root-id", f"duplicate execution root id: {root_id}", execution_root_id=root_id))
            continue
        root_ids.add(root_id)
        entry = roots_by_path.get(normalized)
        if entry is None:
            entry = {"id": root_id, "path": normalized, "context_bundles": []}
            roots_by_path[normalized] = entry
            findings.append(policy_finding("declared-execution-root-not-detected", "declared root has no .agents/AGENTS.md or .agent/AGENTS.md", severity="finding", path=normalized, execution_root_id=root_id))
        else:
            entry["id"] = root_id
    execution_roots = sorted(roots_by_path.values(), key=lambda item: str(item["path"]))
    output_ids = [str(item["id"]) for item in execution_roots]
    for duplicate in sorted({item for item in output_ids if output_ids.count(item) > 1}):
        findings.append(policy_finding("duplicate-execution-root-id", f"duplicate execution root id after discovery merge: {duplicate}", execution_root_id=duplicate))
    for entry in execution_roots:
        root_ids.add(str(entry["id"]))

    raw_policies = document.get("policies", [])
    if not isinstance(raw_policies, list) or not raw_policies:
        findings.append(policy_finding("invalid-policies", "policies must be a non-empty array when a topology is declared"))
        raw_policies = []
    policies: list[dict[str, Any]] = []
    policies_by_id: dict[str, dict[str, Any]] = {}
    policy_paths: dict[str, Path] = {}
    for raw_policy in raw_policies:
        if not isinstance(raw_policy, dict) or not isinstance(raw_policy.get("id"), str) or not raw_policy.get("id"):
            findings.append(policy_finding("invalid-policy", "each policy requires a non-empty id"))
            continue
        policy_id = raw_policy["id"]
        if policy_id in policies_by_id:
            findings.append(policy_finding("duplicate-policy-id", f"duplicate policy id: {policy_id}", policy_id=policy_id))
            continue
        policy_path = safe_manifest_path(project, raw_policy.get("path"), f"policy {policy_id}", findings)
        expected_hash = raw_policy.get("sha256")
        applies_to = raw_policy.get("applies_to", ["*"])
        known_copies = raw_policy.get("known_copies", [])
        if not isinstance(raw_policy.get("mandatory"), bool):
            findings.append(policy_finding("invalid-policy-mandatory", "mandatory must be an explicit boolean", policy_id=policy_id))
        if not isinstance(applies_to, list) or not applies_to or any(not isinstance(item, str) for item in applies_to):
            findings.append(policy_finding("invalid-policy-scope", "applies_to must be a non-empty array of execution-root ids or *", policy_id=policy_id))
            applies_to = []
        unknown_roots = set(applies_to) - root_ids - {"*"}
        if unknown_roots:
            findings.append(policy_finding("unknown-policy-scope-root", "unknown execution roots: " + ", ".join(sorted(unknown_roots)), policy_id=policy_id))
        if len(applies_to) != len(set(applies_to)):
            findings.append(policy_finding("duplicate-policy-scope-root", "applies_to contains duplicate execution-root ids", policy_id=policy_id))
        if not isinstance(known_copies, list) or any(not isinstance(item, str) or not item for item in known_copies):
            findings.append(policy_finding("invalid-known-policy-copies", "known_copies must be an array of project-relative paths", policy_id=policy_id))
            known_copies = []
        elif len(known_copies) != len(set(known_copies)):
            findings.append(policy_finding("duplicate-known-policy-copy", "known_copies contains duplicate paths", policy_id=policy_id))
        normalized = {
            "id": policy_id,
            "path": raw_policy.get("path"),
            "sha256": expected_hash,
            "mandatory": raw_policy.get("mandatory") is True,
            "applies_to": applies_to,
            "known_copies": known_copies,
        }
        if policy_path:
            actual_hash = sha256_file(policy_path)
            normalized["actual_sha256"] = actual_hash
            policy_paths[policy_id] = policy_path
            if not is_sha256(expected_hash):
                findings.append(policy_finding("invalid-policy-hash", "policy sha256 must contain 64 hexadecimal characters", policy_id=policy_id, path=str(raw_policy.get("path"))))
            elif actual_hash.casefold() != expected_hash.casefold():
                findings.append(policy_finding("policy-hash-mismatch", "policy file does not match its declared SHA-256", policy_id=policy_id, path=str(raw_policy.get("path"))))
            path_parts = {part.casefold() for part in Path(str(raw_policy.get("path"))).parts}
            if normalized["mandatory"] and "memory" in path_parts:
                findings.append(policy_finding("mandatory-policy-in-optional-memory", "mandatory policies must not exist only in optional memory", policy_id=policy_id, path=str(raw_policy.get("path"))))
        policies.append(normalized)
        policies_by_id[policy_id] = normalized

    raw_bindings = document.get("bindings")
    if not isinstance(raw_bindings, list):
        findings.append(policy_finding("invalid-policy-bindings", "bindings must be an array"))
        raw_bindings = []
    bindings: list[dict[str, Any]] = []
    binding_keys: set[tuple[str, str]] = set()
    roots_by_id = {str(item["id"]): item for item in execution_roots}
    for raw_binding in raw_bindings:
        if not isinstance(raw_binding, dict):
            findings.append(policy_finding("invalid-policy-binding", "each binding must be an object"))
            continue
        root_id = raw_binding.get("execution_root_id")
        policy_id = raw_binding.get("policy_id")
        binding_type = raw_binding.get("type")
        if root_id not in roots_by_id or policy_id not in policies_by_id or binding_type not in POLICY_BINDING_TYPES:
            findings.append(policy_finding("invalid-policy-binding", "binding must name a known execution root, policy, and binding type", policy_id=str(policy_id), execution_root_id=str(root_id)))
            continue
        key = (str(root_id), str(policy_id))
        if key in binding_keys:
            findings.append(policy_finding("duplicate-policy-binding", "duplicate root-policy binding", policy_id=str(policy_id), execution_root_id=str(root_id)))
            continue
        binding_keys.add(key)
        normalized_binding: dict[str, Any] = {
            "execution_root_id": root_id,
            "policy_id": policy_id,
            "type": binding_type,
            "status": "invalid",
        }
        root_path = project / str(roots_by_id[str(root_id)]["path"])
        policy_path = policy_paths.get(str(policy_id))
        if binding_type == "explicit_reference" and policy_path:
            canonical_reference = os.path.relpath(policy_path, root_path).replace("\\", "/")
            normalized_binding["canonical_reference"] = canonical_reference
            agents_files = [root_path / name / "AGENTS.md" for name in roots_by_id[str(root_id)].get("context_bundles", [])]
            readable = [path for path in agents_files if path.is_file() and path.stat().st_size <= MAX_POLICY_TEXT_BYTES]
            texts = [path.read_text(encoding="utf-8-sig") for path in readable]
            if not texts or not any(canonical_reference in text.replace("\\", "/") for text in texts):
                findings.append(policy_finding("mandatory-policy-unreachable", f"no execution-root AGENTS.md explicitly references {canonical_reference}", policy_id=str(policy_id), execution_root_id=str(root_id)))
            elif raw_binding.get("non_weakening") is not True:
                findings.append(policy_finding("missing-non-weakening-constraint", "explicit references must declare non_weakening=true", policy_id=str(policy_id), execution_root_id=str(root_id)))
            else:
                review = raw_binding.get("semantic_review")
                if not isinstance(review, dict) or review.get("status") != "approved" or not review.get("reviewer") or not review.get("reviewed_at"):
                    normalized_binding["status"] = "conditional"
                    findings.append(policy_finding("semantic-non-weakening-review-required", "path reachability is verified but natural-language non-weakening still requires an approved semantic review", severity="finding", policy_id=str(policy_id), execution_root_id=str(root_id)))
                else:
                    normalized_binding["status"] = "verified"
        elif binding_type == "verified_loader":
            loader = safe_manifest_path(project, raw_binding.get("loader_path"), "verified loader", findings)
            evidence = raw_binding.get("verification_evidence")
            evidence_path = safe_manifest_path(project, evidence.get("path") if isinstance(evidence, dict) else None, "loader verification evidence", findings)
            hashes_ok = True
            for checked_path, expected, code in (
                (loader, raw_binding.get("loader_sha256"), "loader-hash-mismatch"),
                (evidence_path, evidence.get("sha256") if isinstance(evidence, dict) else None, "loader-evidence-hash-mismatch"),
            ):
                if checked_path is None or not is_sha256(expected) or sha256_file(checked_path).casefold() != expected.casefold():
                    hashes_ok = False
                    findings.append(policy_finding(code, "verified loader evidence is missing or does not match its SHA-256", policy_id=str(policy_id), execution_root_id=str(root_id)))
            if not isinstance(evidence, dict) or evidence.get("result") != "pass":
                hashes_ok = False
                findings.append(policy_finding("loader-unverified", "verified_loader requires immutable passing verification evidence", policy_id=str(policy_id), execution_root_id=str(root_id)))
            elif evidence.get("covers_execution_root_id") != root_id or evidence.get("covers_policy_id") != policy_id:
                hashes_ok = False
                findings.append(policy_finding("loader-evidence-scope-mismatch", "loader verification evidence must name this execution root and policy", policy_id=str(policy_id), execution_root_id=str(root_id)))
            if hashes_ok:
                normalized_binding["status"] = "verified"
        elif binding_type == "owner_approved_isolation":
            approval = raw_binding.get("approval")
            if not isinstance(approval, dict) or not approval.get("owner") or not approval.get("approved_at") or not approval.get("rationale"):
                findings.append(policy_finding("invalid-owner-approved-isolation", "isolation requires owner, approved_at, and rationale", policy_id=str(policy_id), execution_root_id=str(root_id)))
            else:
                normalized_binding["status"] = "isolated"
                findings.append(policy_finding("owner-approved-isolation", "mandatory policy is intentionally isolated by an owner decision", severity="finding", policy_id=str(policy_id), execution_root_id=str(root_id)))
        bindings.append(normalized_binding)

    for policy in policies:
        if not policy["mandatory"]:
            continue
        applicable = execution_roots if "*" in policy["applies_to"] else [item for item in execution_roots if item["id"] in policy["applies_to"]]
        for root in applicable:
            if (str(root["id"]), str(policy["id"])) not in binding_keys:
                findings.append(policy_finding("mandatory-policy-unreachable", "no binding declares how this execution root reaches the mandatory policy", policy_id=str(policy["id"]), execution_root_id=str(root["id"])))

    for policy in policies:
        policy_path = policy_paths.get(str(policy["id"]))
        if not policy_path:
            continue
        for raw_copy in policy.get("known_copies", []):
            copy = safe_manifest_path(project, raw_copy, f"known copy of policy {policy['id']}", findings)
            if not copy or copy == policy_path:
                continue
            kind = "duplicated-policy-body" if sha256_file(copy) == sha256_file(policy_path) else "duplicated-policy-drift"
            severity = "finding" if kind == "duplicated-policy-body" else "error"
            findings.append(policy_finding(kind, "declared copy duplicates the canonical policy; use a short reference" if kind == "duplicated-policy-body" else "declared policy copy has drifted from the canonical policy", severity=severity, path=copy.relative_to(project).as_posix(), policy_id=str(policy["id"])))

    has_errors = any(item["severity"] == "error" for item in findings)
    if has_errors:
        status, exit_code = "invalid", 2
    elif findings:
        status, exit_code = "conditional", 1
    else:
        status, exit_code = "verified", 0
    return {
        "schema_version": POLICY_TOPOLOGY_SCHEMA,
        "status": status,
        "manifest_path": manifest_path.relative_to(project).as_posix(),
        "policies": policies,
        "execution_roots": execution_roots,
        "bindings": bindings,
        "findings": findings,
        "summary": {"exit_code": exit_code, "policy_count": len(policies), "execution_root_count": len(execution_roots), "binding_count": len(bindings), "finding_count": len(findings)},
    }


def run_equivalence_validation(project: Path, script: Path | None, records_arg: str | None) -> dict[str, Any]:
    if not records_arg:
        return {
            "schema_version": EQUIVALENCE_SCHEMA,
            "status": "not_declared",
            "records_path": None,
            "findings": [],
            "records": [],
            "summary": {"exit_code": 0, "record_count": 0, "verified_count": 0, "finding_count": 0},
        }
    if script is None:
        raise ComponentError("equivalence validator interface is unavailable")
    records_path = resolve_project_input_file(project, records_arg, "equivalence records")
    process = run_process(
        [sys.executable, "-X", "utf8", str(script), str(records_path), "--project-root", str(project), "--compact"],
        accepted_codes={0, 1, 2},
    )
    payload = parse_component_json(process, "equivalence validator")
    if payload.get("schema_version") != EQUIVALENCE_SCHEMA:
        raise ComponentError("unsupported equivalence-validator schema")
    if not isinstance(payload.get("summary"), dict):
        raise ComponentError("equivalence validator omitted its summary")
    payload["records_path"] = records_path.relative_to(project).as_posix()
    payload["summary"]["exit_code"] = process.returncode
    return payload


def build_plan(
    project: Path,
    profile: str,
    components: dict[str, Path | None],
    *,
    policy_topology: str | None = None,
    equivalence_records: str | None = None,
) -> dict[str, Any]:
    generator = inspect_generator(project, components["generator"])  # type: ignore[arg-type]
    inventory = inspect_workspace(project, components["inventory"])  # type: ignore[arg-type]
    validate_complete_inventory(inventory)
    roles = inventory.get("role_candidates", {})
    role_gaps = [role for role in REQUIRED_RESEARCH_ROLES if not roles.get(role)]
    context_bundles = existing_context_bundles(project)
    context_exists = bool(context_bundles)
    topology = analyze_policy_topology(project, policy_topology)
    equivalence = run_equivalence_validation(
        project,
        components["equivalence_validator"],  # type: ignore[arg-type]
        equivalence_records,
    )
    fingerprint = str(inventory["workspace_fingerprint_sha256"])
    pipeline_id = hashlib.sha256(
        f"{project}|{fingerprint}|{profile}".encode("utf-8")
    ).hexdigest()[:16]
    plan: dict[str, Any] = {
        "schema_version": PIPELINE_SCHEMA,
        "pipeline_id": pipeline_id,
        "plan_sha256": "",
        "status": "architecture_review_required",
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
            "policy_topology": topology["schema_version"],
            "equivalence_validator": equivalence["schema_version"],
        },
        "policy_topology": topology,
        "equivalence_contracts": equivalence,
        "role_gaps_for_semantic_review": role_gaps,
        "stages": [
            {"name": "discover", "status": "complete", "mutation": False},
            {"name": "architecture_design", "status": "requires_governance_review", "mutation": False},
            {"name": "approval", "status": "required", "mutation": False},
            {"name": "framework_apply", "status": "blocked_by_approval", "mutation": True},
            {"name": "post_change_rediscovery", "status": "required_after_changes", "mutation": False},
            {"name": "agent_context", "status": "preserve" if context_exists else "pending", "mutation": not context_exists},
            {"name": "knowledge_bootstrap_audit", "status": "pending", "mutation": False},
            {"name": "adversarial_verification", "status": "pending", "mutation": False},
        ],
        "snapshots": {
            "project_agent_generator": generator,
            "research_workspace_inventory": inventory,
        },
        "invariants": [
            "The plan does not authorize migration, overwrite, force, or deletion.",
            "Rerun plan after framework changes before creating agent context.",
            "Existing .agents or .agent context is preserved for standalone reviewed maintenance.",
            "Role gaps are name-based prompts for semantic review, not automatic directory creation.",
            "The metadata fingerprint detects ordinary drift; it is not a content-integrity signature or security boundary.",
            "Policy reachability is path/hash evidence; natural-language non-weakening requires semantic review.",
            "Equivalence validation checks declarations and evidence metadata, not domain science.",
        ],
    }
    plan["plan_sha256"] = canonical_hash(plan)
    return plan


def load_and_validate_plan(path: Path, project: Path, confirmed_hash: str) -> dict[str, Any]:
    path = path.expanduser().resolve()
    if is_relative_to(path, project):
        raise ValueError("reviewed pipeline plan must be outside the target project")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema_version") != PIPELINE_SCHEMA:
        raise ValueError("unsupported pipeline plan")
    embedded_hash = str(payload.get("plan_sha256", "")).casefold()
    calculated_hash = canonical_hash(payload).casefold()
    if embedded_hash != calculated_hash:
        raise ValueError("pipeline plan content does not match its embedded hash")
    if confirmed_hash.casefold() != embedded_hash:
        raise ValueError("confirmation hash does not match the reviewed pipeline plan")
    if Path(str(payload.get("project_root", ""))).resolve() != project:
        raise ValueError("pipeline plan targets a different project root")
    return payload


def command_plan(args: argparse.Namespace, components: dict[str, Path | None]) -> int:
    project = Path(args.project).expanduser().resolve()
    plan = build_plan(
        project,
        args.profile,
        components,
        policy_topology=args.policy_topology,
        equivalence_records=args.equivalence_records,
    )
    if args.output:
        output = Path(args.output).expanduser().resolve(strict=False)
        if is_relative_to(output, project):
            raise ValueError("pipeline plan output must be outside the target project")
        write_json_new(output, plan, compact=args.compact)
        emit({
            "schema_version": PIPELINE_SCHEMA,
            "status": "plan_written",
            "path": str(output),
            "plan_sha256": plan["plan_sha256"],
            "pipeline_id": plan["pipeline_id"],
        }, compact=args.compact)
    else:
        emit(plan, compact=args.compact)
    return 0


def command_bootstrap(args: argparse.Namespace, components: dict[str, Path | None]) -> int:
    project = Path(args.project).expanduser().resolve()
    if not project.is_dir():
        raise ValueError(f"project root does not exist or is not a directory: {project}")
    context_bundles = existing_context_bundles(project)
    agents_dir = project / ".agents"
    if context_bundles:
        emit({
            "schema_version": PIPELINE_SCHEMA,
            "status": "existing_context_preserved",
            "project_root": str(project),
            "context_locations": [path.name for path in context_bundles],
            "message": "Use project-agent-generator-skill independently for reviewed refresh.",
        }, compact=args.compact)
        return 0 if not args.apply else 1

    generator_path = components["generator"]
    assert isinstance(generator_path, Path)
    if not args.apply:
        process = run_process([
            sys.executable,
            "-X",
            "utf8",
            str(generator_path),
            str(project),
            "--dry-run",
            "--json",
        ])
        preview = parse_component_json(process, "project-agent generator dry-run")
        emit({
            "schema_version": PIPELINE_SCHEMA,
            "status": "context_preview",
            "project_root": str(project),
            "generator_preview": preview,
        }, compact=args.compact)
        return 0

    if not args.plan or not args.confirm_plan_sha256:
        raise ValueError("--apply requires --plan and --confirm-plan-sha256")
    plan = load_and_validate_plan(
        Path(args.plan).expanduser().resolve(),
        project,
        args.confirm_plan_sha256,
    )
    if plan.get("context_action") != "create_after_framework":
        raise ValueError("reviewed plan does not authorize creating a missing .agents bundle")
    inventory_path = components["inventory"]
    assert isinstance(inventory_path, Path)
    current_inventory = inspect_workspace(project, inventory_path)
    validate_complete_inventory(current_inventory)
    if current_inventory["workspace_fingerprint_sha256"] != plan["workspace_fingerprint_sha256"]:
        raise ValueError("project changed since the reviewed plan; rerun plan")

    process = run_process([
        sys.executable,
        "-X",
        "utf8",
        str(generator_path),
        str(project),
    ])
    missing = [name for name in REQUIRED_AGENT_FILES if not (agents_dir / name).is_file()]
    if missing:
        raise ComponentError(f"agent context creation incomplete: {missing}")
    emit({
        "schema_version": PIPELINE_SCHEMA,
        "status": "context_created",
        "project_root": str(project),
        "plan_sha256": plan["plan_sha256"],
        "generator_output": process.stdout.strip().splitlines(),
    }, compact=args.compact)
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
    project = Path(args.project).expanduser().resolve()
    generator_path = components["generator"]
    inventory_path = components["inventory"]
    assert isinstance(generator_path, Path)
    assert isinstance(inventory_path, Path)
    generator = inspect_generator(project, generator_path)
    inventory = inspect_workspace(project, inventory_path)
    topology = analyze_policy_topology(project, args.policy_topology)
    equivalence = run_equivalence_validation(
        project,
        components["equivalence_validator"],  # type: ignore[arg-type]
        args.equivalence_records,
    )
    policy_code = int(topology["summary"]["exit_code"])
    equivalence_code = int(equivalence["summary"]["exit_code"])
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
        neat_topology = (
            str(topology.get("manifest_path"))
            if args.policy_topology and policy_code != 2
            else None
        )
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
                    "skipped_invalid_pipeline_topology"
                    if args.policy_topology
                    else "not_requested"
                )
            ),
        }
        worst_code = int(bootstrap["exit_code"])
        if "exit_code" in audit:
            worst_code = max(int(audit["exit_code"]), worst_code)

    scan = inventory.get("scan", {})
    if missing or worst_code == 2 or context_link_detected or policy_code == 2 or equivalence_code == 2:
        status = "fail"
        exit_code = 2
    elif context_ambiguity:
        status = "conditional"
        exit_code = 1
    elif scan.get("scan_truncated") or int(scan.get("unreadable_count", 0)) > 0:
        status = "conditional"
        exit_code = 1
    elif knowledge_results["status"] == "unavailable" or worst_code == 1 or policy_code == 1 or equivalence_code == 1:
        status = "conditional"
        exit_code = 1
    else:
        status = "pass"
        exit_code = 0
    emit({
        "schema_version": PIPELINE_SCHEMA,
        "status": status,
        "mode": "read-only-verification",
        "project_root": str(project),
        "context_locations": [path.name for path in context_bundles],
        "context_ambiguity": context_ambiguity,
        "context_link_detected": context_link_detected,
        "missing_agent_files": missing,
        "project_agent_inspection": generator,
        "workspace_inventory": inventory,
        "policy_topology": topology,
        "equivalence_contracts": equivalence,
        "knowledge_and_bootstrap": knowledge_results,
        "next_action": (
            "Run research-workspace-governance adversarial review against the approved architecture plan."
            if status != "fail"
            else "Resolve blocking context or audit failures before continuing."
        ),
    }, compact=args.compact)
    return exit_code


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core-utils-root", help="Override the sibling Skills root")
    parser.add_argument("--generator-script", help="Override project-agent generator script")
    parser.add_argument("--inventory-script", help="Override governance inventory script")
    parser.add_argument("--knowledge-script", help="Override optional neat-freak script")
    parser.add_argument("--equivalence-validator-script", help="Override optional equivalence validator script")
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan = subparsers.add_parser("plan", help="Create a read-only pipeline plan")
    plan.add_argument("project")
    plan.add_argument(
        "--profile",
        choices=("lightweight", "collaborative", "controlled"),
        default="collaborative",
    )
    plan.add_argument("--output", help="Optional new plan file outside the project")
    plan.add_argument("--policy-topology", help="Project-contained mandatory-policy topology JSON")
    plan.add_argument("--equivalence-records", help="Project-contained typed-equivalence JSON")
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
    verify.add_argument("--policy-topology", help="Project-contained mandatory-policy topology JSON")
    verify.add_argument("--equivalence-records", help="Project-contained typed-equivalence JSON")
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
        print(json.dumps({
            "schema_version": PIPELINE_SCHEMA,
            "status": "error",
            "error": str(exc),
        }, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
