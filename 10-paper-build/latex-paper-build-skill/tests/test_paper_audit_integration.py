"""Structural/integration checks, not scientific or agent-behavior validation."""
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

HUB = Path(__file__).resolve().parents[2]
ROOT = HUB.parent
AUDIT = HUB / "paper-audit"
PIPELINE = HUB / "latex-paper-build-skill"
SCRIPT = PIPELINE / "scripts" / "create_paper_pipeline.py"


def load_pipeline():
    spec = importlib.util.spec_from_file_location("paper_audit_pipeline_test", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(str(SCRIPT))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def file_snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob("*") if p.is_file()}


def local_targets(markdown):
    for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", markdown.read_text(encoding="utf-8")):
        target = match.group(1)
        if not target.startswith(("https://", "http://", "mailto:", "#")):
            yield (markdown.parent / target.split("#", 1)[0]).resolve()


class PaperAuditIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pipeline = load_pipeline()

    def create(self, root):
        project = root / "synthetic-paper"
        args = self.pipeline.parse_args(
            ["--project", str(project), "--title", "Synthetic review fixture", "--no-template"]
        )
        self.pipeline.create_pipeline(args)
        return project, args

    def test_package_is_small_and_self_contained(self):
        expected = {"SKILL.md", "LICENSE", "agents/openai.yaml",
                    "references/method-checks.md", "references/report-template.md"}
        self.assertEqual(set(file_snapshot(AUDIT)), expected)
        with tempfile.TemporaryDirectory(prefix="paper-audit-package-") as temporary:
            isolated = Path(temporary) / "paper-audit"
            shutil.copytree(AUDIT, isolated)
            self.assertFalse((isolated.parent / "latex-paper-build-skill").exists())
            for markdown in isolated.rglob("*.md"):
                for target in local_targets(markdown):
                    self.assertTrue(target.is_relative_to(isolated), str(target))
                    self.assertTrue(target.is_file(), str(target))
            self.assertEqual(file_snapshot(isolated), file_snapshot(AUDIT))

    def test_metadata_declares_review_not_runtime_dependencies(self):
        skill = (AUDIT / "SKILL.md").read_text(encoding="utf-8")
        ui = (AUDIT / "agents/openai.yaml").read_text(encoding="utf-8")
        self.assertRegex(skill, r"(?m)^name: paper-audit$")
        self.assertIn("$paper-audit", ui)
        self.assertNotRegex(ui, r"(?m)^dependencies:")
        self.assertIn("Revision re-review", skill)

    def test_distribution_retains_exact_fixed_sources_and_license_scopes(self):
        license_text = (AUDIT / "LICENSE").read_text(encoding="utf-8")
        for sha in (
            "33ddc61ee5aaa1932210894ac62d4d7ac909c936",
            "6383d0ca3c1b6cec3e9c8d7fda75092d67857768",
            "ef30b0f9790eb419bbfe25906472b727dbd69de3",
            "c1637a89c7097d486ba1c6e755e34d01cbb24998",
            "8c307f367c91bd974002f10f2be2965d642c13df",
        ):
            self.assertIn(sha, license_text)
        for original_owner in ("Connor", "Yiran Wang", "Stephen D. Turner", "Siqi Chen"):
            self.assertIn(original_owner, license_text)
        self.assertIn("Apache License", license_text)
        self.assertIn("END OF TERMS AND CONDITIONS", license_text)
        self.assertIn("does not relicense", license_text)

    def test_real_generation_adds_navigation_not_review_artifacts(self):
        with tempfile.TemporaryDirectory(prefix="paper-audit-generation-") as temporary:
            project, _ = self.create(Path(temporary))
            self.assertEqual(set(file_snapshot(project)), {
                "paper_config.json", "pipeline_context.md",
                "00_research_logic/intake.md", "00_research_logic/research_logic.md",
                "01_experiment_design/experiment_plan.md",
                "06_review_gate/author_review_checklist.md",
                "07_polished_submission/build_report.md",
            })
            context = (project / "pipeline_context.md").read_text(encoding="utf-8")
            review = (project / "06_review_gate/author_review_checklist.md").read_text(encoding="utf-8")
            build = (project / "07_polished_submission/build_report.md").read_text(encoding="utf-8")
            self.assertIn("paper-audit", context)
            self.assertIn("paper-audit", review)
            self.assertIn("pre-review", build)
            self.assertFalse((project / "06_review_gate/paper_audit_report.md").exists())
            self.assertFalse(any(project.rglob("*ledger*")))

    def test_old_cli_configuration_and_eight_stages_still_work(self):
        with tempfile.TemporaryDirectory(prefix="paper-audit-legacy-cli-") as temporary:
            project, _ = self.create(Path(temporary))
            config = json.loads((project / "paper_config.json").read_text(encoding="utf-8"))
            self.assertEqual(config["schema_version"], 1)
            self.assertNotIn("paper_audit", config)
            self.assertEqual({p.name for p in project.iterdir() if p.is_dir()},
                             set(self.pipeline.STAGE_DIRS))
            self.assertEqual(len(self.pipeline.STAGE_DIRS), 8)

    def test_existing_user_files_and_nonstandard_report_remain_byte_identical(self):
        with tempfile.TemporaryDirectory(prefix="paper-audit-legacy-files-") as temporary:
            project, args = self.create(Path(temporary))
            (project / "pipeline_context.md").write_bytes(
                b"\xef\xbb\xbf# Owner navigation\r\nKeep custom decisions.\r\n")
            report = project / "06_review_gate" / "my-old-review.txt"
            report.write_bytes(b"PA-021: unresolved\r\nOriginal reviewer text.\r\n")
            before = file_snapshot(project)
            self.pipeline.create_pipeline(args)
            self.assertEqual(file_snapshot(project), before)
            self.assertFalse((report.parent / "paper_audit_report.md").exists())

    def test_minimal_initializer_view_is_still_only_two_entries(self):
        inputs = {
            "work_goal": "Inspect the draft", "acceptance": "Bounded review only",
            "formal_goal_ref": "", "goal_source": "synthetic request",
            "next_action": "Ask author for the missing figure", "references": [],
            "title": "Synthetic", "intake_ref": "00_research_logic/intake.md",
            "start_stage": "06_review_gate",
        }
        entries = self.pipeline.initialization_entries(inputs)
        self.assertEqual(set(entries), {"00_research_logic/intake.md", "pipeline_context.md"})
        self.assertNotIn("paper_audit_report.md", "\n".join(entries.values()))

    def test_all_final_entrances_link_the_same_handoff(self):
        for relative in (
            "latex-paper-build-skill/SKILL.md",
            "latex-paper-build-skill/references/paper-pipeline.md",
            "paper-polishing-skill/SKILL.md",
            "prl-manuscript-polisher/SKILL.md",
        ):
            text = (HUB / relative).read_text(encoding="utf-8")
            with self.subTest(entrance=relative):
                self.assertIn("paper-audit/SKILL.md#final-manuscript-handoff", text)
        self.assertIn("## Final-manuscript handoff",
                      (AUDIT / "SKILL.md").read_text(encoding="utf-8"))

    def test_changed_entrances_have_resolvable_local_links(self):
        paths = list(AUDIT.rglob("*.md")) + [
            HUB / "README.md", HUB / "README.en.md",
            ROOT / "README.md", ROOT / "README.en.md",
            HUB / "latex-paper-build-skill/SKILL.md",
            HUB / "latex-paper-build-skill/references/paper-pipeline.md",
            HUB / "paper-polishing-skill/SKILL.md",
            HUB / "prl-manuscript-polisher/SKILL.md",
        ]
        for markdown in paths:
            for target in local_targets(markdown):
                self.assertTrue(target.exists(), f"{markdown} -> {target}")

    def test_counts_and_bilingual_indexes_match_actual_active_skills(self):
        active = [p for section in ("10-paper-build", "20-project-build", "50-core-utils", "60-visual-computing")
                  for p in (ROOT / section).glob("*/SKILL.md")
                  if p.parent.name != "skill-registry"]
        self.assertEqual(len(active), 36)
        self.assertEqual(len(list(HUB.glob("*/SKILL.md"))), 13)
        for root_name in ("README.md", "README.en.md"):
            root_doc = (ROOT / root_name).read_text(encoding="utf-8")
            paper_doc = (HUB / root_name).read_text(encoding="utf-8")
            self.assertIn("36", root_doc)
            self.assertIn("13", paper_doc)
            self.assertIn("paper-audit", root_doc)
            self.assertIn("paper-audit", paper_doc)


if __name__ == "__main__":
    unittest.main()
