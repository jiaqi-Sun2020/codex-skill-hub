from __future__ import annotations

import importlib.util
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "inventory_workspace.py"
SPEC = importlib.util.spec_from_file_location("inventory_workspace", SCRIPT)
assert SPEC and SPEC.loader
inventory = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = inventory
SPEC.loader.exec_module(inventory)


class InventoryWorkspaceTests(unittest.TestCase):
    def make_project(self, parent: Path) -> Path:
        project = parent / "legacy-research"
        (project / "data" / "raw").mkdir(parents=True)
        (project / "data" / "processed").mkdir()
        (project / "runs" / "run-001").mkdir(parents=True)
        (project / ".tmp").mkdir()
        (project / "src").mkdir()
        (project / "README.md").write_text("# Research\n", encoding="utf-8")
        (project / "data" / "raw" / "observations.csv").write_text(
            "id,value\n1,2\n", encoding="utf-8"
        )
        (project / "data" / "processed" / "clean.csv").write_text(
            "id,value\n1,2\n", encoding="utf-8"
        )
        (project / ".tmp" / "preview.tmp.json").write_text("{}\n", encoding="utf-8")
        (project / ".env").write_text("TOKEN=do-not-read\n", encoding="utf-8")
        return project

    def test_inventory_classifies_roles_without_reading_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            payload = inventory.build_inventory(project)
            self.assertEqual(payload["status"], "inspected")
            self.assertFalse(payload["scan"]["sensitive_contents_inspected"])
            self.assertEqual(payload["scan"]["sensitive_surface_count"], 1)
            self.assertIn("data/raw/", payload["role_candidates"]["source_records"])
            self.assertIn("data/processed/", payload["role_candidates"]["derived_data"])
            self.assertIn("runs/", payload["role_candidates"]["run_evidence"])
            self.assertIn(".tmp/", payload["temporary_candidates_not_deletion_approval"])
            rendered = json.dumps(payload, ensure_ascii=False)
            self.assertNotIn("TOKEN=do-not-read", rendered)

    def test_default_cli_is_read_only_json(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            before = sorted(path.relative_to(project) for path in project.rglob("*"))
            stream = io.StringIO()
            with redirect_stdout(stream):
                result = inventory.main([str(project), "--compact"])
            payload = json.loads(stream.getvalue())
            after = sorted(path.relative_to(project) for path in project.rglob("*"))
            self.assertEqual(result, 0)
            self.assertEqual(payload["schema_version"], inventory.SCHEMA_VERSION)
            self.assertEqual(before, after)

    def test_explicit_output_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            project = self.make_project(root)
            output = root / "inventory.json"
            self.assertEqual(inventory.main([str(project), "--output", str(output)]), 0)
            self.assertTrue(output.exists())
            self.assertEqual(inventory.main([str(project), "--output", str(output)]), 2)


if __name__ == "__main__":
    unittest.main()
