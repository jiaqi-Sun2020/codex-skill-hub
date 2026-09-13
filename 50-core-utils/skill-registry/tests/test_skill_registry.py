import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS_DIR))

import skill_registry as registry


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def create_skill(path, marker):
    path.mkdir(parents=True, exist_ok=True)
    (path / "SKILL.md").write_text(
        "---\nname: demo\n"
        "description: Safe test skill.\n---\n\n# Demo\n\n{}\n".format(marker),
        encoding="utf-8",
    )
    references = path / "references"
    references.mkdir()
    (references / "contract.md").write_text(
        "# Contract\n\n{}\n".format(marker), encoding="utf-8"
    )


def create_registry(path):
    create_skill(path / "sources" / "demo", "version-one")
    write_json(
        path / "registry.json",
        {
            "schema_version": 1,
            "skills": {
                "demo": {
                    "current_version": None,
                    "description": "Test skill",
                    "releases": {},
                    "source": "sources/demo",
                }
            },
        },
    )


def create_project(path, registry_path, version="1.0.0"):
    path.mkdir(parents=True, exist_ok=True)
    write_json(
        path / "skills.manifest.json",
        {
            "schema_version": 1,
            "registry": str(registry_path),
            "skills": {
                "demo": {
                    "destination": "skills/demo",
                    "mode": "vendored",
                    "version": version,
                },
                "local-only": {
                    "destination": "skills/local-only",
                    "mode": "project-owned",
                },
            },
        },
    )


def run_cli(arguments):
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        code = registry.main(arguments)
    return code, stdout.getvalue(), stderr.getvalue()


