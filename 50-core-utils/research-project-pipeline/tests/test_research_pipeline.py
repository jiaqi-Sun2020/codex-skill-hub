from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import hashlib
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

    def make_policy_topology(
        self,
        project: Path,
        *,
        include_reference: bool = True,
        approve_semantics: bool = True,
    ) -> Path:
        root_bundle = project / ".agents"
        root_bundle.mkdir(exist_ok=True)
        root_agents = root_bundle / "AGENTS.md"
        if not root_agents.exists():
            root_agents.write_text("# Root instructions\n", encoding="utf-8")
        policy = root_bundle / "MANDATORY_POLICY.md"
        policy.write_text("# Mandatory policy\n\nPreserve evidence.\n", encoding="utf-8")
        nested_bundle = project / "nested" / ".agents"
        nested_bundle.mkdir(parents=True)
        reference = "Load `../.agents/MANDATORY_POLICY.md`.\n" if include_reference else "No parent policy.\n"
        (nested_bundle / "AGENTS.md").write_text("# Nested\n\n" + reference, encoding="utf-8")
        binding = {
            "execution_root_id": "nested",
            "policy_id": "mandatory",
            "type": "explicit_reference",
            "non_weakening": True,
        }
        if approve_semantics:
            binding["semantic_review"] = {
                "status": "approved",
                "reviewer": "owner",
                "reviewed_at": "2026-09-14",
            }
        manifest = root_bundle / "policy-topology.json"
        manifest.write_text(
            json.dumps(
                {
                    "schema_version": pipeline.POLICY_TOPOLOGY_SCHEMA,
                    "execution_roots": [
                        {"id": "root", "path": "."},
                        {"id": "nested", "path": "nested"},
                    ],
                    "policies": [
                        {
                            "id": "mandatory",
                            "path": ".agents/MANDATORY_POLICY.md",
                            "sha256": hashlib.sha256(policy.read_bytes()).hexdigest(),
                            "mandatory": True,
                            "applies_to": ["nested"],
                        }
                    ],
                    "bindings": [binding],
                }
            ),
            encoding="utf-8",
        )
        return manifest

    def make_equivalence_records(self, project: Path) -> Path:
        records = project / "equivalence-records.json"
        records.write_text(
            json.dumps(
                {
                    "schema_version": pipeline.EQUIVALENCE_SCHEMA,
                    "records": [
                        {
                            "id": "metric-check",
                            "type": "metric_only",
                            "scope": {"metric": "score"},
                            "evidence": [{"external_id": "domain-run-1", "content_sha256": "a" * 64}],
                            "comparison_method": {"name": "metric-test", "result": "pass"},
                            "tolerance": 1e-9,
                            "invalidation_keys": {"implementation": "abc"},
                            "allowed_use": ["metric_comparison"],
                            "forbidden_inference": [
                                "matrix_identity",
                                "matrix_equivalence_up_to_global_phase",
                                "observational_interchangeability",
                                "deduplicate_operator_evidence",
                                "deduplicate_observation_evidence",
                            ],
                            "status": "verified",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        return records

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

    def test_nested_execution_root_without_manifest_is_conditional(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            (project / "nested" / ".agents").mkdir(parents=True)
            (project / "nested" / ".agents" / "AGENTS.md").write_text(
                "# Nested\n", encoding="utf-8"
            )
            before = sorted(path.relative_to(project) for path in project.rglob("*"))
            report = pipeline.analyze_policy_topology(project, None)
            after = sorted(path.relative_to(project) for path in project.rglob("*"))
            self.assertEqual(report["status"], "conditional")
            self.assertEqual(report["summary"]["execution_root_count"], 2)
            self.assertIn("policy-declaration-missing", {item["code"] for item in report["findings"]})
            self.assertEqual(before, after)

    def test_explicit_nested_policy_reference_can_be_verified(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            manifest = self.make_policy_topology(project)
            report = pipeline.analyze_policy_topology(
                project,
                manifest.relative_to(project).as_posix(),
            )
            self.assertEqual(report["status"], "verified", report)
            self.assertEqual(report["bindings"][0]["status"], "verified")

    def test_missing_nested_policy_reference_is_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            manifest = self.make_policy_topology(project, include_reference=False)
            report = pipeline.analyze_policy_topology(
                project,
                manifest.relative_to(project).as_posix(),
            )
            self.assertEqual(report["status"], "invalid")
            self.assertIn("mandatory-policy-unreachable", {item["code"] for item in report["findings"]})

    def test_unreviewed_non_weakening_is_conditional(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            manifest = self.make_policy_topology(project, approve_semantics=False)
            report = pipeline.analyze_policy_topology(
                project,
                manifest.relative_to(project).as_posix(),
            )
            self.assertEqual(report["status"], "conditional")
            self.assertIn("semantic-non-weakening-review-required", {item["code"] for item in report["findings"]})

    def test_verified_loader_evidence_is_bound_to_root_and_policy(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            manifest = self.make_policy_topology(project)
            loader = project / ".agents" / "policy-loader.py"
            evidence = project / ".agents" / "loader-test.json"
            loader.write_text("# verified loader\n", encoding="utf-8")
            evidence.write_text('{"result":"pass"}\n', encoding="utf-8")
            document = json.loads(manifest.read_text(encoding="utf-8"))
            document["bindings"] = [
                {
                    "execution_root_id": "nested",
                    "policy_id": "mandatory",
                    "type": "verified_loader",
                    "loader_path": ".agents/policy-loader.py",
                    "loader_sha256": hashlib.sha256(loader.read_bytes()).hexdigest(),
                    "verification_evidence": {
                        "path": ".agents/loader-test.json",
                        "sha256": hashlib.sha256(evidence.read_bytes()).hexdigest(),
                        "result": "pass",
                        "covers_execution_root_id": "nested",
                        "covers_policy_id": "mandatory",
                    },
                }
            ]
            manifest.write_text(json.dumps(document), encoding="utf-8")
            report = pipeline.analyze_policy_topology(project, manifest.relative_to(project).as_posix())
            self.assertEqual(report["status"], "verified", report)

            document["bindings"][0]["verification_evidence"]["covers_policy_id"] = "another-policy"
            manifest.write_text(json.dumps(document), encoding="utf-8")
            report = pipeline.analyze_policy_topology(project, manifest.relative_to(project).as_posix())
            self.assertEqual(report["status"], "invalid")
            self.assertIn("loader-evidence-scope-mismatch", {item["code"] for item in report["findings"]})

    def test_owner_approved_isolation_remains_visible_and_conditional(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            manifest = self.make_policy_topology(project)
            document = json.loads(manifest.read_text(encoding="utf-8"))
            document["bindings"] = [
                {
                    "execution_root_id": "nested",
                    "policy_id": "mandatory",
                    "type": "owner_approved_isolation",
                    "approval": {
                        "owner": "owner",
                        "approved_at": "2026-09-14",
                        "rationale": "This root runs a separately reviewed protocol.",
                    },
                }
            ]
            manifest.write_text(json.dumps(document), encoding="utf-8")
            report = pipeline.analyze_policy_topology(project, manifest.relative_to(project).as_posix())
            self.assertEqual(report["status"], "conditional")
            self.assertIn("owner-approved-isolation", {item["code"] for item in report["findings"]})

    def test_policy_hash_mismatch_and_drifted_copy_are_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            manifest = self.make_policy_topology(project)
            document = json.loads(manifest.read_text(encoding="utf-8"))
            document["policies"][0]["sha256"] = "0" * 64
            document["policies"][0]["known_copies"] = [
                "nested/.agents/MANDATORY_POLICY.md"
            ]
            manifest.write_text(json.dumps(document), encoding="utf-8")
            (project / "nested" / ".agents" / "MANDATORY_POLICY.md").write_text(
                "# Drifted\n", encoding="utf-8"
            )
            report = pipeline.analyze_policy_topology(project, manifest.relative_to(project).as_posix())
            codes = {item["code"] for item in report["findings"]}
            self.assertIn("policy-hash-mismatch", codes)
            self.assertIn("duplicated-policy-drift", codes)
            self.assertEqual(report["summary"]["exit_code"], 2)

    def test_policy_path_outside_project_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            manifest = self.make_policy_topology(project)
            document = json.loads(manifest.read_text(encoding="utf-8"))
            document["policies"][0]["path"] = "../outside-policy.md"
            manifest.write_text(json.dumps(document), encoding="utf-8")
            report = pipeline.analyze_policy_topology(project, manifest.relative_to(project).as_posix())
            self.assertIn("policy-path-outside-project", {item["code"] for item in report["findings"]})
            self.assertEqual(report["status"], "invalid")

    def test_topology_cannot_hide_mandatory_semantics_by_omission(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            manifest = self.make_policy_topology(project)
            document = json.loads(manifest.read_text(encoding="utf-8"))
            del document["policies"][0]["mandatory"]
            manifest.write_text(json.dumps(document), encoding="utf-8")
            report = pipeline.analyze_policy_topology(project, manifest.relative_to(project).as_posix())
            self.assertEqual(report["status"], "invalid")
            self.assertIn("invalid-policy-mandatory", {item["code"] for item in report["findings"]})

    def test_verify_preserves_structured_findings_for_invalid_topology(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            manifest = self.make_policy_topology(project)
            document = json.loads(manifest.read_text(encoding="utf-8"))
            document["policies"] = []
            manifest.write_text(json.dumps(document), encoding="utf-8")
            code, stdout, stderr = self.run_main([
                "verify",
                str(project),
                "--policy-topology",
                manifest.relative_to(project).as_posix(),
                "--compact",
            ])
            self.assertEqual(code, 2, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["status"], "fail")
            self.assertEqual(payload["policy_topology"]["status"], "invalid")
            self.assertEqual(
                payload["knowledge_and_bootstrap"]["policy_topology_audit"],
                "skipped_invalid_pipeline_topology",
            )

    def test_plan_includes_verified_policy_and_equivalence_extensions(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            manifest = self.make_policy_topology(project)
            records = self.make_equivalence_records(project)
            before = {path.relative_to(project).as_posix(): path.stat().st_mtime_ns for path in project.rglob("*")}
            code, stdout, stderr = self.run_main([
                "plan",
                str(project),
                "--policy-topology",
                manifest.relative_to(project).as_posix(),
                "--equivalence-records",
                records.relative_to(project).as_posix(),
                "--compact",
            ])
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["policy_topology"]["status"], "verified")
            self.assertEqual(payload["equivalence_contracts"]["status"], "verified")
            self.assertEqual(payload["plan_sha256"], pipeline.canonical_hash(payload))
            after = {path.relative_to(project).as_posix(): path.stat().st_mtime_ns for path in project.rglob("*")}
            self.assertEqual(before, after)

    def test_equivalence_records_must_be_project_contained(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            project = self.make_project(root)
            outside = root / "outside-records.json"
            outside.write_text(json.dumps({"schema_version": pipeline.EQUIVALENCE_SCHEMA, "records": []}), encoding="utf-8")
            code, stdout, stderr = self.run_main([
                "plan", str(project), "--equivalence-records", str(outside), "--compact"
            ])
            self.assertEqual(code, 2)
            self.assertEqual(stdout, "")
            self.assertIn("must stay inside", stderr)


if __name__ == "__main__":
    unittest.main()
