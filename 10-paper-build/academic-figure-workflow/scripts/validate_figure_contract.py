#!/usr/bin/env python3
"""Read-only validation for academic-figure-contract/v1 records."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "academic-figure-contract/v1"
POPULATION_ROLES = {"source", "display", "fit", "statistical", "sensitivity"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def load_contract(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError("figure contract root must be an object")
    return payload


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def semantic_payload(contract: dict[str, Any]) -> dict[str, Any]:
    """Return only meaning-bearing fields; visual-only changes stay outside."""
    return {
        "claim_anchors": contract.get("claim_anchors", []),
        "panels": contract.get("panels", []),
        "architecture": contract.get("architecture"),
    }


def semantic_fingerprint(contract: dict[str, Any]) -> str:
    payload = json.dumps(
        semantic_payload(contract), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _is_within(path: Path, root: Path) -> bool:
    try:
        return os.path.commonpath((str(path), str(root))) == str(root)
    except ValueError:
        return False


def _resolve_reference(
    value: str | dict[str, Any],
    root: Path,
    label: str,
    errors: list[str],
    warnings: list[str],
    *,
    required_exists: bool = False,
) -> tuple[Path | None, str | None, bool]:
    if isinstance(value, str):
        raw_path = value
        expected_hash = None
        external = False
    elif isinstance(value, dict):
        raw_path = value.get("path")
        expected_hash = value.get("sha256")
        external = value.get("external") is True
    else:
        errors.append(f"{label}: path reference must be a string or object")
        return None, None, False
    if not isinstance(raw_path, str) or not raw_path.strip():
        errors.append(f"{label}: path is missing")
        return None, expected_hash, external
    candidate = Path(raw_path)
    resolved = (candidate if candidate.is_absolute() else root / candidate).resolve(strict=False)
    if not external and not _is_within(resolved, root):
        errors.append(f"{label}: path escapes figure root: {raw_path}")
    if external and not expected_hash:
        errors.append(f"{label}: external reference requires sha256")
    if expected_hash is not None and (
        not isinstance(expected_hash, str) or not SHA256_RE.fullmatch(expected_hash.lower())
    ):
        errors.append(f"{label}: sha256 must be 64 lowercase hexadecimal characters")
    if not resolved.exists():
        message = f"{label}: referenced path does not exist: {raw_path}"
        (errors if required_exists else warnings).append(message)
    elif resolved.is_file() and isinstance(expected_hash, str) and SHA256_RE.fullmatch(expected_hash.lower()):
        actual_hash = sha256_file(resolved)
        if actual_hash != expected_hash.lower():
            errors.append(f"{label}: sha256 mismatch for {raw_path}")
    return resolved, expected_hash, external


def compare_contracts(previous: dict[str, Any], current: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    semantic_changed = semantic_fingerprint(previous) != semantic_fingerprint(current)
    revision = current.get("revision", {})
    change_class = revision.get("change_class")
    invalidated = revision.get("invalidated_outputs", [])
    if semantic_changed and change_class == "visual":
        errors.append("revision: semantic content changed but change_class is visual")
    if semantic_changed and (not isinstance(invalidated, list) or not invalidated):
        errors.append("revision: semantic change requires non-empty invalidated_outputs")
    return errors


def validate_contract(
    contract: dict[str, Any],
    contract_path: Path,
    root: Path | None = None,
    *,
    allow_template: bool = False,
    previous: dict[str, Any] | None = None,
) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    root = (root or contract_path.parent).resolve(strict=True)
    is_template = contract.get("template") is True

    if contract.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version: expected {SCHEMA_VERSION}")
    if is_template and not allow_template:
        errors.append("template contract cannot be used as a delivery contract")
    if not isinstance(contract.get("figure_id"), str) or not contract.get("figure_id", "").strip():
        errors.append("figure_id: non-empty string required")
    if contract.get("status") not in {"draft", "built", "verified"}:
        errors.append("status: expected draft, built, or verified")
    claim_anchors = contract.get("claim_anchors")
    if not isinstance(claim_anchors, list) or not claim_anchors or any(
        not isinstance(item, str) or not item.strip() for item in claim_anchors
    ):
        errors.append("claim_anchors: non-empty string list required")
        claim_anchor_set: set[str] = set()
    else:
        claim_anchor_set = set(claim_anchors)
        if len(claim_anchor_set) != len(claim_anchors):
            errors.append("claim_anchors: duplicate anchor")

    panels = contract.get("panels")
    if not isinstance(panels, list) or not panels:
        errors.append("panels: at least one panel is required")
        panels = []
    panel_ids: set[str] = set()
    element_ids: set[str] = set()
    for panel_index, panel in enumerate(panels):
        prefix = f"panels[{panel_index}]"
        if not isinstance(panel, dict):
            errors.append(f"{prefix}: panel must be an object")
            continue
        panel_id = panel.get("panel_id")
        if not isinstance(panel_id, str) or not panel_id.strip():
            errors.append(f"{prefix}.panel_id: non-empty string required")
        elif panel_id in panel_ids:
            errors.append(f"{prefix}.panel_id: duplicate {panel_id}")
        else:
            panel_ids.add(panel_id)
        if not panel.get("claim_anchor"):
            errors.append(f"{prefix}.claim_anchor: required")
        elif panel.get("claim_anchor") not in claim_anchor_set:
            errors.append(f"{prefix}.claim_anchor: not declared in claim_anchors")
        if not isinstance(panel.get("evidence_refs"), list) or not panel.get("evidence_refs") or any(
            not isinstance(item, str) or not item.strip() for item in panel.get("evidence_refs", [])
        ):
            errors.append(f"{prefix}.evidence_refs: at least one reference required")

        populations = panel.get("populations", [])
        if not isinstance(populations, list):
            errors.append(f"{prefix}.populations: list required")
            populations = []
        population_ids: set[str] = set()
        for population_index, population in enumerate(populations):
            pop_prefix = f"{prefix}.populations[{population_index}]"
            if not isinstance(population, dict):
                errors.append(f"{pop_prefix}: population must be an object")
                continue
            population_id = population.get("population_id")
            role = population.get("role")
            if not isinstance(population_id, str) or not population_id:
                errors.append(f"{pop_prefix}.population_id: required")
            elif population_id in population_ids:
                errors.append(f"{pop_prefix}.population_id: duplicate {population_id}")
            else:
                population_ids.add(population_id)
            if role not in POPULATION_ROLES:
                errors.append(f"{pop_prefix}.role: unsupported role {role!r}")
            count = population.get("count")
            if not isinstance(count, int) or isinstance(count, bool) or count < 0:
                errors.append(f"{pop_prefix}.count: non-negative integer required")
            if not isinstance(population.get("selector_ref"), str) or not population.get("selector_ref", "").strip():
                errors.append(f"{pop_prefix}.selector_ref: required")
            if not isinstance(population.get("evidence_refs"), list) or not population.get("evidence_refs") or any(
                not isinstance(item, str) or not item.strip() for item in population.get("evidence_refs", [])
            ):
                errors.append(f"{pop_prefix}.evidence_refs: at least one reference required")
            if role == "display" and not population.get("relationship_to_rendered_rows"):
                errors.append(f"{pop_prefix}.relationship_to_rendered_rows: required for display population")
            if role in {"fit", "statistical", "sensitivity"} and not population.get("relationship_to_display"):
                errors.append(f"{pop_prefix}.relationship_to_display: required for {role} population")

        uncertainty = panel.get("uncertainty")
        if not isinstance(uncertainty, dict):
            errors.append(f"{prefix}.uncertainty: object required")
        elif uncertainty.get("applicability") == "required":
            for field in ("method", "meaning", "unit_of_analysis", "prohibited_inference"):
                if not uncertainty.get(field):
                    errors.append(f"{prefix}.uncertainty.{field}: required")
        elif uncertainty.get("applicability") == "not_applicable":
            if not uncertainty.get("reason"):
                errors.append(f"{prefix}.uncertainty.reason: required when not applicable")
        else:
            errors.append(f"{prefix}.uncertainty.applicability: expected required or not_applicable")

        elements = panel.get("elements")
        if not isinstance(elements, list) or not elements:
            errors.append(f"{prefix}.elements: at least one element required")
            elements = []
        for element_index, element in enumerate(elements):
            element_prefix = f"{prefix}.elements[{element_index}]"
            if not isinstance(element, dict):
                errors.append(f"{element_prefix}: element must be an object")
                continue
            element_id = element.get("element_id")
            if not isinstance(element_id, str) or not element_id:
                errors.append(f"{element_prefix}.element_id: required")
            elif element_id in element_ids:
                errors.append(f"{element_prefix}.element_id: duplicate {element_id}")
            else:
                element_ids.add(element_id)
            if not isinstance(element.get("evidence_refs"), list) or not element.get("evidence_refs") or any(
                not isinstance(item, str) or not item.strip() for item in element.get("evidence_refs", [])
            ):
                errors.append(f"{element_prefix}.evidence_refs: at least one reference required")

    surfaces = contract.get("surfaces")
    if not isinstance(surfaces, dict):
        errors.append("surfaces: object required")
        surfaces = {}
    caption_path: Path | None = None
    if not surfaces.get("caption_md"):
        errors.append("surfaces.caption_md: required")
    elif not is_template:
        caption_path, _, _ = _resolve_reference(
            surfaces["caption_md"],
            root,
            "surfaces.caption_md",
            errors,
            warnings,
            required_exists=contract.get("status") in {"built", "verified"},
        )
    bindings = surfaces.get("bindings")
    if not isinstance(bindings, list):
        errors.append("surfaces.bindings: list required")
        bindings = []
    bound_ids: set[str] = set()
    ppt = surfaces.get("ppt", {}) if isinstance(surfaces.get("ppt", {}), dict) else {}
    ppt_required = ppt.get("required") is True
    visible_required = ppt.get("visible_explanations_required") is True
    if visible_required:
        visible_slides = ppt.get("visible_caption_slides")
        if not isinstance(visible_slides, list) or not visible_slides:
            errors.append("surfaces.ppt.visible_caption_slides: non-empty list required")
    for binding_index, binding in enumerate(bindings):
        prefix = f"surfaces.bindings[{binding_index}]"
        if not isinstance(binding, dict):
            errors.append(f"{prefix}: binding must be an object")
            continue
        element_id = binding.get("element_id")
        if element_id not in element_ids:
            errors.append(f"{prefix}.element_id: unknown element {element_id!r}")
        elif element_id in bound_ids:
            errors.append(f"{prefix}.element_id: duplicate binding {element_id}")
        else:
            bound_ids.add(element_id)
        for field in ("source", "manifest", "caption"):
            if not binding.get(field):
                errors.append(f"{prefix}.{field}: required")
        if ppt_required:
            for field in ("ppt_main", "notes"):
                if not binding.get(field):
                    errors.append(f"{prefix}.{field}: required for PPT delivery")
        if visible_required:
            for field in ("component_board", "visible_explanation"):
                if not binding.get(field):
                    errors.append(f"{prefix}.{field}: required for visible PPT explanations")
    missing_bindings = sorted(element_ids - bound_ids)
    if missing_bindings:
        errors.append(f"surfaces.bindings: missing elements {missing_bindings}")

    caption_hash = surfaces.get("caption_sha256")
    notes_hash = surfaces.get("notes_caption_sha256")
    for field, digest in (("caption_sha256", caption_hash), ("notes_caption_sha256", notes_hash)):
        if digest is not None and (
            not isinstance(digest, str) or not SHA256_RE.fullmatch(digest.lower())
        ):
            errors.append(f"surfaces.{field}: invalid sha256")
    if caption_hash and notes_hash and caption_hash != notes_hash:
        errors.append("surfaces: caption_sha256 and notes_caption_sha256 differ")
    if (
        caption_path is not None
        and caption_path.is_file()
        and isinstance(caption_hash, str)
        and SHA256_RE.fullmatch(caption_hash.lower())
        and sha256_file(caption_path) != caption_hash.lower()
    ):
        errors.append("surfaces.caption_sha256: differs from caption.md")
    if contract.get("status") == "verified" and ppt_required and (not caption_hash or not notes_hash):
        errors.append("surfaces: verified PPT contract requires caption and notes hashes")

    architecture = contract.get("architecture")
    if architecture is not None:
        if not isinstance(architecture, dict):
            errors.append("architecture: object required")
        else:
            nodes = architecture.get("nodes", [])
            edges = architecture.get("edges", [])
            if not isinstance(nodes, list):
                errors.append("architecture.nodes: list required")
                nodes = []
            if not isinstance(edges, list):
                errors.append("architecture.edges: list required")
                edges = []
            node_ids: set[str] = set()
            for index, node in enumerate(nodes):
                node_id = node.get("node_id") if isinstance(node, dict) else None
                if not node_id or node_id in node_ids:
                    errors.append(f"architecture.nodes[{index}].node_id: missing or duplicate")
                else:
                    node_ids.add(node_id)
                if not isinstance(node, dict) or not node.get("evidence_refs"):
                    errors.append(f"architecture.nodes[{index}].evidence_refs: required")
            edge_ids: set[str] = set()
            for index, edge in enumerate(edges):
                edge_id = edge.get("edge_id") if isinstance(edge, dict) else None
                if not edge_id or edge_id in edge_ids:
                    errors.append(f"architecture.edges[{index}].edge_id: missing or duplicate")
                else:
                    edge_ids.add(edge_id)
                if not isinstance(edge, dict) or edge.get("from") not in node_ids or edge.get("to") not in node_ids:
                    errors.append(f"architecture.edges[{index}]: endpoints must reference declared nodes")
                if not isinstance(edge, dict) or not edge.get("evidence_refs"):
                    errors.append(f"architecture.edges[{index}].evidence_refs: required")
            baseline = architecture.get("template_baseline")
            if baseline is not None:
                if not isinstance(baseline, dict) or not baseline.get("path") or not baseline.get("sha256"):
                    errors.append("architecture.template_baseline: path and sha256 required")
                else:
                    digest = baseline.get("sha256")
                    if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest.lower()):
                        errors.append("architecture.template_baseline.sha256: invalid")
                    if baseline.get("user_approved") is True and not baseline.get("approval_ref"):
                        errors.append("architecture.template_baseline.approval_ref: required when user approved")
                    if not isinstance(baseline.get("allowed_deviations", []), list):
                        errors.append("architecture.template_baseline.allowed_deviations: list required")
                    if not is_template and isinstance(digest, str) and SHA256_RE.fullmatch(digest.lower()):
                        _resolve_reference(
                            {"path": baseline.get("path"), "sha256": digest},
                            root,
                            "architecture.template_baseline",
                            errors,
                            warnings,
                            required_exists=True,
                        )

    rebuild = contract.get("rebuild")
    if not isinstance(rebuild, dict):
        errors.append("rebuild: object required")
        rebuild = {}
    rebuild_mode = rebuild.get("mode", "command")
    command = rebuild.get("command")
    if rebuild_mode == "command":
        if not isinstance(command, list) or not command or any(not isinstance(item, str) or not item for item in command):
            errors.append("rebuild.command: non-empty string array required in command mode")
    elif rebuild_mode == "manual":
        if not rebuild.get("instructions_ref"):
            errors.append("rebuild.instructions_ref: required in manual mode")
    else:
        errors.append("rebuild.mode: expected command or manual")
    if not rebuild.get("working_directory"):
        errors.append("rebuild.working_directory: required")
    inputs = rebuild.get("inputs")
    if not isinstance(inputs, list) or not inputs:
        errors.append("rebuild.inputs: at least one input required")
        inputs = []
    outputs = rebuild.get("outputs")
    if not isinstance(outputs, list) or not outputs:
        errors.append("rebuild.outputs: at least one output required")
        outputs = []

    if not is_template:
        if rebuild.get("working_directory"):
            working_directory, _, _ = _resolve_reference(
                rebuild["working_directory"],
                root,
                "rebuild.working_directory",
                errors,
                warnings,
                required_exists=True,
            )
            if working_directory is not None and working_directory.exists() and not working_directory.is_dir():
                errors.append("rebuild.working_directory: must be a directory")
        if rebuild_mode == "manual" and rebuild.get("instructions_ref"):
            _resolve_reference(
                rebuild["instructions_ref"],
                root,
                "rebuild.instructions_ref",
                errors,
                warnings,
                required_exists=contract.get("status") in {"built", "verified"},
            )
        layout_ref = contract.get("layout_ref")
        if layout_ref:
            _resolve_reference(
                layout_ref,
                root,
                "layout_ref",
                errors,
                warnings,
                required_exists=contract.get("status") in {"built", "verified"},
            )
        for index, value in enumerate(inputs):
            _resolve_reference(
                value,
                root,
                f"rebuild.inputs[{index}]",
                errors,
                warnings,
                required_exists=contract.get("status") in {"built", "verified"},
            )
        for index, value in enumerate(outputs):
            resolved, _, external = _resolve_reference(
                value,
                root,
                f"rebuild.outputs[{index}]",
                errors,
                warnings,
                required_exists=contract.get("status") in {"built", "verified"},
            )
            if external:
                errors.append(f"rebuild.outputs[{index}]: outputs cannot be external")
            if resolved is not None and not _is_within(resolved, root):
                errors.append(f"rebuild.outputs[{index}]: output escapes figure root")

    baseline = contract.get("baseline")
    if not isinstance(baseline, dict) or not baseline.get("current_revision"):
        errors.append("baseline.current_revision: required")
    else:
        protected = baseline.get("protected_user_revisions", [])
        if not isinstance(protected, list):
            errors.append("baseline.protected_user_revisions: list required")
        else:
            for index, revision in enumerate(protected):
                prefix = f"baseline.protected_user_revisions[{index}]"
                if not isinstance(revision, dict):
                    errors.append(f"{prefix}: object required")
                    continue
                for field in ("revision_id", "path", "sha256", "approval_ref"):
                    if not revision.get(field):
                        errors.append(f"{prefix}.{field}: required")
                digest = revision.get("sha256")
                if digest and (not isinstance(digest, str) or not SHA256_RE.fullmatch(digest.lower())):
                    errors.append(f"{prefix}.sha256: invalid")
                if not isinstance(revision.get("allowed_deviations", []), list):
                    errors.append(f"{prefix}.allowed_deviations: list required")
                if not is_template and isinstance(digest, str) and SHA256_RE.fullmatch(digest.lower()):
                    _resolve_reference(
                        {"path": revision.get("path"), "sha256": digest},
                        root,
                        prefix,
                        errors,
                        warnings,
                        required_exists=True,
                    )

    revision = contract.get("revision")
    if not isinstance(revision, dict):
        errors.append("revision: object required")
    else:
        if revision.get("change_class") not in {"initial", "visual", "scientific", "mixed"}:
            errors.append("revision.change_class: expected initial, visual, scientific, or mixed")
        for field in ("changed_refs", "invalidated_outputs"):
            value = revision.get(field)
            if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
                errors.append(f"revision.{field}: string list required")

    if previous is not None:
        errors.extend(compare_contracts(previous, contract))

    report = {
        "schema_version": contract.get("schema_version"),
        "figure_id": contract.get("figure_id"),
        "status": contract.get("status"),
        "semantic_fingerprint": semantic_fingerprint(contract),
        "panel_count": len(panel_ids),
        "element_count": len(element_ids),
        "errors": errors,
        "warnings": warnings,
        "valid": not errors,
    }
    return errors, warnings, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--root", type=Path, help="Figure package root; defaults to the contract directory")
    parser.add_argument("--previous", type=Path, help="Previous contract for revision/invalidation checks")
    parser.add_argument("--allow-template", action="store_true")
    args = parser.parse_args()

    contract_path = args.contract.resolve(strict=True)
    contract = load_contract(contract_path)
    previous = load_contract(args.previous.resolve(strict=True)) if args.previous else None
    errors, _, report = validate_contract(
        contract,
        contract_path,
        root=args.root,
        allow_template=args.allow_template,
        previous=previous,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
