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
    for label, path in (("generator", generator), ("inventory", inventory)):
        if not path.is_file():
            raise ComponentError(f"{label} interface not found: {path}")
    return {
        "core_root": core_root,
        "generator": generator,
        "inventory": inventory,
        "knowledge": knowledge if knowledge.is_file() else None,
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


def build_plan(project: Path, profile: str, components: dict[str, Path | None]) -> dict[str, Any]:
    generator = inspect_generator(project, components["generator"])  # type: ignore[arg-type]
    inventory = inspect_workspace(project, components["inventory"])  # type: ignore[arg-type]
    validate_complete_inventory(inventory)
    roles = inventory.get("role_candidates", {})
    role_gaps = [role for role in REQUIRED_RESEARCH_ROLES if not roles.get(role)]
    context_bundles = existing_context_bundles(project)
    context_exists = bool(context_bundles)
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
        },
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
    plan = build_plan(project, args.profile, components)
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
) -> dict[str, Any]:
    process = run_process(
        [
            sys.executable,
            "-X",
            "utf8",
            str(script),
            "--compact",
            "--memory-dir",
            memory_directory,
            str(project),
            mode,
        ],
        accepted_codes={0, 1, 2},
    )
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
    elif (
        isinstance(knowledge_script, Path)
        and agents_dir.is_dir()
        and not context_link_detected
    ):
        memory_directory = f"{agents_dir.name}/memory"
        audit = run_knowledge_audit(project, knowledge_script, "audit", memory_directory)
        bootstrap = run_knowledge_audit(
            project,
            knowledge_script,
            "bootstrap-audit",
            memory_directory,
        )
        knowledge_results = {"status": "executed", "audit": audit, "bootstrap_audit": bootstrap}
        worst_code = max(int(audit["exit_code"]), int(bootstrap["exit_code"]))

    scan = inventory.get("scan", {})
    if missing or worst_code == 2 or context_link_detected:
        status = "fail"
        exit_code = 2
    elif context_ambiguity:
        status = "conditional"
        exit_code = 1
    elif scan.get("scan_truncated") or int(scan.get("unreadable_count", 0)) > 0:
        status = "conditional"
        exit_code = 1
    elif knowledge_results["status"] == "unavailable" or worst_code == 1:
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
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan = subparsers.add_parser("plan", help="Create a read-only pipeline plan")
    plan.add_argument("project")
    plan.add_argument(
        "--profile",
        choices=("lightweight", "collaborative", "controlled"),
        default="collaborative",
    )
    plan.add_argument("--output", help="Optional new plan file outside the project")
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
