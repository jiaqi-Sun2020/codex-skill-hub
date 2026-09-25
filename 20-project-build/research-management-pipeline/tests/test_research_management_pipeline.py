from __future__ import annotations

from pathlib import Path
import unittest


class ResearchManagementIntegrationTests(unittest.TestCase):
    def test_skill_is_an_orchestrator_without_a_duplicate_runtime(self):
        skill_root = Path(__file__).resolve().parents[1]
        text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("validate_contract_registry.py", text)
        self.assertIn("experiment-protocol-audit", text)
        self.assertIn("Neat-Freak", text)
        self.assertIn("project-submission-audit", text)
        self.assertIn("project-agent-generator-skill", text)
        self.assertFalse((skill_root / "scripts").exists())

    def test_engineering_routing_contract_is_skill_local_and_has_no_executor(self):
        skill_root = Path(__file__).resolve().parents[1]
        operations = skill_root / "references" / "engineering-operations.md"
        lifecycle = skill_root / "references" / "lifecycle-interface.md"
        self.assertTrue(operations.is_file())
        self.assertTrue(lifecycle.is_file())
        operations_text = operations.read_text(encoding="utf-8")
        lifecycle_text = lifecycle.read_text(encoding="utf-8")
        self.assertIn("fast-forward", operations_text)
        self.assertIn("head_sha", operations_text)
        self.assertIn("repair:", lifecycle_text)
        self.assertIn("run:", lifecycle_text)


if __name__ == "__main__":
    unittest.main()
