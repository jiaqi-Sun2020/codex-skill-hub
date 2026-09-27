from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = SKILL_ROOT / "scripts" / "validate_figure_contract.py"
SPEC = importlib.util.spec_from_file_location("validate_figure_contract", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def base_contract() -> dict:
    return {
        "schema_version": "academic-figure-contract/v1",
        "figure_id": "fig-generic",
        "status": "draft",
        "claim_anchors": ["claim-1"],
        "panels": [
            {
                "panel_id": "a",
                "claim_anchor": "claim-1",
                "evidence_refs": ["source/data.json"],
                "populations": [
                    {
                        "population_id": "a-source",
                        "role": "source",
                        "count": 20,
                        "selector_ref": "source/data.json#all",
                        "evidence_refs": ["source/data.json"],
                    },
                    {
                        "population_id": "a-display",
                        "role": "display",
                        "count": 20,
                        "selector_ref": "source/data.json#display",
                        "relationship_to_rendered_rows": "one_to_one",
                        "evidence_refs": ["source/data.json"],
                    },
                    {
                        "population_id": "a-fit",
                        "role": "fit",
                        "count": 17,
                        "selector_ref": "source/data.json#fit",
                        "relationship_to_display": "declared subset after reviewed exclusions",
                        "evidence_refs": ["source/data.json", "source/exclusions.json"],
                    },
                ],
                "uncertainty": {
                    "applicability": "required",
                    "method": "resampling defined by the project method",
                    "meaning": "variation under the declared resampling unit",
                    "unit_of_analysis": "project-declared independent unit",
                    "prohibited_inference": "Does not establish a claim outside the declared evaluation scope.",
                },
                "elements": [
                    {
                        "element_id": "a.points",
                        "kind": "data_marks",
                        "evidence_refs": ["source/data.json"],
                    }
                ],
            }
        ],
        "surfaces": {
            "caption_md": "caption.md",
            "ppt": {"required": False, "visible_explanations_required": False},
            "bindings": [
                {
                    "element_id": "a.points",
                    "source": "source-panel-a",
                    "manifest": "manifest-panel-a",
                    "caption": "caption-panel-a",
                }
            ],
        },
        "baseline": {"current_revision": "r1", "protected_user_revisions": []},
        "rebuild": {
            "mode": "command",
            "working_directory": ".",
            "command": ["python", "source/build.py"],
            "inputs": [{"path": "source/data.json", "sha256": ""}],
            "outputs": ["exports/figure.svg"],
        },
        "revision": {"change_class": "initial", "changed_refs": [], "invalidated_outputs": []},
    }


class FigureContractTests(unittest.TestCase):
    def validate(self, contract: dict, previous: dict | None = None):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "source").mkdir()
            (root / "exports").mkdir()
            data_path = root / "source" / "data.json"
            data_path.write_text("{}\n", encoding="utf-8")
            (root / "source" / "exclusions.json").write_text("{}\n", encoding="utf-8")
            (root / "caption.md").write_text("# Caption\n", encoding="utf-8")
            contract = copy.deepcopy(contract)
            first_input = contract["rebuild"]["inputs"][0]
            if isinstance(first_input, dict) and first_input.get("path") == "source/data.json":
                first_input["sha256"] = MODULE.sha256_file(data_path)
            contract_path = root / "figure_contract.json"
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            return MODULE.validate_contract(contract, contract_path, root=root, previous=previous)

    def test_distinct_display_and_fit_populations_are_valid_when_declared(self):
        errors, _, report = self.validate(base_contract())
        self.assertEqual([], errors)
        self.assertTrue(report["valid"])

    def test_multiple_sensitivity_populations_are_allowed(self):
        contract = base_contract()
        for suffix, count in (("short", 12), ("long", 15)):
            contract["panels"][0]["populations"].append(
                {
                    "population_id": f"a-sensitivity-{suffix}",
                    "role": "sensitivity",
                    "count": count,
                    "selector_ref": f"source/data.json#sensitivity-{suffix}",
                    "relationship_to_display": "declared alternative subset",
                    "evidence_refs": ["source/data.json"],
                }
            )
        errors, _, _ = self.validate(contract)
        self.assertEqual([], errors)

    def test_display_population_must_explain_rendered_row_relationship(self):
        contract = base_contract()
        contract["panels"][0]["populations"][1].pop("relationship_to_rendered_rows")
        errors, _, _ = self.validate(contract)
        self.assertTrue(any("relationship_to_rendered_rows" in issue for issue in errors))

    def test_aggregated_display_population_is_valid_without_one_to_one_claim(self):
        contract = base_contract()
        contract["panels"][0]["populations"][1]["relationship_to_rendered_rows"] = (
            "aggregated into project-defined summary rows"
        )
        errors, _, _ = self.validate(contract)
        self.assertEqual([], errors)

    def test_missing_surface_binding_is_blocking(self):
        contract = base_contract()
        contract["surfaces"]["bindings"] = []
        errors, _, _ = self.validate(contract)
        self.assertTrue(any("missing elements" in issue for issue in errors))

    def test_ppt_delivery_requires_all_declared_surfaces(self):
        contract = base_contract()
        contract["surfaces"]["ppt"] = {
            "required": True,
            "visible_explanations_required": True,
        }
        errors, _, _ = self.validate(contract)
        self.assertTrue(any("ppt_main" in issue for issue in errors))
        self.assertTrue(any("visible_explanation" in issue for issue in errors))

    def test_semantic_change_requires_invalidation(self):
        previous = base_contract()
        current = copy.deepcopy(previous)
        current["panels"][0]["populations"][2]["count"] = 16
        current["revision"] = {
            "change_class": "scientific",
            "changed_refs": ["a-fit"],
            "invalidated_outputs": [],
        }
        errors = MODULE.compare_contracts(previous, current)
        self.assertTrue(any("invalidated_outputs" in issue for issue in errors))

    def test_visual_only_change_does_not_invalidate_science(self):
        previous = base_contract()
        current = copy.deepcopy(previous)
        current["style_manifest"] = "style/revised-style.json"
        current["revision"] = {
            "change_class": "visual",
            "changed_refs": ["style_manifest"],
            "invalidated_outputs": [],
        }
        self.assertEqual([], MODULE.compare_contracts(previous, current))

    def test_architecture_rejects_dangling_edge(self):
        contract = base_contract()
        contract["architecture"] = {
            "nodes": [{"node_id": "input", "evidence_refs": ["source/model.txt"]}],
            "edges": [
                {
                    "edge_id": "edge-1",
                    "from": "input",
                    "to": "missing",
                    "evidence_refs": ["source/model.txt"],
                }
            ],
        }
        errors, _, _ = self.validate(contract)
        self.assertTrue(any("endpoints" in issue for issue in errors))

    def test_external_input_requires_hash(self):
        contract = base_contract()
        contract["rebuild"]["inputs"] = [{"path": "C:/external/data.csv", "external": True}]
        errors, _, _ = self.validate(contract)
        self.assertTrue(any("external reference requires sha256" in issue for issue in errors))

    def test_output_may_not_escape_figure_root(self):
        contract = base_contract()
        contract["rebuild"]["outputs"] = ["../outside.svg"]
        errors, _, _ = self.validate(contract)
        self.assertTrue(any("output escapes figure root" in issue for issue in errors))

    def test_manual_rebuild_uses_instructions_instead_of_fake_command(self):
        contract = base_contract()
        contract["rebuild"].pop("command")
        contract["rebuild"]["mode"] = "manual"
        contract["rebuild"]["instructions_ref"] = "source/manual-rebuild.md"
        errors, _, _ = self.validate(contract)
        self.assertEqual([], errors)

    def test_caption_and_notes_hashes_must_match(self):
        contract = base_contract()
        contract["surfaces"]["caption_sha256"] = "a" * 64
        contract["surfaces"]["notes_caption_sha256"] = "b" * 64
        errors, _, _ = self.validate(contract)
        self.assertTrue(any("caption_sha256" in issue for issue in errors))

    def test_caption_hash_must_match_caption_file(self):
        contract = base_contract()
        contract["surfaces"]["caption_sha256"] = "a" * 64
        errors, _, _ = self.validate(contract)
        self.assertTrue(any("differs from caption.md" in issue for issue in errors))

    def test_template_is_not_a_delivery_contract(self):
        contract = base_contract()
        contract["template"] = True
        errors, _, _ = self.validate(contract)
        self.assertTrue(any("template contract" in issue for issue in errors))

    def test_semantic_change_cannot_be_labeled_visual(self):
        previous = base_contract()
        current = copy.deepcopy(previous)
        current["panels"][0]["populations"][2]["selector_ref"] = "source/data.json#new-fit"
        current["revision"] = {
            "change_class": "visual",
            "changed_refs": ["style_manifest"],
            "invalidated_outputs": [],
        }
        errors = MODULE.compare_contracts(previous, current)
        self.assertTrue(any("change_class is visual" in issue for issue in errors))


if __name__ == "__main__":
    unittest.main()
