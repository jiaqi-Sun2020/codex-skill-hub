"""Dependency-light loading and validation for paper-wide figure style manifests."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

REQUIRED_SECTIONS = {
    "schema_version",
    "project_id",
    "state",
    "references",
    "precedence",
    "palette",
    "semantic_colors",
    "neutral_colors",
    "backgrounds",
    "typography",
    "strokes",
    "arrows",
    "borders",
    "corners",
    "fills",
    "shadows",
    "spacing",
    "panels",
    "axes",
    "ticks",
    "legend",
    "grid",
    "markers",
    "charts",
    "architecture",
    "powerpoint",
    "overrides",
    "conflicts",
    "unresolved_issues",
}

# Keep REQUIRED_SECTIONS as the legacy full-template vocabulary. Consumers
# select only their additional requirements; no task state is stored in YAML.
TASK_REQUIRED_SECTIONS = {
    "general": set(),
    "svg": set(),
    "architecture": {"architecture", "arrows", "borders", "corners", "fills", "shadows", "spacing"},
    "plot": {"axes", "ticks", "legend", "grid", "markers", "charts", "spacing", "panels"},
    "powerpoint": {"powerpoint", "arrows", "borders", "corners", "fills", "shadows", "spacing", "panels"},
}
COMMON_REQUIRED_SECTIONS = REQUIRED_SECTIONS - set().union(*TASK_REQUIRED_SECTIONS.values())
LIST_SECTIONS = {"precedence", "overrides", "conflicts", "unresolved_issues"}
OBJECT_SECTIONS = REQUIRED_SECTIONS - LIST_SECTIONS - {"schema_version", "project_id"}

# Legacy exported example vocabulary, retained for callers; not universal
# requirements. Validation below checks only roles actually used by a consumer.
REQUIRED_SEMANTIC_ROLES = {
    "proposed_method",
    "baseline",
    "encoder",
    "decoder",
    "fusion",
    "attention",
    "input",
    "output",
    "uncertainty",
    "highlight",
}

REFERENCE_ROLES = {"primary_style", "chart_style", "architecture_style", "layout_inspiration"}
LOCK_STATES = {"provisional", "approved", "locked"}
SEMANTIC_ROLE_ALIASES = {"control": "baseline", "treatment": "proposed_method", "comparison": "baseline", "model": "proposed_method", "negative": "output", "positive": "proposed_method"}
HEX_COLOUR = re.compile(r"^#[0-9A-Fa-f]{6}$")


class StyleManifestError(ValueError):
    """Raised when the manifest cannot be parsed safely."""


def load_style_manifest(path: str | Path) -> dict[str, Any]:
    """Load JSON-compatible YAML, or full YAML when PyYAML is already available."""
    manifest_path = Path(path)
    if not manifest_path.exists():
        raise StyleManifestError(f"Style manifest not found: {manifest_path}")
    text = manifest_path.read_text(encoding="utf-8-sig")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as json_error:
        try:
            import yaml  # type: ignore
        except ImportError as exc:
            raise StyleManifestError(
                "Manifest is not JSON-compatible YAML and PyYAML is unavailable. "
                "Use assets/style_manifest.template.yaml or provide a normalized JSON file."
            ) from exc
        try:
            payload = yaml.safe_load(text)
        except Exception as yaml_error:  # noqa: BLE001
            raise StyleManifestError(f"Invalid style manifest: {yaml_error}") from json_error
    if not isinstance(payload, dict):
        raise StyleManifestError("Style manifest root must be an object.")
    return payload


def nested(manifest: dict[str, Any] | None, *keys: str, default: Any = None) -> Any:
    value: Any = manifest or {}
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return default
        value = value[key]
    return value


def _walk_colours(value: Any, prefix: str = ""):
    if isinstance(value, dict):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            yield from _walk_colours(child, child_prefix)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_colours(child, f"{prefix}[{index}]")
    elif prefix.split(".", 1)[0] in {"palette", "semantic_colors", "neutral_colors", "backgrounds"} or prefix.endswith(".color"):
        yield prefix, value


def semantic_colour_errors(semantic: Any) -> list[str]:
    """Validate declared role values before a consumer can stringify them."""
    if not isinstance(semantic, dict):
        return ["semantic_colors must be an object"]
    return [f"semantic_colors.{role} must be a six-digit hex colour, got {colour!r}"
            for role, colour in semantic.items()
            if not isinstance(colour, str) or not HEX_COLOUR.fullmatch(colour)]


def validate_style_manifest(
    manifest: dict[str, Any], used_roles: list[str] | None = None,
    *, tasks: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Validate common identity/locks/tokens plus the real consumer's sections.

    With no tasks, check common requirements, not readiness for every format.
    Supplied but unused sections still receive type and colour checks.
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(manifest, dict):
        return ["style manifest root must be an object"], warnings
    required = set(COMMON_REQUIRED_SECTIONS)
    requested = [tasks] if isinstance(tasks, str) else (tasks or ["general"])
    for task in requested:
        if not isinstance(task, str) or task not in TASK_REQUIRED_SECTIONS:
            errors.append(f"unknown style task: {task!r}")
        else:
            required.update(TASK_REQUIRED_SECTIONS[task])
    missing_sections = sorted(required - set(manifest))
    errors.extend(f"missing required section: {section}" for section in missing_sections)

    version = manifest.get("schema_version")
    # YAML/JSON numeric 1.0 and the existing string form denote the same
    # schema. Do not coerce arbitrary values (especially bool, an int subclass).
    if not ((type(version) in (int, float) and version == 1.0)
            or (type(version) is str and version == "1.0")):
        errors.append('schema_version must be numeric 1.0 or the string "1.0"')
    if not isinstance(manifest.get("project_id"), str) or not manifest["project_id"].strip():
        errors.append("project_id must be a non-empty string")
    for field in sorted(OBJECT_SECTIONS & set(manifest)):
        if not isinstance(manifest[field], dict):
            errors.append(f"{field} must be an object")
    for field in sorted(LIST_SECTIONS & set(manifest)):
        if not isinstance(manifest[field], list):
            errors.append(f"{field} must be a list")

    state = manifest.get("state")
    if not isinstance(state, dict):
        errors.append("state must be an object")
    else:
        status = state.get("status")
        locked = state.get("locked")
        if status not in LOCK_STATES:
            errors.append(f"state.status must be one of {sorted(LOCK_STATES)}")
        if not isinstance(locked, bool):
            errors.append("state.locked must be true or false")
        if locked is True and status != "locked":
            errors.append("state.locked=true requires state.status=locked")
        if status == "locked" and locked is not True:
            errors.append("state.status=locked requires state.locked=true")

    semantic = manifest.get("semantic_colors")
    errors.extend(semantic_colour_errors(semantic))
    if isinstance(semantic, dict):
        # Old full manifests remain valid; unrelated example model roles are
        # not universal requirements for a statistical or conceptual figure.
        for role in sorted(set(used_roles or [])):
            canonical = role if role in semantic else SEMANTIC_ROLE_ALIASES.get(role, role)
            if canonical not in semantic:
                errors.append(f"semantic_colors missing used role: {role}")

    for key, colour in _walk_colours(manifest):
        if key.startswith("semantic_colors."):
            continue  # Role values (including non-strings) were checked above.
        if not isinstance(colour, str) or not HEX_COLOUR.fullmatch(colour):
            errors.append(f"{key} must be a six-digit hex colour, got {colour!r}")

    references = manifest.get("references")
    primary_count = 0
    if not isinstance(references, dict) or not references:
        errors.append("references must contain at least one reference")
    else:
        for reference_id, reference in references.items():
            if not isinstance(reference, dict):
                errors.append(f"references.{reference_id} must be an object")
                continue
            role = reference.get("role")
            if role not in REFERENCE_ROLES:
                errors.append(f"references.{reference_id}.role must be one of {sorted(REFERENCE_ROLES)}")
            if role == "primary_style":
                primary_count += 1
            if not reference.get("path"):
                warnings.append(f"references.{reference_id}.path is empty")
        if primary_count == 0:
            errors.append("one reference must have role=primary_style")
        if primary_count > 1:
            errors.append("only one reference may have role=primary_style")

    if not manifest.get("unresolved_issues") and nested(manifest, "state", "status") == "provisional":
        warnings.append("provisional manifest has no unresolved_issues")

    return errors, warnings


def normalized_json(manifest: dict[str, Any]) -> str:
    return json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
