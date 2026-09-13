from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "research_pipeline.py"
SPEC = importlib.util.spec_from_file_location("research_pipeline", SCRIPT)
assert SPEC and SPEC.loader
pipeline = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = pipeline
SPEC.loader.exec_module(pipeline)


class ResearchPipelineTests(unittest.TestCase):
    def make_project(self, parent: Path) -> Path:
        project = parent / "legacy-research"
        (project / "data" / "raw").mkdir(parents=True)
        (project / "src").mkdir()
        (project / "README.md").write_text("# Legacy research\n", encoding="utf-8")
        (project / "src" / "analysis.py").write_text("print('ok')\n", encoding="utf-8")
        (project / "data" / "raw" / "source.csv").write_text("x\n1\n", encoding="utf-8")
        return project

    def make_context_bundle(self, project: Path, name: str) -> Path:
        bundle = project / name
        for relative in pipeline.REQUIRED_AGENT_FILES:
            target = bundle / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f"# {relative}\n", encoding="utf-8")
        return bundle

    def run_main(self, arguments: list[str]) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = pipeline.main(arguments)
        return code, stdout.getvalue(), stderr.getvalue()

    def write_plan(self, project: Path, destination: Path) -> dict:
        code, stdout, stderr = self.run_main([
            "plan",
            str(project),
            "--profile",
            "collaborative",
            "--output",
            str(destination),
            "--compact",
        ])
        self.assertEqual(code, 0, stderr)
        response = json.loads(stdout)
        self.assertEqual(response["status"], "plan_written")
        return json.loads(destination.read_text(encoding="utf-8"))

    def test_plan_is_read_only_and_hash_bound(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            before = sorted(path.relative_to(project) for path in project.rglob("*"))
            code, stdout, stderr = self.run_main([
                "plan", str(project), "--profile", "lightweight", "--compact"
            ])
            payload = json.loads(stdout)
            after = sorted(path.relative_to(project) for path in project.rglob("*"))
            self.assertEqual(code, 0, stderr)
            self.assertEqual(payload["schema_version"], pipeline.PIPELINE_SCHEMA)
            self.assertEqual(payload["plan_sha256"], pipeline.canonical_hash(payload))
            self.assertEqual(payload["context_action"], "create_after_framework")
            self.assertEqual(before, after)
            self.assertFalse((project / ".agents").exists())

    def test_confirmed_current_plan_can_create_missing_context(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            project = self.make_project(root)
            plan_path = root / "reviewed-plan.json"
            plan = self.write_plan(project, plan_path)
            code, stdout, stderr = self.run_main([
                "bootstrap-agents",
                str(project),
                "--apply",
                "--plan",
                str(plan_path),
                "--confirm-plan-sha256",
                plan["plan_sha256"],
                "--compact",
            ])
            self.assertEqual(code, 0, stderr)
            self.assertEqual(json.loads(stdout)["status"], "context_created")
            self.assertTrue((project / ".agents" / "AGENTS.md").is_file())
            self.assertTrue((project / ".agents" / "memory" / "MEMORY.md").is_file())
            self.assertTrue((project / ".codex" / "hooks.json").is_file())

    def test_preview_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            before = {
                path.relative_to(project).as_posix(): path.stat().st_mtime_ns
                for path in project.rglob("*")
            }
            code, stdout, stderr = self.run_main([
                "bootstrap-agents", str(project), "--compact"
            ])
            after = {
                path.relative_to(project).as_posix(): path.stat().st_mtime_ns
                for path in project.rglob("*")
            }
            self.assertEqual(code, 0, stderr)
            self.assertEqual(json.loads(stdout)["status"], "context_preview")
            self.assertEqual(before, after)
            self.assertFalse((project / ".agents").exists())

    def test_changed_project_invalidates_plan_before_write(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            project = self.make_project(root)
            plan_path = root / "reviewed-plan.json"
            plan = self.write_plan(project, plan_path)
            (project / "new-evidence.txt").write_text("changed\n", encoding="utf-8")
            code, stdout, stderr = self.run_main([
                "bootstrap-agents",
                str(project),
                "--apply",
                "--plan",
                str(plan_path),
                "--confirm-plan-sha256",
                plan["plan_sha256"],
            ])
            self.assertEqual(code, 2)
            self.assertEqual(stdout, "")
            self.assertIn("project changed since the reviewed plan", stderr)
            self.assertFalse((project / ".agents").exists())

    def test_existing_context_is_preserved_even_with_apply(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            agents = project / ".agents"
            agents.mkdir()
            sentinel = agents / "OWNER.md"
            sentinel.write_text("preserve\n", encoding="utf-8")
            code, stdout, stderr = self.run_main([
                "bootstrap-agents", str(project), "--apply", "--compact"
            ])
            self.assertEqual(code, 1, stderr)
            self.assertEqual(json.loads(stdout)["status"], "existing_context_preserved")
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve\n")

    def test_legacy_singular_context_is_preserved_even_with_apply(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            bundle = self.make_context_bundle(project, ".agent")
            sentinel = bundle / "OWNER.md"
            sentinel.write_text("legacy-preserve\n", encoding="utf-8")
            code, stdout, stderr = self.run_main([
                "bootstrap-agents", str(project), "--apply", "--compact"
            ])
            self.assertEqual(code, 1, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["status"], "existing_context_preserved")
            self.assertEqual(payload["context_locations"], [".agent"])
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "legacy-preserve\n")
            self.assertFalse((project / ".agents").exists())

    def test_verify_accepts_singular_context_without_assuming_plural(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            self.make_context_bundle(project, ".agent")
            code, stdout, stderr = self.run_main([
                "verify", str(project), "--compact"
            ])
            self.assertEqual(code, 1, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["status"], "conditional")
            self.assertEqual(payload["context_locations"], [".agent"])
            self.assertEqual(payload["missing_agent_files"], [])

    def test_both_context_names_are_reported_as_ambiguous(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            self.make_context_bundle(project, ".agents")
            self.make_context_bundle(project, ".agent")
            code, stdout, stderr = self.run_main([
                "verify", str(project), "--compact"
            ])
            self.assertEqual(code, 1, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["status"], "conditional")
            self.assertTrue(payload["context_ambiguity"])
            self.assertEqual(payload["context_locations"], [".agents", ".agent"])
            self.assertEqual(
                payload["knowledge_and_bootstrap"]["status"],
                "skipped_context_ambiguity",
            )

    def test_tampered_plan_is_rejected_before_write(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            project = self.make_project(root)
            plan_path = root / "reviewed-plan.json"
            plan = self.write_plan(project, plan_path)
            plan["profile"] = "controlled"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            code, stdout, stderr = self.run_main([
                "bootstrap-agents",
                str(project),
                "--apply",
                "--plan",
                str(plan_path),
                "--confirm-plan-sha256",
                plan["plan_sha256"],
            ])
            self.assertEqual(code, 2)
            self.assertEqual(stdout, "")
            self.assertIn("does not match its embedded hash", stderr)
            self.assertFalse((project / ".agents").exists())

    def test_wrong_confirmation_hash_is_rejected_before_write(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            project = self.make_project(root)
            plan_path = root / "reviewed-plan.json"
            self.write_plan(project, plan_path)
            code, stdout, stderr = self.run_main([
                "bootstrap-agents",
                str(project),
                "--apply",
                "--plan",
                str(plan_path),
                "--confirm-plan-sha256",
                "0" * 64,
            ])
            self.assertEqual(code, 2)
            self.assertEqual(stdout, "")
            self.assertIn("confirmation hash does not match", stderr)
            self.assertFalse((project / ".agents").exists())

    def test_plan_output_inside_project_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            destination = project / "pipeline-plan.json"
            code, stdout, stderr = self.run_main([
                "plan", str(project), "--output", str(destination)
            ])
            self.assertEqual(code, 2)
            self.assertEqual(stdout, "")
            self.assertIn("must be outside the target project", stderr)
            self.assertFalse(destination.exists())

    def test_apply_refuses_a_review_plan_stored_inside_project(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            project = self.make_project(root)
            outside_plan = root / "outside-plan.json"
            plan = self.write_plan(project, outside_plan)
            inside_plan = project / "reviewed-plan.json"
            inside_plan.write_text(outside_plan.read_text(encoding="utf-8"), encoding="utf-8")
            code, stdout, stderr = self.run_main([
                "bootstrap-agents",
                str(project),
                "--apply",
                "--plan",
                str(inside_plan),
                "--confirm-plan-sha256",
                plan["plan_sha256"],
            ])
            self.assertEqual(code, 2)
            self.assertEqual(stdout, "")
            self.assertIn("plan must be outside the target project", stderr)
            self.assertFalse((project / ".agents").exists())

    def test_verify_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            project = self.make_project(root)
            plan_path = root / "reviewed-plan.json"
            plan = self.write_plan(project, plan_path)
            create_code, _, create_stderr = self.run_main([
                "bootstrap-agents",
                str(project),
                "--apply",
                "--plan",
                str(plan_path),
                "--confirm-plan-sha256",
                plan["plan_sha256"],
            ])
            self.assertEqual(create_code, 0, create_stderr)
            before = {
                path.relative_to(project).as_posix(): path.stat().st_mtime_ns
                for path in project.rglob("*")
            }
            code, stdout, stderr = self.run_main([
                "verify", str(project), "--compact"
            ])
            after = {
                path.relative_to(project).as_posix(): path.stat().st_mtime_ns
                for path in project.rglob("*")
            }
            self.assertIn(code, {0, 1}, stderr)
            payload = json.loads(stdout)
            self.assertIn(payload["status"], {"pass", "conditional"})
            self.assertEqual(payload["mode"], "read-only-verification")
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
