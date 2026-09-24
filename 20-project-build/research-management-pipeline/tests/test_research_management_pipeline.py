from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = ROOT / "20-project-build" / "research-workspace-governance" / "scripts" / "validate_contract_registry.py"


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

    def test_management_entry_reuses_governance_validator_without_writes(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            governance = project / ".agents" / "governance"
            governance.mkdir(parents=True)
            registry = governance / "contract_registry.json"
            registry.write_text(json.dumps({
                "schema_version": "research-contract-registry/v1",
                "registry_id": "small-review",
                "revision": 1,
                "supersedes": None,
                "profile_refs": [],
                "protocol_refs": [],
                "contracts": [],
                "amendments": [],
            }), encoding="utf-8")
            before = {path.relative_to(project).as_posix(): path.read_bytes() for path in project.rglob("*") if path.is_file()}
            process = subprocess.run([
                sys.executable, "-B", str(VALIDATOR), "validate", str(project),
                "--registry", ".agents/governance/contract_registry.json",
            ], capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
            after = {path.relative_to(project).as_posix(): path.read_bytes() for path in project.rglob("*") if path.is_file()}
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            payload = json.loads(process.stdout)
            self.assertEqual(payload["schema_version"], "research-contract-registry-validation/v1")
            self.assertFalse(payload["commands_executed"])
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
