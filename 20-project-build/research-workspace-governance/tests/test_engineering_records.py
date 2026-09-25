from __future__ import annotations

import copy
import importlib.util
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_engineering_records.py"
REFERENCES = Path(__file__).resolve().parents[1] / "references"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "engineering-records"
SPEC = importlib.util.spec_from_file_location("validate_engineering_records", SCRIPT)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)

HEX = "a" * 64
OID = "b" * 40


def ref(path: str = "evidence/item.json") -> dict[str, str]:
    return {"path": path, "sha256": HEX}


def rehash(value: dict, field: str) -> dict:
    value[field] = validator.canonical_hash(value, field)
    return value


def make_plan() -> dict:
    plan = {
        "schema_version": validator.PLAN_SCHEMA,
        "plan_id": "plan-001",
        "plan_sha256": HEX,
        "issue_id": "ENG-001",
        "attempt_id": "attempt-001",
        "base_sha": OID,
        "head_sha": OID,
        "worktree_fingerprint_sha256": HEX,
        "code_fingerprint_sha256": HEX,
        "campaign_binding": {"status": "not_applicable", "ref": None, "decision_ref": ref("decisions/campaign-na.json")},
        "profile_binding": {"status": "not_applicable", "ref": None, "decision_ref": ref("decisions/profile-na.json")},
        "stage_id": "repair",
        "predecessor_receipt_ref": None,
        "authorization_ref": ref("decisions/repair.json"),
        "commands": [{"cwd": ".", "argv": ["python", "-c", "print('recorded only')"]}],
        "planned_writes": ["src/fix.py"],
        "protected_paths": ["data/raw"],
        "side_effects": ["modifies one source file"],
        "transaction": {
            "target_identity_sha256": HEX,
            "parent": "outputs",
            "name_prefix": ".txn-r-aaaaaaaaaaaaaaaa-",
            "path_budget": {
                "portable_limit_chars": 259,
                "final_path_chars": 241,
                "legacy_staging_path_chars": 259,
                "staging_path_chars": 80,
                "max_descendant_relative_chars": 100
            },
            "cleanup_conditions": ["exact path created by this attempt"],
            "rollback_conditions": ["authorization remains current"]
        },
        "stop_conditions": ["target drift"],
        "required_verification": ["unit tests"]
    }
    return rehash(plan, "plan_sha256")


def make_receipt(plan: dict) -> dict:
    receipt = {
        "schema_version": validator.RECEIPT_SCHEMA,
        "receipt_id": "receipt-001",
        "receipt_sha256": HEX,
        "supersedes": None,
        "plan_id": plan["plan_id"],
        "plan_sha256": plan["plan_sha256"],
        "issue_id": plan["issue_id"],
        "attempt_id": plan["attempt_id"],
        "stage_id": plan["stage_id"],
        "base_sha": plan["base_sha"],
        "head_sha": plan["head_sha"],
        "worktree_fingerprint_sha256": plan["worktree_fingerprint_sha256"],
        "code_fingerprint_sha256": plan["code_fingerprint_sha256"],
        "operator": {"kind": "agent", "id": "operator-001"},
        "delegation": {
            "task_id": "task-001", "controller_id": "controller-001",
            "requested_plan_sha256": plan["plan_sha256"], "handoff_state": "complete"
        },
        "started_at": "2026-09-25T08:00:00Z",
        "finished_at": "2026-09-25T08:01:00Z",
        "commands": [{
            "cwd": ".", "argv": plan["commands"][0]["argv"], "exit_code": 0,
            "stdout_ref": ref("evidence/stdout.txt"), "stderr_ref": ref("evidence/stderr.txt")
        }],
        "changed_files": [{"path": "src/fix.py", "before_sha256": None, "after_sha256": HEX}],
        "write_reconciliation": {"planned": ["src/fix.py"], "actual": ["src/fix.py"], "unexpected": []},
        "cleanup": "complete", "rollback": "not_needed", "partial_output": "none",
        "commit": {"status": "not_attempted", "object_id": None, "evidence_ref": None},
        "push": {
            "status": "not_attempted", "evidence_ref": None, "remote": None,
            "updates": [], "fast_forward_verified": None, "atomic": None,
            "forced": False, "protection_rejected": False
        },
        "ci": {"status": "not_attempted", "object_id": None, "evidence_ref": None},
        "failure_class": "none", "handoff_state": "complete"
    }
    return rehash(receipt, "receipt_sha256")


