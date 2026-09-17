from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "research_pipeline.py"
DOMAIN_AUDITOR = SCRIPT.parents[2] / "experiment-protocol-audit" / "scripts" / "audit_experiment_protocol.py"
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
        self.assertEqual(response["outcome"], "plan_written")
        self.assertEqual(response["command_status"], "ok")
        self.assertEqual(response["schema_version"], pipeline.PIPELINE_RESULT_SCHEMA)
        self.assertEqual(response["document_type"], "pipeline-command-result")
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
                    "schema_version": "research-policy-topology/v1",
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

    def make_comparison_records(self, project: Path) -> Path:
        records = project / "comparison-records.json"
        records.write_text(
            json.dumps(
                {
                    "schema_version": pipeline.COMPARISON_SCHEMA,
                    "records": [
                        {
                            "id": "comparison-check",
                            "type": "domain.example/relation-v1",
                            "scope": {"items": ["a", "b"]},
                            "evidence": [{"external_id": "review-package-1", "content_sha256": "a" * 64}],
                            "comparison_method": {"name": "domain-procedure", "result": "pass"},
                            "tolerance": {"name": "domain-defined", "value": "accepted"},
                            "invalidation_keys": {"input_revision": "abc"},
                            "allowed_use": ["named-downstream-use"],
                            "forbidden_inference": ["broader-unsupported-claim"],
                            "domain_review": {
                                "status": "approved",
                                "reviewer": "owner",
                                "reviewed_at": "2026-09-15",
                            },
                            "status": "verified",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        return records

    def make_domain_record(self, project: Path) -> Path:
        (project / "domain-profile.json").write_text(json.dumps({
            "schema_version": "experiment-domain-profile/v1",
            "profile_id": "example-domain",
            "version": "1.0.0",
            "rules": [{"id": "positive", "type": "numeric-bound", "input_path": "value", "operator": ">", "expected": 0}],
        }), encoding="utf-8")
        (project / "project-protocol.json").write_text(json.dumps({
            "schema_version": "experiment-project-protocol/v1",
            "protocol_id": "example-protocol",
            "version": "1.0.0",
            "profile_id": "example-domain",
            "owner": {"kind": "human", "id": "domain-reviewer"},
            "claim_ceiling": "diagnostic_only",
            "source_paths": ["src/analysis.py"],
        }), encoding="utf-8")
        (project / "domain-observations.json").write_text(json.dumps({
            "schema_version": "experiment-runtime-observation/v1",
            "observations": {"value": 1},
        }), encoding="utf-8")
        record = project / "domain-record.json"
        process = subprocess.run([
            sys.executable, "-B", str(DOMAIN_AUDITOR), "audit-design", str(project),
            "--profile", "domain-profile.json", "--protocol", "project-protocol.json",
            "--observations", "domain-observations.json", "--output", "domain-record.json", "--compact",
        ], capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        self.assertEqual(process.returncode, 0, process.stderr)
        return record

    def test_plan_is_read_only_and_hash_bound(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            before = sorted(path.relative_to(project) for path in project.rglob("*"))
            code, stdout, stderr = self.run_main([
                "plan", str(project), "--profile", "minimal", "--compact"
            ])
            payload = json.loads(stdout)
            after = sorted(path.relative_to(project) for path in project.rglob("*"))
            self.assertEqual(code, 0, stderr)
            self.assertEqual(payload["schema_version"], pipeline.PIPELINE_PLAN_SCHEMA)
            self.assertEqual(payload["document_type"], "pipeline-plan")
            self.assertEqual(payload["plan_sha256"], pipeline.canonical_hash(payload))
            self.assertEqual(payload["context_action"], "create_after_framework")
            self.assertEqual(before, after)
            self.assertFalse((project / ".agents").exists())
            self.assertEqual(payload["governance_layout"]["status"], "absent")
            schema = json.loads(
                (SCRIPT.parents[1] / "references" / "pipeline-plan.schema.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(
                schema["properties"]["schema_version"]["const"],
                pipeline.PIPELINE_PLAN_SCHEMA,
            )
            self.assertTrue(set(schema["required"]).issubset(payload))
            self.assertEqual(payload["review_gate_inputs"]["result"], "conditional")
            self.assertEqual(
                payload["review_gate_inputs"]["human_summary_language"],
                "current-user-language",
            )
            source = payload["review_gate_inputs"]["human_summary_source"]
            self.assertTrue(set(pipeline.HUMAN_SUMMARY_FIELDS).issubset(source))
            for field in pipeline.HUMAN_SUMMARY_FIELDS:
                self.assertTrue(source[field])
            self.assertIn("generator", payload["component_bindings"])
            self.assertEqual(payload["relocation_maps"]["status"], "not_checked")

    def test_legacy_lightweight_profile_normalizes_to_minimal(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            code, stdout, stderr = self.run_main([
                "plan", str(project), "--profile", "lightweight", "--compact"
            ])
            self.assertEqual(code, 0, stderr)
            self.assertEqual(json.loads(stdout)["profile"], "minimal")

    def test_legacy_inventory_is_readable_but_cannot_authorize_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw)).resolve()
            legacy_payload = {
                "schema_version": pipeline.LEGACY_INVENTORY_SCHEMA,
                "status": "inspected",
                "project_root": str(project),
                "workspace_fingerprint_sha256": "a" * 64,
                "role_candidates": {"experiments_analyses": ["work/"]},
                "scan": {"scan_truncated": False, "unreadable_count": 0},
            }
            completed = pipeline.subprocess.CompletedProcess(
                args=[], returncode=0, stdout=json.dumps(legacy_payload), stderr=""
            )
            with mock.patch.object(pipeline, "run_process", return_value=completed):
                inspected = pipeline.inspect_workspace(project, Path("inventory-v1.py"))
            self.assertEqual(inspected["source_schema_version"], pipeline.LEGACY_INVENTORY_SCHEMA)
            self.assertEqual(inspected["governance_layout"]["status"], "unsafe")
            self.assertFalse(inspected["governance_layout"]["write_allowed"])
            self.assertEqual(inspected["role_candidates"]["work_units"], ["work/"])

    def test_legacy_plans_cannot_be_applied(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            project = self.make_project(root).resolve()
            for index, schema in enumerate(sorted(pipeline.LEGACY_PIPELINE_SCHEMAS)):
                plan_path = root / f"legacy-plan-{index}.json"
                plan_path.write_text(
                    json.dumps({"schema_version": schema}),
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(ValueError, "cannot authorize mutation"):
                    pipeline.load_and_validate_plan(plan_path, project, "0" * 64)

    def test_hash_valid_but_structurally_incomplete_plan_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            project = self.make_project(root).resolve()
            plan_path = root / "reviewed-plan.json"
            plan = self.write_plan(project, plan_path)
            plan.pop("component_actions")
            plan["plan_sha256"] = pipeline.canonical_hash(plan)
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing required fields"):
                pipeline.load_and_validate_plan(
                    plan_path, project, plan["plan_sha256"]
                )

    def test_hash_valid_plan_cannot_hide_component_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            project = self.make_project(root).resolve()
            (project / ".agents" / "governance").mkdir(parents=True)
            (project / "governance").mkdir()
            plan_path = root / "reviewed-plan.json"
            plan = self.write_plan(project, plan_path)
            self.assertTrue(plan["review_gate_inputs"]["blockers"])
            plan["review_gate_inputs"]["blockers"] = []
            plan["review_gate_inputs"]["result"] = "conditional"
            plan["plan_sha256"] = pipeline.canonical_hash(plan)
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "blockers do not match"):
                pipeline.load_and_validate_plan(
                    plan_path, project, plan["plan_sha256"]
                )

    def test_project_root_link_or_junction_is_rejected_before_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            with mock.patch.object(
                pipeline, "first_link_component", return_value=project
            ):
                with self.assertRaisesRegex(ValueError, "link or junction"):
                    pipeline.resolve_project_root(str(project))

    def test_plan_propagates_governance_ambiguity_without_guessing(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            (project / ".agents" / "governance").mkdir(parents=True)
            (project / "governance").mkdir()
            code, stdout, stderr = self.run_main([
                "plan", str(project), "--profile", "minimal", "--compact"
            ])
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["governance_layout"]["status"], "ambiguous")
            design = next(stage for stage in payload["stages"] if stage["name"] == "design")
            self.assertEqual(design["status"], "blocked")
            self.assertEqual(payload["review_gate_inputs"]["result"], "fail")
            self.assertIn(
                "multiple-governance-locations",
                {item["code"] for item in payload["review_gate_inputs"]["blockers"]},
            )

    def test_bootstrap_refuses_plan_with_unsafe_governance_location(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            project = self.make_project(root)
            (project / "governance").write_text("not a directory\n", encoding="utf-8")
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
            self.assertEqual(code, 2)
            self.assertEqual(stdout, "")
            self.assertIn("blocking governance-location", stderr)
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
            payload = json.loads(stdout)
            self.assertEqual(payload["outcome"], "context_created")
            self.assertEqual(payload["initialization_status"], "complete")
            self.assertEqual(payload["maintenance_owner"], "neat-freak")
            self.assertTrue((project / ".agents" / "AGENTS.md").is_file())
            self.assertTrue((project / ".agents" / "memory" / "MEMORY.md").is_file())
            self.assertTrue((project / ".codex" / "hooks.json").is_file())

    def test_component_swap_is_rejected_before_write(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            project = self.make_project(root)
            plan_path = root / "reviewed-plan.json"
            plan = self.write_plan(project, plan_path)
            fake_generator = root / "fake-generator.py"
            fake_generator.write_text("raise SystemExit('must not execute')\n", encoding="utf-8")
            code, stdout, stderr = self.run_main([
                "--generator-script",
                str(fake_generator),
                "bootstrap-agents",
                str(project),
                "--apply",
                "--plan",
                str(plan_path),
                "--confirm-plan-sha256",
                plan["plan_sha256"],
                "--compact",
            ])
            self.assertEqual(code, 2)
            self.assertEqual(stdout, "")
            self.assertIn("differs from the reviewed plan", stderr)
            self.assertFalse((project / ".agents").exists())

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
            self.assertEqual(json.loads(stdout)["outcome"], "context_preview")
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
            payload = json.loads(stdout)
            self.assertEqual(payload["outcome"], "existing_context_preserved")
            self.assertEqual(payload["maintenance_owner"], "neat-freak")
            self.assertIn("Neat-Freak", payload["message"])
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
            self.assertEqual(payload["outcome"], "existing_context_preserved")
            self.assertEqual(payload["maintenance_owner"], "neat-freak")
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
            self.assertEqual(payload["outcome"], "verification_complete")
            self.assertEqual(payload["readiness"]["onboarding_state"], "conditional")
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
            self.assertEqual(payload["outcome"], "verification_complete")
            self.assertEqual(payload["readiness"]["onboarding_state"], "conditional")
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
            self.assertEqual(payload["outcome"], "verification_complete")
            self.assertIn(payload["readiness"]["onboarding_state"], {"ready", "conditional"})
            self.assertEqual(payload["mode"], "read-only-verification")
            self.assertEqual(before, after)

    def test_pipeline_invokes_neat_freak_only_in_audit_modes(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            self.make_context_bundle(project, ".agents")
            audit_result = {
                "exit_code": 0,
                "result": {"summary": {"exit_code": 0, "status": "clean"}},
            }
            with mock.patch.object(
                pipeline, "run_knowledge_audit", return_value=audit_result
            ) as delegated:
                code, _stdout, stderr = self.run_main([
                    "verify", str(project), "--compact"
                ])
            self.assertIn(code, {0, 1}, stderr)
            modes = {call.args[2] for call in delegated.call_args_list}
            self.assertEqual(modes, {"audit", "bootstrap-audit"})

    def test_pipeline_does_not_parse_agent_loading_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            manifest = project / "agent-loading-manifest.json"
            manifest.write_text("this is intentionally not JSON\n", encoding="utf-8")
            code, stdout, stderr = self.run_main([
                "plan",
                str(project),
                "--policy-topology",
                manifest.relative_to(project).as_posix(),
                "--compact",
            ])
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            handoff = payload["agent_loading_audit_handoff"]
            self.assertEqual(handoff["owner"], "neat-freak")
            self.assertEqual(handoff["status"], "pending_neat_freak_audit")
            self.assertNotIn("policy_topology", payload)

    def test_verify_delegates_loading_manifest_to_neat_freak(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            self.make_context_bundle(project, ".agents")
            manifest = project / ".agents" / "policy-topology.json"
            manifest.write_text("content owned by neat-freak\n", encoding="utf-8")
            calls: list[tuple[str, str | None]] = []

            def fake_audit(
                project_arg: Path,
                script: Path,
                mode: str,
                memory_directory: str,
                policy_topology: str | None = None,
            ) -> dict:
                self.assertEqual(project_arg, project.resolve())
                calls.append((mode, policy_topology))
                return {"exit_code": 0, "result": {"status": "pass"}}

            with mock.patch.object(pipeline, "run_knowledge_audit", side_effect=fake_audit):
                code, stdout, stderr = self.run_main([
                    "verify",
                    str(project),
                    "--policy-topology",
                    manifest.relative_to(project).as_posix(),
                    "--compact",
                ])
            self.assertIn(code, {0, 1}, stderr)
            payload = json.loads(stdout)
            self.assertIn(
                ("bootstrap-audit", manifest.relative_to(project).as_posix()),
                calls,
            )
            self.assertEqual(
                payload["knowledge_and_bootstrap"]["policy_topology_audit"],
                "executed",
            )

    def test_agent_loading_manifest_must_be_project_contained(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            project = self.make_project(root)
            outside = root / "outside-agent-loading.json"
            outside.write_text("{}\n", encoding="utf-8")
            code, stdout, stderr = self.run_main([
                "plan", str(project), "--policy-topology", str(outside), "--compact"
            ])
            self.assertEqual(code, 2)
            self.assertEqual(stdout, "")
            self.assertIn("must stay inside", stderr)

    def test_plan_includes_loading_handoff_and_verified_comparison(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            manifest = self.make_policy_topology(project)
            records = self.make_comparison_records(project)
            before = {path.relative_to(project).as_posix(): path.stat().st_mtime_ns for path in project.rglob("*")}
            code, stdout, stderr = self.run_main([
                "plan",
                str(project),
                "--policy-topology",
                manifest.relative_to(project).as_posix(),
                "--comparison-records",
                records.relative_to(project).as_posix(),
                "--compact",
            ])
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(
                payload["agent_loading_audit_handoff"]["status"],
                "pending_neat_freak_audit",
            )
            self.assertEqual(payload["agent_loading_audit_handoff"]["owner"], "neat-freak")
            self.assertEqual(payload["comparison_contracts"]["status"], "verified")
            self.assertEqual(payload["plan_sha256"], pipeline.canonical_hash(payload))
            after = {path.relative_to(project).as_posix(): path.stat().st_mtime_ns for path in project.rglob("*")}
            self.assertEqual(before, after)

    def test_comparison_records_must_be_project_contained(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            project = self.make_project(root)
            outside = root / "outside-records.json"
            outside.write_text(json.dumps({"schema_version": pipeline.COMPARISON_SCHEMA, "records": []}), encoding="utf-8")
            code, stdout, stderr = self.run_main([
                "plan", str(project), "--comparison-records", str(outside), "--compact"
            ])
            self.assertEqual(code, 2)
            self.assertEqual(stdout, "")
            self.assertIn("must stay inside", stderr)

    def test_domain_validation_is_a_scoped_axis_not_an_onboarding_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            code, stdout, stderr = self.run_main([
                "plan", str(project), "--domain-validation", "required", "--compact"
            ])
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["domain_validation_handoff"]["effective_state"], "not_declared")
            self.assertEqual(payload["readiness"]["domain_validation_state"], "not_declared")
            self.assertEqual(payload["readiness"]["execution_state"], "not_authorized")
            self.assertEqual(payload["readiness"]["claim_state"], "unsupported")
            self.assertNotIn("domain-validation-not-declared", {item.get("code") for item in payload["review_gate_inputs"]["blockers"]})
            self.assertIn("domain-validation-not-declared", {item.get("code") for item in payload["review_gate_inputs"]["non_blockers"]})
            self.assertNotEqual(payload.get("status"), "pass")

    def test_not_applicable_requires_and_records_a_named_owner(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            code, stdout, stderr = self.run_main([
                "plan", str(project), "--domain-validation", "not-applicable", "--compact"
            ])
            self.assertEqual(code, 0, stderr)
            unresolved = json.loads(stdout)["domain_validation_handoff"]
            self.assertEqual(unresolved["effective_state"], "not_declared")

            code, stdout, stderr = self.run_main([
                "plan", str(project), "--domain-validation", "not-applicable",
                "--domain-validation-owner", "principal-investigator", "--compact",
            ])
            self.assertEqual(code, 0, stderr)
            handoff = json.loads(stdout)["domain_validation_handoff"]
            self.assertEqual(handoff["effective_state"], "not_applicable")
            self.assertEqual(handoff["owner"], {"kind": "human", "id": "principal-investigator"})
            self.assertEqual(handoff["claim_ceiling"], "unsupported")

    def test_current_domain_record_is_verified_and_hash_bound(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            record = self.make_domain_record(project)
            code, stdout, stderr = self.run_main([
                "plan", str(project), "--domain-validation", "required",
                "--domain-validation-record", record.relative_to(project).as_posix(), "--compact",
            ])
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            handoff = payload["domain_validation_handoff"]
            self.assertEqual(handoff["effective_state"], "verified")
            self.assertEqual(handoff["claim_ceiling"], "diagnostic_only")
            self.assertEqual(payload["readiness"]["claim_state"], "diagnostic_only")
            self.assertEqual(handoff["validator"]["sha256"], pipeline.sha256_file(DOMAIN_AUDITOR))
            pipeline.validate_plan_structure(payload)

    def test_domain_record_becomes_stale_when_source_changes(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            record = self.make_domain_record(project)
            (project / "src" / "analysis.py").write_text("print('changed')\n", encoding="utf-8")
            code, stdout, stderr = self.run_main([
                "plan", str(project), "--domain-validation", "required",
                "--domain-validation-record", record.relative_to(project).as_posix(), "--compact",
            ])
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["domain_validation_handoff"]["effective_state"], "stale")
            self.assertEqual(payload["readiness"]["claim_state"], "unsupported")
            self.assertIn("domain-validation-evidence-stale", {item["code"] for item in payload["domain_validation_handoff"]["findings"]})

    def test_forged_verified_record_with_blocker_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            record = self.make_domain_record(project)
            payload = json.loads(record.read_text(encoding="utf-8"))
            payload["findings"] = [{"code": "unresolved-domain-defect", "severity": "blocker"}]
            record.write_text(json.dumps(payload), encoding="utf-8")
            code, stdout, stderr = self.run_main([
                "plan", str(project), "--domain-validation", "required",
                "--domain-validation-record", record.relative_to(project).as_posix(), "--compact",
            ])
            self.assertEqual(code, 0, stderr)
            handoff = json.loads(stdout)["domain_validation_handoff"]
            self.assertEqual(handoff["effective_state"], "invalid")
            self.assertIn("domain-validation-status-conflict", {item["code"] for item in handoff["findings"]})

    def test_domain_record_must_be_project_contained(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            project = self.make_project(root)
            outside = root / "domain-record.json"
            outside.write_text("{}\n", encoding="utf-8")
            code, stdout, stderr = self.run_main([
                "plan", str(project), "--domain-validation-record", str(outside), "--compact"
            ])
            self.assertEqual(code, 2)
            self.assertEqual(stdout, "")
            self.assertIn("must stay inside", stderr)

    def test_component_discovery_separates_project_build_and_reusable_core(self) -> None:
        args = pipeline.parse_args(["plan", str(Path.cwd())])
        components = pipeline.resolve_components(args)
        self.assertIn("20-project-build", str(components["generator"]))
        self.assertIn("20-project-build", str(components["domain_validator"]))
        self.assertIn("50-core-utils", str(components["knowledge"]))


if __name__ == "__main__":
    unittest.main()