class SkillRegistryTests(unittest.TestCase):
    def test_tree_hash_is_deterministic_and_ignores_caches(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            left = root / "left"
            right = root / "right"
            create_skill(left, "same")
            create_skill(right, "same")
            (left / "__pycache__").mkdir()
            (left / "__pycache__" / "ignored.pyc").write_bytes(b"left")
            (right / "ignored.pyc").write_bytes(b"right")
            left_hash, left_files = registry.tree_snapshot(left)
            right_hash, right_files = registry.tree_snapshot(right)
            self.assertEqual(left_hash, right_hash)
            self.assertEqual(left_files, right_files)
            self.assertNotIn("ignored.pyc", right_files)

    def test_bootstrap_keeps_backup_and_drift_blocks_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry_root = root / "registry"
            project_root = root / "project"
            create_registry(registry_root)
            create_project(project_root, registry_root)

            code, _, error = run_cli(
                [
                    "release",
                    "--registry",
                    str(registry_root),
                    "--skill",
                    "demo",
                    "--version",
                    "1.0.0",
                    "--apply",
                ]
            )
            self.assertEqual(code, 0, error)

            existing = project_root / "skills" / "demo"
            create_skill(existing, "project-old")
            original_text = (existing / "SKILL.md").read_text(encoding="utf-8")

            code, _, error = run_cli(
                [
                    "sync",
                    "--project",
                    str(project_root),
                    "--skill",
                    "demo",
                    "--apply",
                ]
            )
            self.assertEqual(code, 2)
            self.assertIn("--bootstrap", error)
            self.assertEqual(
                (existing / "SKILL.md").read_text(encoding="utf-8"), original_text
            )

            code, output, error = run_cli(
                [
                    "sync",
                    "--project",
                    str(project_root),
                    "--skill",
                    "demo",
                    "--bootstrap",
                    "--apply",
                ]
            )
            self.assertEqual(code, 0, error)
            self.assertIn("version-one", (existing / "SKILL.md").read_text("utf-8"))
            self.assertTrue((project_root / "skills.lock.json").is_file())
            backups = list(
                (project_root / ".skill-registry" / "backups" / "demo").iterdir()
            )
            self.assertEqual(len(backups), 1)
            self.assertIn(
                "project-old",
                (backups[0] / "SKILL.md").read_text(encoding="utf-8"),
            )
            self.assertIn('"applied": true', output)

            code, _, error = run_cli(
                ["check", "--project", str(project_root)]
            )
            self.assertEqual(code, 0, error)

            with (existing / "SKILL.md").open("a", encoding="utf-8") as handle:
                handle.write("\nlocal drift\n")
            drift_text = (existing / "SKILL.md").read_text(encoding="utf-8")
            code, _, error = run_cli(
                [
                    "sync",
                    "--project",
                    str(project_root),
                    "--skill",
                    "demo",
                    "--apply",
                ]
            )
            self.assertEqual(code, 2)
            self.assertIn("local drift", error)
            self.assertEqual(
                (existing / "SKILL.md").read_text(encoding="utf-8"), drift_text
            )

    def test_version_update_is_pinned_and_reviewable(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry_root = root / "registry"
            project_root = root / "project"
            create_registry(registry_root)
            create_project(project_root, registry_root)

            self.assertEqual(
                run_cli(
                    [
                        "release",
                        "--registry",
                        str(registry_root),
                        "--skill",
                        "demo",
                        "--version",
                        "1.0.0",
                        "--apply",
                    ]
                )[0],
                0,
            )
            self.assertEqual(
                run_cli(
                    [
                        "sync",
                        "--project",
                        str(project_root),
                        "--skill",
                        "demo",
                        "--apply",
                    ]
                )[0],
                0,
            )

            source = registry_root / "sources" / "demo"
            (source / "SKILL.md").write_text(
                (source / "SKILL.md").read_text("utf-8") + "\nversion-two\n",
                encoding="utf-8",
            )
            self.assertEqual(
                run_cli(
                    [
                        "release",
                        "--registry",
                        str(registry_root),
                        "--skill",
                        "demo",
                        "--version",
                        "1.1.0",
                        "--apply",
                    ]
                )[0],
                0,
            )
            manifest_path = project_root / "skills.manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["skills"]["demo"]["version"] = "1.1.0"
            write_json(manifest_path, manifest)

            check_code, check_output, _ = run_cli(
                ["check", "--project", str(project_root)]
            )
            self.assertEqual(check_code, 2)
            self.assertIn("update_available", check_output)

            preview_code, preview_output, _ = run_cli(
                [
                    "sync",
                    "--project",
                    str(project_root),
                    "--skill",
                    "demo",
                ]
            )
            self.assertEqual(preview_code, 0)
            self.assertIn('"applied": false', preview_output)
            self.assertNotIn(
                "version-two",
                (project_root / "skills" / "demo" / "SKILL.md").read_text("utf-8"),
            )

            apply_code, _, apply_error = run_cli(
                [
                    "sync",
                    "--project",
                    str(project_root),
                    "--skill",
                    "demo",
                    "--apply",
                ]
            )
            self.assertEqual(apply_code, 0, apply_error)
            self.assertIn(
                "version-two",
                (project_root / "skills" / "demo" / "SKILL.md").read_text("utf-8"),
            )
            lock = json.loads(
                (project_root / "skills.lock.json").read_text(encoding="utf-8")
            )
            self.assertEqual(lock["skills"]["demo"]["version"], "1.1.0")

    def test_destination_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry_root = root / "registry"
            project_root = root / "project"
            create_registry(registry_root)
            create_project(project_root, registry_root)
            self.assertEqual(
                run_cli(
                    [
                        "release",
                        "--registry",
                        str(registry_root),
                        "--skill",
                        "demo",
                        "--version",
                        "1.0.0",
                        "--apply",
                    ]
                )[0],
                0,
            )
            manifest_path = project_root / "skills.manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["skills"]["demo"]["destination"] = "../escape"
            write_json(manifest_path, manifest)
            code, output, error = run_cli(
                ["check", "--project", str(project_root)]
            )
            self.assertEqual(code, 2)
            self.assertIn("safe relative path", output + error)
            self.assertFalse((root / "escape").exists())


if __name__ == "__main__":
    unittest.main()