def make_repair(plan: dict) -> dict:
    repair = {
        "schema_version": validator.REPAIR_SCHEMA,
        "issue_id": plan["issue_id"], "revision": 1, "supersedes": None, "record_sha256": HEX,
        "title": "Windows transaction path exceeds budget", "classification": "portability",
        "failure_signature": {"code": "winerror-206", "message_sha256": HEX},
        "discovered_at": "2026-09-25T08:00:00Z",
        "source_control": {"base_sha": OID, "head_sha": OID, "branch": "repair/path", "remote": "origin", "remote_ref": "refs/heads/repair/path"},
        "environment": {"os": "windows", "os_version": "11", "runtime": "python-3.11", "filesystem": "ntfs", "cwd": ".", "long_paths_enabled": False},
        "reproduction": {"steps": ["run bounded fixture"], "expected": "publish", "actual": "path reaches 259", "exit_code": 1, "evidence_refs": [ref()]},
        "root_cause": {"summary": "target basename was repeated", "affected_files": ["src/fix.py"], "affected_contracts": ["ENG-02"], "scientific_contract_impact": "none"},
        "invalidation": {"invalidated_gates": ["formal-prepare"], "stale_evidence": [], "required_revalidation": ["windows-ci"]},
        "repair_state": "planned",
        "state_history": [
            {"from": None, "to": "reported", "at": "2026-09-25T08:00:00Z", "actor": "operator", "evidence_refs": [ref()], "decision_ref": None},
            {"from": "reported", "to": "reproduced", "at": "2026-09-25T08:01:00Z", "actor": "operator", "evidence_refs": [ref()], "decision_ref": None},
            {"from": "reproduced", "to": "diagnosed", "at": "2026-09-25T08:02:00Z", "actor": "operator", "evidence_refs": [ref()], "decision_ref": None},
            {"from": "diagnosed", "to": "planned", "at": "2026-09-25T08:03:00Z", "actor": "operator", "evidence_refs": [ref()], "decision_ref": ref("decisions/plan.json")}
        ],
        "run_authorization": {
            "state": "awaiting_authorization", "authorization_ref": None, "evidence_refs": [],
            "state_history": [
                {"from": None, "to": "not_started", "at": "2026-09-25T08:00:00Z", "authorization_ref": None, "execution_receipt_ref": None, "evidence_refs": []},
                {"from": "not_started", "to": "awaiting_authorization", "at": "2026-09-25T08:03:00Z", "authorization_ref": None, "execution_receipt_ref": None, "evidence_refs": []}
            ]
        },
        "plan_ref": {"path": "governance/plan.json", "sha256": plan["plan_sha256"]},
        "authorization": {"state": "not_granted", "authorizer": None, "authorized_at": None, "scope": [], "decision_ref": None},
        "implementation": {"changed_files": [], "commit_sha": None, "execution_receipt_refs": []},
        "verification": {"test_layers": [], "artifact_safety": "not_evaluated", "rollback_strategy": "restore reviewed base", "push_refs": [], "ci_evidence_ref": None},
        "action_boundary": {"allowed_actions": ["review plan"], "forbidden_actions": ["formal prepare", "canary", "full experiment"]},
        "residual_risks": ["network filesystem may reject hard links"], "closure_evidence": None,
        "closed_at": None, "closed_by": None, "blocked_from": None, "blocker": None, "unblock_condition": None
    }
    return rehash(repair, "record_sha256")


