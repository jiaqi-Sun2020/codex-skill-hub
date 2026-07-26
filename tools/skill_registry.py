#!/usr/bin/env python3
"""Versioned, fail-closed vendoring for project-local Codex skills."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple


SCHEMA_VERSION = 1
EXCLUDED_DIRECTORIES = {".git", ".pytest_cache", "__pycache__"}
EXCLUDED_FILES = {".DS_Store"}
EXCLUDED_SUFFIXES = {".pyc"}
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


class RegistryError(RuntimeError):
    """A safe, user-actionable registry failure."""


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            value = json.load(handle)
    except FileNotFoundError:
        raise RegistryError("Missing JSON file: {}".format(path))
    except json.JSONDecodeError as exc:
        raise RegistryError("Invalid JSON in {}: {}".format(path, exc))
    if not isinstance(value, dict):
        raise RegistryError("Expected a JSON object in {}".format(path))
    return value


def atomic_write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix="." + path.name + ".",
        suffix=".tmp",
        dir=str(path.parent),
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, str(path))
    except Exception:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise


def ensure_schema(document: Mapping[str, Any], path: Path) -> None:
    if document.get("schema_version") != SCHEMA_VERSION:
        raise RegistryError(
            "{} must use schema_version {}".format(path, SCHEMA_VERSION)
        )


def resolve_root(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.is_dir():
        raise RegistryError("Directory does not exist: {}".format(resolved))
    return resolved


def resolve_within(root: Path, relative: str, label: str) -> Path:
    relative_path = Path(relative)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise RegistryError("{} must be a safe relative path: {}".format(label, relative))
    candidate = (root / relative_path).resolve()
    try:
        common = Path(os.path.commonpath([str(root), str(candidate)]))
    except ValueError:
        raise RegistryError("{} escapes its root: {}".format(label, relative))
    if os.path.normcase(str(common)) != os.path.normcase(str(root)):
        raise RegistryError("{} escapes its root: {}".format(label, relative))
    return candidate


def should_exclude_file(path: Path) -> bool:
    return path.name in EXCLUDED_FILES or path.suffix.lower() in EXCLUDED_SUFFIXES


def iter_skill_files(root: Path) -> Iterable[Tuple[str, Path]]:
    if not root.is_dir():
        raise RegistryError("Skill directory does not exist: {}".format(root))
    if root.is_symlink():
        raise RegistryError("Skill root cannot be a symbolic link: {}".format(root))
    for current, directory_names, file_names in os.walk(str(root), followlinks=False):
        current_path = Path(current)
        safe_directories: List[str] = []
        for directory_name in sorted(directory_names):
            child = current_path / directory_name
            if directory_name in EXCLUDED_DIRECTORIES:
                continue
            if child.is_symlink():
                raise RegistryError("Skill tree contains a directory link: {}".format(child))
            safe_directories.append(directory_name)
        directory_names[:] = safe_directories
        for file_name in sorted(file_names):
            file_path = current_path / file_name
            if should_exclude_file(file_path):
                continue
            if file_path.is_symlink():
                raise RegistryError("Skill tree contains a file link: {}".format(file_path))
            relative = file_path.relative_to(root).as_posix()
            yield relative, file_path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def tree_snapshot(root: Path) -> Tuple[str, Dict[str, Dict[str, Any]]]:
    files: Dict[str, Dict[str, Any]] = {}
    tree_digest = hashlib.sha256()
    for relative, path in iter_skill_files(root):
        file_hash = sha256_file(path)
        size = path.stat().st_size
        files[relative] = {"sha256": file_hash, "size": size}
        record = "{}\0{}\0{}\n".format(relative, size, file_hash)
        tree_digest.update(record.encode("utf-8"))
    if "SKILL.md" not in files:
        raise RegistryError("Skill tree has no root SKILL.md: {}".format(root))
    return tree_digest.hexdigest(), files


def copy_skill_tree(source: Path, destination: Path) -> None:
    if destination.exists():
        raise RegistryError("Destination already exists: {}".format(destination))
    destination.mkdir(parents=True)
    try:
        for relative, source_file in iter_skill_files(source):
            destination_file = destination / Path(relative)
            destination_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(source_file), str(destination_file))
    except Exception:
        shutil.rmtree(str(destination), ignore_errors=True)
        raise


def compare_trees(source: Path, local: Path) -> Dict[str, Any]:
    source_hash, source_files = tree_snapshot(source)
    local_hash, local_files = tree_snapshot(local)
    all_paths = sorted(set(source_files) | set(local_files))
    same: List[str] = []
    changed: List[str] = []
    source_only: List[str] = []
    local_only: List[str] = []
    for relative in all_paths:
        if relative not in local_files:
            source_only.append(relative)
        elif relative not in source_files:
            local_only.append(relative)
        elif source_files[relative]["sha256"] == local_files[relative]["sha256"]:
            same.append(relative)
        else:
            changed.append(relative)
    return {
        "source_hash": source_hash,
        "local_hash": local_hash,
        "same_count": len(same),
        "changed": changed,
        "source_only": source_only,
        "local_only": local_only,
    }


def registry_path(registry_root: Path) -> Path:
    return registry_root / "registry.json"


def load_registry(registry_root: Path) -> Dict[str, Any]:
    path = registry_path(registry_root)
    registry = read_json(path)
    ensure_schema(registry, path)
    if not isinstance(registry.get("skills"), dict):
        raise RegistryError("{} must contain a skills object".format(path))
    return registry


def load_project(project_root: Path) -> Tuple[Path, Dict[str, Any], Path, Dict[str, Any]]:
    manifest_path = project_root / "skills.manifest.json"
    manifest = read_json(manifest_path)
    ensure_schema(manifest, manifest_path)
    if not isinstance(manifest.get("skills"), dict):
        raise RegistryError("{} must contain a skills object".format(manifest_path))
    lock_path = project_root / "skills.lock.json"
    if lock_path.exists():
        lock = read_json(lock_path)
        ensure_schema(lock, lock_path)
        if not isinstance(lock.get("skills"), dict):
            raise RegistryError("{} must contain a skills object".format(lock_path))
    else:
        lock = {"schema_version": SCHEMA_VERSION, "skills": {}}
    return manifest_path, manifest, lock_path, lock


def manifest_registry_root(
    manifest: Mapping[str, Any], override: Optional[str]
) -> Path:
    raw = override or manifest.get("registry")
    if not isinstance(raw, str) or not raw.strip():
        raise RegistryError("Manifest must define registry or use --registry")
    return resolve_root(Path(raw))


def registry_release(
    registry_root: Path,
    registry: Mapping[str, Any],
    skill_id: str,
    version: str,
) -> Tuple[Path, Mapping[str, Any]]:
    skill_entry = registry["skills"].get(skill_id)
    if not isinstance(skill_entry, dict):
        raise RegistryError("Registry has no skill '{}'".format(skill_id))
    releases = skill_entry.get("releases")
    if not isinstance(releases, dict) or version not in releases:
        raise RegistryError(
            "Registry has no release {} for '{}'".format(version, skill_id)
        )
    release = releases[version]
    if not isinstance(release, dict):
        raise RegistryError("Invalid release record for {} {}".format(skill_id, version))
    relative_path = release.get("path")
    expected_hash = release.get("sha256")
    if not isinstance(relative_path, str) or not isinstance(expected_hash, str):
        raise RegistryError("Release record is missing path or sha256")
    release_root = resolve_within(registry_root, relative_path, "release path")
    actual_hash, _ = tree_snapshot(release_root)
    if actual_hash != expected_hash:
        raise RegistryError(
            "Registry release integrity failure for {} {}: expected {}, got {}".format(
                skill_id, version, expected_hash, actual_hash
            )
        )
    return release_root, release


def manifest_skill(
    manifest: Mapping[str, Any], skill_id: str
) -> MutableMapping[str, Any]:
    value = manifest["skills"].get(skill_id)
    if not isinstance(value, dict):
        raise RegistryError("Manifest has no skill '{}'".format(skill_id))
    mode = value.get("mode")
    if mode not in {"vendored", "forked", "project-owned"}:
        raise RegistryError(
            "Skill '{}' has unsupported mode '{}'".format(skill_id, mode)
        )
    return value


def vendored_context(
    project_root: Path,
    manifest: Mapping[str, Any],
    registry_root: Path,
    registry: Mapping[str, Any],
    skill_id: str,
) -> Tuple[MutableMapping[str, Any], str, Path, Path, Mapping[str, Any]]:
    skill = manifest_skill(manifest, skill_id)
    if skill["mode"] != "vendored":
        raise RegistryError(
            "Skill '{}' is {}, not vendored".format(skill_id, skill["mode"])
        )
    version = skill.get("version")
    destination_value = skill.get("destination")
    if not isinstance(version, str) or not SEMVER_RE.match(version):
        raise RegistryError("Skill '{}' has an invalid version".format(skill_id))
    if not isinstance(destination_value, str):
        raise RegistryError("Skill '{}' has no destination".format(skill_id))
    destination = resolve_within(
        project_root, destination_value, "destination for {}".format(skill_id)
    )
    release_root, release = registry_release(
        registry_root, registry, skill_id, version
    )
    return skill, version, destination, release_root, release


def project_skill_status(
    project_root: Path,
    manifest: Mapping[str, Any],
    lock: Mapping[str, Any],
    registry_root: Path,
    registry: Mapping[str, Any],
    skill_id: str,
) -> Dict[str, Any]:
    skill = manifest_skill(manifest, skill_id)
    if skill["mode"] != "vendored":
        destination_value = skill.get("destination")
        exists = False
        if isinstance(destination_value, str):
            destination = resolve_within(
                project_root, destination_value, "destination for {}".format(skill_id)
            )
            exists = destination.is_dir()
        return {
            "skill": skill_id,
            "mode": skill["mode"],
            "status": "ignored",
            "destination_exists": exists,
        }

    skill, version, destination, release_root, release = vendored_context(
        project_root, manifest, registry_root, registry, skill_id
    )
    source_hash = release["sha256"]
    lock_entry = lock["skills"].get(skill_id)
    base: Dict[str, Any] = {
        "skill": skill_id,
        "mode": "vendored",
        "version": version,
        "destination": str(destination),
        "registry_hash": source_hash,
    }
    if not destination.exists():
        base["status"] = "missing"
        return base
    if not destination.is_dir():
        base["status"] = "destination_not_directory"
        return base
    local_hash, _ = tree_snapshot(destination)
    base["local_hash"] = local_hash
    if not isinstance(lock_entry, dict):
        base["status"] = (
            "unlocked_match" if local_hash == source_hash else "unmanaged_existing"
        )
        return base
    locked_hash = lock_entry.get("local_hash")
    locked_registry_hash = lock_entry.get("registry_hash")
    locked_version = lock_entry.get("version")
    base["locked_version"] = locked_version
    base["locked_hash"] = locked_hash
    if local_hash != locked_hash:
        base["status"] = "local_drift"
    elif (
        local_hash == source_hash
        and locked_registry_hash == source_hash
        and locked_version == version
    ):
        base["status"] = "current"
    else:
        base["status"] = "update_available"
    return base


def lock_entry(
    skill_id: str,
    version: str,
    destination: str,
    source_hash: str,
) -> Dict[str, Any]:
    return {
        "destination": destination,
        "local_hash": source_hash,
        "registry_hash": source_hash,
        "synced_at": utc_now(),
        "version": version,
    }


def ensure_control_directory(project_root: Path) -> Path:
    control_root = project_root / ".skill-registry"
    control_root.mkdir(parents=True, exist_ok=True)
    ignore_file = control_root / ".gitignore"
    if not ignore_file.exists():
        try:
            with ignore_file.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write("*\n")
        except FileExistsError:
            pass
    return control_root


def backup_destination(project_root: Path, skill_id: str, destination: Path) -> Path:
    current_hash, _ = tree_snapshot(destination)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_root = ensure_control_directory(project_root) / "backups" / skill_id
    backup_root.mkdir(parents=True, exist_ok=True)
    backup = backup_root / "{}-{}".format(stamp, current_hash[:12])
    counter = 1
    while backup.exists():
        backup = backup_root / "{}-{}-{}".format(stamp, current_hash[:12], counter)
        counter += 1
    return backup


def sync_one(
    project_root: Path,
    manifest: Mapping[str, Any],
    lock_path: Path,
    lock: MutableMapping[str, Any],
    registry_root: Path,
    registry: Mapping[str, Any],
    skill_id: str,
    apply: bool,
    bootstrap: bool,
) -> Dict[str, Any]:
    skill, version, destination, release_root, release = vendored_context(
        project_root, manifest, registry_root, registry, skill_id
    )
    status = project_skill_status(
        project_root, manifest, lock, registry_root, registry, skill_id
    )
    status_name = status["status"]
    if status_name == "local_drift":
        raise RegistryError(
            "Refusing to overwrite local drift in '{}'. Run diff and restore or fork it first.".format(
                skill_id
            )
        )
    if status_name == "destination_not_directory":
        raise RegistryError("Destination is not a directory: {}".format(destination))
    if status_name == "unmanaged_existing" and not bootstrap:
        raise RegistryError(
            "Existing '{}' has no lock and differs from the registry. "
            "Review diff, then rerun with --bootstrap.".format(skill_id)
        )
    if status_name == "current":
        return {
            "skill": skill_id,
            "status": "current",
            "applied": False,
            "backup": None,
        }

    destination_value = skill["destination"]
    action = "lock-only" if status_name == "unlocked_match" else "replace"
    preview = {
        "skill": skill_id,
        "status_before": status_name,
        "action": action,
        "applied": apply,
        "version": version,
        "destination": str(destination),
        "registry_hash": release["sha256"],
        "backup": None,
    }
    if not apply:
        preview["applied"] = False
        return preview

    if action == "lock-only":
        lock["skills"][skill_id] = lock_entry(
            skill_id, version, destination_value, release["sha256"]
        )
        atomic_write_json(lock_path, lock)
        return preview

    staging_root = ensure_control_directory(project_root) / "staging"
    staging_root.mkdir(parents=True, exist_ok=True)
    staging = staging_root / "{}-{}".format(skill_id, uuid.uuid4().hex)
    copy_skill_tree(release_root, staging)
    staged_hash, _ = tree_snapshot(staging)
    if staged_hash != release["sha256"]:
        shutil.rmtree(str(staging), ignore_errors=True)
        raise RegistryError("Staged copy hash mismatch for '{}'".format(skill_id))

    backup: Optional[Path] = None
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        if destination.exists():
            backup = backup_destination(project_root, skill_id, destination)
            os.replace(str(destination), str(backup))
        os.replace(str(staging), str(destination))
        lock["skills"][skill_id] = lock_entry(
            skill_id, version, destination_value, release["sha256"]
        )
        atomic_write_json(lock_path, lock)
    except Exception:
        if destination.exists():
            shutil.rmtree(str(destination), ignore_errors=True)
        if backup is not None and backup.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.replace(str(backup), str(destination))
        if staging.exists():
            shutil.rmtree(str(staging), ignore_errors=True)
        raise
    preview["backup"] = str(backup) if backup is not None else None
    return preview


def command_release(args: argparse.Namespace) -> int:
    registry_root = resolve_root(Path(args.registry))
    registry = load_registry(registry_root)
    if not SEMVER_RE.match(args.version):
        raise RegistryError("Invalid semantic version: {}".format(args.version))
    skill_entry = registry["skills"].get(args.skill)
    if not isinstance(skill_entry, dict):
        raise RegistryError("Registry has no skill '{}'".format(args.skill))
    source_value = skill_entry.get("source")
    if not isinstance(source_value, str):
        raise RegistryError("Skill '{}' has no source path".format(args.skill))
    source = resolve_within(registry_root, source_value, "source path")
    source_hash, source_files = tree_snapshot(source)
    release_relative = "releases/{}/{}".format(args.skill, args.version)
    release_path = resolve_within(registry_root, release_relative, "release path")
    releases = skill_entry.setdefault("releases", {})
    if args.version in releases or release_path.exists():
        raise RegistryError(
            "Release already exists: {} {}".format(args.skill, args.version)
        )
    result = {
        "action": "release",
        "skill": args.skill,
        "version": args.version,
        "source": str(source),
        "release": str(release_path),
        "sha256": source_hash,
        "file_count": len(source_files),
        "applied": bool(args.apply),
    }
    if not args.apply:
        print_json(result)
        return 0
    temporary = release_path.parent / ".{}-{}".format(args.version, uuid.uuid4().hex)
    release_path.parent.mkdir(parents=True, exist_ok=True)
    copy_skill_tree(source, temporary)
    try:
        copied_hash, _ = tree_snapshot(temporary)
        if copied_hash != source_hash:
            raise RegistryError("Release staging hash mismatch")
        os.replace(str(temporary), str(release_path))
        releases[args.version] = {
            "path": release_relative,
            "released_at": utc_now(),
            "sha256": source_hash,
        }
        skill_entry["current_version"] = args.version
        atomic_write_json(registry_path(registry_root), registry)
    except Exception:
        if temporary.exists():
            shutil.rmtree(str(temporary), ignore_errors=True)
        if release_path.exists() and args.version not in read_json(
            registry_path(registry_root)
        ).get("skills", {}).get(args.skill, {}).get("releases", {}):
            shutil.rmtree(str(release_path), ignore_errors=True)
        raise
    print_json(result)
    return 0


def command_registry_check(args: argparse.Namespace) -> int:
    registry_root = resolve_root(Path(args.registry))
    registry = load_registry(registry_root)
    results: List[Dict[str, Any]] = []
    healthy = True
    for skill_id in sorted(registry["skills"]):
        entry = registry["skills"][skill_id]
        if not isinstance(entry, dict):
            results.append({"skill": skill_id, "status": "invalid_entry"})
            healthy = False
            continue
        source_value = entry.get("source")
        try:
            source = resolve_within(registry_root, source_value, "source path")
            source_hash, source_files = tree_snapshot(source)
            releases = entry.get("releases", {})
            release_results: List[Dict[str, Any]] = []
            for version in sorted(releases):
                release_root, release = registry_release(
                    registry_root, registry, skill_id, version
                )
                release_results.append(
                    {
                        "version": version,
                        "path": str(release_root),
                        "sha256": release["sha256"],
                        "status": "valid",
                    }
                )
            results.append(
                {
                    "skill": skill_id,
                    "status": "valid",
                    "source_hash": source_hash,
                    "source_file_count": len(source_files),
                    "releases": release_results,
                }
            )
        except (RegistryError, TypeError) as exc:
            healthy = False
            results.append(
                {"skill": skill_id, "status": "invalid", "error": str(exc)}
            )
    print_json({"healthy": healthy, "skills": results})
    return 0 if healthy else 2


def project_context(
    args: argparse.Namespace,
) -> Tuple[Path, Dict[str, Any], Path, Dict[str, Any], Path, Dict[str, Any]]:
    project_root = resolve_root(Path(args.project))
    _, manifest, lock_path, lock = load_project(project_root)
    registry_root = manifest_registry_root(manifest, getattr(args, "registry", None))
    registry = load_registry(registry_root)
    return project_root, manifest, lock_path, lock, registry_root, registry


def command_check(args: argparse.Namespace) -> int:
    project_root, manifest, _, lock, registry_root, registry = project_context(args)
    results: List[Dict[str, Any]] = []
    healthy = True
    for skill_id in sorted(manifest["skills"]):
        try:
            result = project_skill_status(
                project_root, manifest, lock, registry_root, registry, skill_id
            )
        except RegistryError as exc:
            result = {"skill": skill_id, "status": "error", "error": str(exc)}
        results.append(result)
        if result.get("mode") == "vendored" and result.get("status") != "current":
            healthy = False
        if result.get("status") == "error":
            healthy = False
    print_json(
        {
            "healthy": healthy,
            "project": str(project_root),
            "registry": str(registry_root),
            "skills": results,
        }
    )
    return 0 if healthy else 2


def command_diff(args: argparse.Namespace) -> int:
    project_root, manifest, _, _, registry_root, registry = project_context(args)
    _, _, destination, release_root, _ = vendored_context(
        project_root, manifest, registry_root, registry, args.skill
    )
    if not destination.is_dir():
        print_json(
            {
                "skill": args.skill,
                "status": "missing",
                "destination": str(destination),
            }
        )
        return 2
    result = compare_trees(release_root, destination)
    result.update(
        {
            "skill": args.skill,
            "source": str(release_root),
            "destination": str(destination),
            "identical": result["source_hash"] == result["local_hash"],
        }
    )
    print_json(result)
    return 0 if result["identical"] else 2


def command_sync(args: argparse.Namespace) -> int:
    project_root, manifest, lock_path, lock, registry_root, registry = project_context(
        args
    )
    result = sync_one(
        project_root,
        manifest,
        lock_path,
        lock,
        registry_root,
        registry,
        args.skill,
        args.apply,
        args.bootstrap,
    )
    print_json(result)
    return 0


def command_sync_all(args: argparse.Namespace) -> int:
    project_root, manifest, lock_path, lock, registry_root, registry = project_context(
        args
    )
    results: List[Dict[str, Any]] = []
    for skill_id in sorted(manifest["skills"]):
        skill = manifest_skill(manifest, skill_id)
        if skill["mode"] != "vendored":
            continue
        results.append(
            sync_one(
                project_root,
                manifest,
                lock_path,
                lock,
                registry_root,
                registry,
                skill_id,
                args.apply,
                args.bootstrap,
            )
        )
    print_json({"project": str(project_root), "results": results})
    return 0


def print_json(value: Mapping[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Versioned, fail-closed vendoring for project-local Codex skills."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    release_parser = subparsers.add_parser(
        "release", help="Create an immutable release from a canonical source."
    )
    release_parser.add_argument("--registry", required=True)
    release_parser.add_argument("--skill", required=True)
    release_parser.add_argument("--version", required=True)
    release_parser.add_argument("--apply", action="store_true")
    release_parser.set_defaults(func=command_release)

    registry_check_parser = subparsers.add_parser(
        "registry-check", help="Verify sources and immutable release hashes."
    )
    registry_check_parser.add_argument("--registry", required=True)
    registry_check_parser.set_defaults(func=command_registry_check)

    for name, help_text, func in [
        ("check", "Check project locks, drift, and update status.", command_check),
        ("diff", "Compare one project copy with its pinned release.", command_diff),
        ("sync", "Preview or apply one safe vendored update.", command_sync),
        ("sync-all", "Preview or apply all vendored updates.", command_sync_all),
    ]:
        command_parser = subparsers.add_parser(name, help=help_text)
        command_parser.add_argument("--project", required=True)
        command_parser.add_argument("--registry")
        if name in {"diff", "sync"}:
            command_parser.add_argument("--skill", required=True)
        if name in {"sync", "sync-all"}:
            command_parser.add_argument("--apply", action="store_true")
            command_parser.add_argument(
                "--bootstrap",
                action="store_true",
                help="Allow first-time replacement of an unlocked existing copy; a backup is kept.",
            )
        command_parser.set_defaults(func=func)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except RegistryError as exc:
        print("ERROR: {}".format(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
