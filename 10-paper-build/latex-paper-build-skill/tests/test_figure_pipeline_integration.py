from __future__ import annotations

import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
HUB_DIR = SKILL_DIR.parent
SCRIPT_PATH = SKILL_DIR / "scripts" / "create_paper_pipeline.py"
FIGURE_SKILL_DIR = HUB_DIR / "academic-figure-workflow"


def load_pipeline_module():
    spec = importlib.util.spec_from_file_location("create_paper_pipeline", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FigurePipelineIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.pipeline = load_pipeline_module()

    def create_minimal_pipeline(self, root: Path) -> Path:
        project = root / "paper"
        args = self.pipeline.parse_args(
            [
                "--project",
                str(project),
                "--title",
                "Figure-free theory paper",
                "--no-template",
            ]
        )
        self.pipeline.create_pipeline(args)
        return project

    def test_legacy_cli_and_stage_numbering_are_preserved(self) -> None:
        self.assertEqual(
            self.pipeline.STAGE_DIRS,
            (
                "00_research_logic",
                "01_experiment_design",
                "02_training_code",
                "03_results",
                "04_reports",
                "05_manuscript_zh",
                "06_review_gate",
                "07_polished_submission",
            ),
        )
        with tempfile.TemporaryDirectory() as temporary:
            project = self.create_minimal_pipeline(Path(temporary))
            config = json.loads((project / "paper_config.json").read_text(encoding="utf-8"))
            self.assertEqual(config["schema_version"], 1)
            self.assertNotIn("figures", config)

    def test_figure_free_pipeline_creates_no_empty_figure_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.create_minimal_pipeline(Path(temporary))
            self.assertFalse((project / "figures").exists())
            self.assertFalse((project / "05_manuscript_zh" / "figures").exists())
            self.assertFalse(any(project.rglob("style_manifest.yaml")))
            self.assertFalse(any(project.rglob("*manifest.json")))

    def test_generated_context_routes_the_optional_figure_lane(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.create_minimal_pipeline(Path(temporary))
            context = (project / "pipeline_context.md").read_text(encoding="utf-8")
            self.assertIn("`data-analysis`", context)
            self.assertIn("`academic-figure-workflow`", context)
            self.assertIn("`05_manuscript_zh/figures/`", context)
            self.assertIn("N/A until activated", context)
            self.assertIn("Figure/package QA and scientific claim review remain separate", context)

    def test_experiment_plan_contains_a_non_executing_figure_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.create_minimal_pipeline(Path(temporary))
            plan = (project / "01_experiment_design" / "experiment_plan.md").read_text(encoding="utf-8")
            self.assertIn("## Optional Figure Evidence Plan", plan)
            self.assertIn("Evidence readiness", plan)
            self.assertIn("Statistics readiness", plan)
            self.assertIn("defines figure intent only", plan)

    def test_review_templates_keep_figure_and_claim_states_separate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.create_minimal_pipeline(Path(temporary))
            review = (project / "06_review_gate" / "author_review_checklist.md").read_text(encoding="utf-8")
            report = (project / "07_polished_submission" / "build_report.md").read_text(encoding="utf-8")
            self.assertIn("visual/package PASS has not been interpreted as scientific claim approval", review)
            self.assertIn("`N/A` with a reason", review)
            self.assertIn("Visual QA does not approve the scientific claim", report)
            for required in ("Editable figure sources", "Figure captions", "Figure evidence/source trace"):
                self.assertIn(required, report)

    def test_figure_contract_blocks_unreviewed_evidence_from_final_status(self) -> None:
        contract = (
            FIGURE_SKILL_DIR / "references" / "figure-argument-contract.md"
        ).read_text(encoding="utf-8")
        self.assertIn("unavailable | unreviewed | verified_for_figure", contract)
        self.assertIn("stop at a specification, storyboard, or clearly marked draft", contract)
        self.assertIn("Visual, packaging, or editability QA must not change", contract)
        self.assertIn("visually_and_structurally_verified", contract)
        self.assertNotIn("Figure status: specification | storyboard | draft | verified", contract)

    def test_figure_skill_retains_standalone_root_and_pipeline_root(self) -> None:
        skill = (FIGURE_SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("`05_manuscript_zh/figures/`", skill)
        self.assertIn("default to `<project>/figures/`", skill)
        self.assertIn("does not depend on the LaTeX", skill)

    def test_academic_figure_markdown_has_no_broken_local_links(self) -> None:
        broken: list[str] = []
        link_pattern = re.compile(r"\[[^\]]+\]\(([^)#]+)(?:#[^)]+)?\)")
        for markdown in FIGURE_SKILL_DIR.rglob("*.md"):
            content = markdown.read_text(encoding="utf-8")
            for match in link_pattern.finditer(content):
                target = match.group(1).strip()
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                resolved = (markdown.parent / target).resolve()
                if not resolved.exists():
                    broken.append(f"{markdown.relative_to(FIGURE_SKILL_DIR)} -> {target}")
        self.assertEqual(broken, [])


if __name__ == "__main__":
    unittest.main()