def make_ci() -> dict:
    ci = {
        "schema_version": validator.CI_SCHEMA, "evidence_sha256": HEX,
        "repository": "owner/repo", "queried_at": "2026-09-25T08:00:00Z", "head_sha": OID,
        "api_query": {"head_sha": OID, "branch_filter": None, "pages_fetched": 1},
        "pagination_complete": True, "total_count": 1,
        "runs": [{
            "run_id": 1, "head_sha": OID, "head_branch": "repair/path", "event": "push",
            "workflow_id": 7, "workflow_path": ".github/workflows/ci.yml", "run_attempt": 1,
            "status": "completed", "conclusion": "success",
            "jobs": [{"job_id": 2, "name": "windows", "status": "completed", "conclusion": "success", "steps": [{"number": 1, "name": "tests", "status": "completed", "conclusion": "success"}]}]
        }],
        "required_check_policy_ref": ref("governance/required-checks.json"),
        "status": "passed", "supplemental_legacy_statuses": []
    }
    return rehash(ci, "evidence_sha256")


class EngineeringRecordTests(unittest.TestCase):
    def test_reference_schemas_are_valid_json_and_named(self) -> None:
        expected = {
            "engineering-repair-record.schema.json": validator.REPAIR_SCHEMA,
            "engineering-execution-plan.schema.json": validator.PLAN_SCHEMA,
            "engineering-execution-receipt.schema.json": validator.RECEIPT_SCHEMA,
            "github-actions-evidence.schema.json": validator.CI_SCHEMA,
        }
        for name, title in expected.items():
            value = json.loads((REFERENCES / name).read_text(encoding="utf-8"))
            self.assertEqual(value["title"], title)

    def test_schema_validation_rejects_unknown_fields(self) -> None:
        plan = make_plan()
        plan["unexpected_instruction"] = "run me"
        rehash(plan, "plan_sha256")
        codes = {row["code"] for row in validator.validate_plan(plan)}
        self.assertIn("schema-violation", codes)

    def test_valid_records_and_independent_run_state(self) -> None:
        plan = make_plan()
        self.assertEqual(validator.validate_plan(plan), [])
        self.assertEqual(validator.validate_receipt(make_receipt(plan), plan), [])
        repair = make_repair(plan)
        self.assertEqual(repair["repair_state"], "planned")
        self.assertEqual(repair["run_authorization"]["state"], "awaiting_authorization")
        self.assertEqual(validator.validate_repair(repair), [])
        self.assertEqual(validator.validate_ci(make_ci(), OID), [])

    def test_planned_repair_fixture_is_valid(self) -> None:
        record = json.loads((FIXTURES / "planned-repair.json").read_text(encoding="utf-8"))
        self.assertEqual(validator.validate_repair(record), [])

    def test_invalid_state_transition_is_rejected(self) -> None:
        repair = make_repair(make_plan())
        repair["state_history"][-1]["to"] = "fixed"
        repair["repair_state"] = "fixed"
        rehash(repair, "record_sha256")
        codes = {row["code"] for row in validator.validate_repair(repair)}
        self.assertIn("invalid-transition", codes)
        self.assertIn("missing-repair-authorization", codes)

    def test_run_gate_cannot_skip_prepare_or_omit_its_own_receipt(self) -> None:
        repair = make_repair(make_plan())
        repair["run_authorization"]["state"] = "canary_passed"
        repair["run_authorization"]["state_history"].append({
            "from": "awaiting_authorization", "to": "canary_passed",
            "at": "2026-09-25T08:04:00Z", "authorization_ref": None,
            "execution_receipt_ref": None, "evidence_refs": []
        })
        rehash(repair, "record_sha256")
        codes = {row["code"] for row in validator.validate_repair(repair)}
        self.assertIn("invalid-run-transition", codes)
        self.assertIn("missing-stage-authorization", codes)

    def test_plan_receipt_drift_and_partial_cleanup_are_not_valid(self) -> None:
        plan = make_plan()
        receipt = make_receipt(plan)
        receipt["head_sha"] = "c" * 40
        receipt["cleanup"] = "incomplete"
        rehash(receipt, "receipt_sha256")
        findings = validator.validate_receipt(receipt, plan)
        self.assertIn("plan-receipt-mismatch", {row["code"] for row in findings})
        self.assertIn("unsafe-partial-state", {row["code"] for row in findings})
        self.assertEqual(validator.overall(findings), ("stale", 1))

    def test_combined_status_cannot_replace_actions_evidence(self) -> None:
        ci = make_ci()
        ci["runs"] = []
        ci["total_count"] = 0
        ci["supplemental_legacy_statuses"] = [{"state": "success"}]
        rehash(ci, "evidence_sha256")
        codes = {row["code"] for row in validator.validate_ci(ci, OID)}
        self.assertIn("empty-ci-pass", codes)

    def test_actions_accepts_same_sha_across_branches_and_rejects_sha_drift(self) -> None:
        ci = make_ci()
        second = copy.deepcopy(ci["runs"][0])
        second["run_id"] = 3
        second["head_branch"] = "main"
        ci["runs"].append(second)
        ci["total_count"] = 2
        rehash(ci, "evidence_sha256")
        self.assertEqual(validator.validate_ci(ci, OID), [])
        self.assertIn(
            "ci-head-mismatch",
            {row["code"] for row in validator.validate_ci(ci, "c" * 40)},
        )

    def test_force_and_non_atomic_multi_ref_push_are_rejected(self) -> None:
        plan = make_plan()
        receipt = make_receipt(plan)
        receipt["push"] = {
            "status": "succeeded", "evidence_ref": ref("evidence/push.json"), "remote": "origin",
            "updates": [
                {"ref": "refs/heads/a", "remote_before": OID, "remote_after": "c" * 40, "backup_ref": "refs/codex-backup/op/a"},
                {"ref": "refs/heads/b", "remote_before": OID, "remote_after": "d" * 40, "backup_ref": "refs/codex-backup/op/b"}
            ],
            "fast_forward_verified": True, "atomic": False, "forced": True,
            "protection_rejected": False
        }
        rehash(receipt, "receipt_sha256")
        codes = {row["code"] for row in validator.validate_receipt(receipt, plan)}
        self.assertIn("force-push-forbidden", codes)
        self.assertIn("non-atomic-multi-ref", codes)
        receipt["push"]["protection_rejected"] = True
        rehash(receipt, "receipt_sha256")
        self.assertIn(
            "protection-rejection-ignored",
            {row["code"] for row in validator.validate_receipt(receipt, plan)},
        )

    def test_cli_never_executes_recorded_command(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            sentinel = root / "must-not-exist.txt"
            plan = make_plan()
            plan["commands"] = [{"cwd": ".", "argv": [sys.executable, "-c", f"open({str(sentinel)!r}, 'w').write('bad')"]}]
            rehash(plan, "plan_sha256")
            receipt = make_receipt(plan)
            (root / "plan.json").write_text(json.dumps(plan), encoding="utf-8")
            (root / "receipt.json").write_text(json.dumps(receipt), encoding="utf-8")
            stream = io.StringIO()
            with redirect_stdout(stream):
                code = validator.main(["execution", str(root), "--plan", "plan.json", "--receipt", "receipt.json"])
            result = json.loads(stream.getvalue())
            self.assertEqual(code, 0, result)
            self.assertFalse(result["commands_executed"])
            self.assertFalse(sentinel.exists())

    def test_scientific_result_is_not_an_engineering_command_failure(self) -> None:
        plan = make_plan()
        receipt = make_receipt(plan)
        receipt["failure_class"] = "scientific"
        rehash(receipt, "receipt_sha256")
        self.assertNotIn("command-failed", {row["code"] for row in validator.validate_receipt(receipt, plan)})


if __name__ == "__main__":
    unittest.main()
