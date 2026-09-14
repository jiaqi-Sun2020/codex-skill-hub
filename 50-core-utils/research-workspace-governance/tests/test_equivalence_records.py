from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_equivalence_records.py"
SPEC = importlib.util.spec_from_file_location("validate_equivalence_records", SCRIPT)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


class EquivalenceRecordTests(unittest.TestCase):
    def base_record(self, relation: str = "metric_only") -> dict:
        forbidden = {
            "matrix_exact": [
                "observational_interchangeability",
                "metric_comparison",
                "deduplicate_observation_evidence",
            ],
            "matrix_global_phase": [
                "matrix_identity",
                "observational_interchangeability",
                "metric_comparison",
                "deduplicate_observation_evidence",
            ],
            "observational_protocol": [
                "matrix_identity",
                "matrix_equivalence_up_to_global_phase",
                "deduplicate_operator_evidence",
            ],
            "metric_only": [
                "matrix_identity",
                "matrix_equivalence_up_to_global_phase",
                "observational_interchangeability",
                "deduplicate_operator_evidence",
                "deduplicate_observation_evidence",
            ],
        }[relation]
        allowed = {
            "matrix_exact": ["matrix_identity"],
            "matrix_global_phase": ["matrix_equivalence_up_to_global_phase"],
            "observational_protocol": ["observational_interchangeability"],
            "metric_only": ["metric_comparison"],
        }[relation]
        record = {
            "id": "comparison-1",
            "type": relation,
            "scope": {"implementation": ["a", "b"]},
            "evidence": [{"external_id": "domain-run-17", "content_sha256": "a" * 64}],
            "comparison_method": {"name": "domain-test", "result": "pass"},
            "tolerance": None if relation == "matrix_exact" else 1e-9,
            "invalidation_keys": {"implementation_sha256": "abc"},
            "allowed_use": allowed,
            "forbidden_inference": forbidden,
            "status": "verified",
        }
        if relation == "matrix_global_phase":
            record["semantics"] = {"global_phase_physically_irrelevant": True}
        if relation == "observational_protocol":
            record["protocol"] = {"id": "z-basis-v1"}
        return record

    def document(self, record: dict) -> dict:
        return {"schema_version": validator.SCHEMA_VERSION, "records": [record]}

    def test_all_four_relations_can_be_verified(self) -> None:
        for relation in sorted(validator.RELATION_TYPES):
            with self.subTest(relation=relation):
                report = validator.validate_document(self.document(self.base_record(relation)))
                self.assertEqual(report["status"], "verified", report)

    def test_metric_only_cannot_claim_observational_equivalence(self) -> None:
        record = self.base_record()
        record["allowed_use"].append("observational_interchangeability")
        record["forbidden_inference"].remove("observational_interchangeability")
        report = validator.validate_document(self.document(record))
        codes = {item["code"] for item in report["records"][0]["findings"]}
        self.assertEqual(report["status"], "invalid")
        self.assertIn("overstated-equivalence", codes)
        self.assertIn("missing-forbidden-inference", codes)

    def test_observational_protocol_requires_protocol(self) -> None:
        record = self.base_record("observational_protocol")
        del record["protocol"]
        report = validator.validate_document(self.document(record))
        self.assertEqual(report["status"], "invalid")
        self.assertIn("missing-observational-protocol", {item["code"] for item in report["records"][0]["findings"]})

    def test_global_phase_requires_physical_semantics(self) -> None:
        record = self.base_record("matrix_global_phase")
        del record["semantics"]
        report = validator.validate_document(self.document(record))
        self.assertEqual(report["status"], "invalid")
        self.assertIn("missing-global-phase-semantics", {item["code"] for item in report["records"][0]["findings"]})

    def test_invalidation_drift_makes_verified_record_stale(self) -> None:
        record = self.base_record()
        document = self.document(record)
        document["current_invalidation_keys"] = {
            record["id"]: {"implementation_sha256": "changed"}
        }
        report = validator.validate_document(document)
        self.assertEqual(report["status"], "unverified")
        self.assertEqual(report["records"][0]["effective_status"], "stale")

    def test_unstructured_evidence_cannot_verify_a_relation(self) -> None:
        record = self.base_record()
        record["evidence"] = ["trust me"]
        report = validator.validate_document(self.document(record))
        self.assertEqual(report["status"], "invalid")
        self.assertIn("untraceable-equivalence-evidence", {item["code"] for item in report["records"][0]["findings"]})

    def test_matrix_exact_rejects_nonzero_tolerance(self) -> None:
        record = self.base_record("matrix_exact")
        record["tolerance"] = 1e-6
        report = validator.validate_document(self.document(record))
        self.assertEqual(report["status"], "invalid")
        self.assertIn("nonexact-matrix-tolerance", {item["code"] for item in report["records"][0]["findings"]})

    def test_allowed_and_forbidden_claim_cannot_conflict(self) -> None:
        record = self.base_record()
        record["forbidden_inference"].append("metric_comparison")
        report = validator.validate_document(self.document(record))
        self.assertEqual(report["status"], "invalid")
        self.assertIn("conflicting-inference-boundary", {item["code"] for item in report["records"][0]["findings"]})

    def test_project_evidence_hash_and_boundary_are_checked(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw) / "project"
            project.mkdir()
            evidence = project / "evidence.json"
            evidence.write_text("{}\n", encoding="utf-8")
            record = self.base_record()
            record["evidence"] = [{"path": "evidence.json", "sha256": "0" * 64}]
            report = validator.validate_document(self.document(record), project)
            self.assertEqual(report["status"], "invalid")
            self.assertIn("evidence-hash-mismatch", {item["code"] for item in report["records"][0]["findings"]})

            record["evidence"] = [{"path": "../outside.json"}]
            report = validator.validate_document(self.document(record), project)
            self.assertIn("evidence-path-outside-project", {item["code"] for item in report["records"][0]["findings"]})

    def test_cli_rejects_unknown_schema(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "records.json"
            path.write_text(json.dumps({"schema_version": "research-equivalence-record/v2", "records": []}), encoding="utf-8")
            self.assertEqual(validator.main([str(path), "--compact"]), 2)

    def test_declared_empty_record_set_is_not_verified(self) -> None:
        report = validator.validate_document(
            {"schema_version": validator.SCHEMA_VERSION, "records": []}
        )
        self.assertEqual(report["status"], "invalid")
        self.assertIn("empty-equivalence-records", {item["code"] for item in report["findings"]})


if __name__ == "__main__":
    unittest.main()
