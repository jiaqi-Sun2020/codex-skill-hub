from __future__ import annotations

import copy
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch
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

    def test_svg_contract_needs_no_ppt_or_notes_and_legacy_ppt_keeps_notes(self):
        contract = base_contract()
        self.assertEqual([], self.validate(contract)[0])
        self.assertNotIn("notes", contract["surfaces"]["bindings"][0])
        contract["surfaces"]["ppt"]["required"] = True
        contract["surfaces"]["bindings"][0]["ppt_main"] = "native-panel-a"
        errors = self.validate(contract)[0]
        self.assertTrue(any("notes: required for PPT" in issue for issue in errors))
        contract["surfaces"]["bindings"][0]["notes"] = "notes-a"
        self.assertEqual([], self.validate(contract)[0])

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


class AppleStyleCompatibilityTests(unittest.TestCase):
    """Check real schema/consumer invariants, not visual or agent behaviour."""

    def setUp(self):
        self.template = json.loads(
            (SKILL_ROOT / "assets/style_manifest.template.yaml").read_text("utf-8")
        )
        reference = (SKILL_ROOT / "references/apple-inspired-academic-figure-style.md").read_text("utf-8")
        self.tokens = json.loads(re.search(r"```json\n(.*?)\n```", reference, re.S).group(1))
        spec = importlib.util.spec_from_file_location("style_manifest", SKILL_ROOT / "scripts/style_manifest.py")
        self.style = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.style)
        spec = importlib.util.spec_from_file_location("apple_test_nstyle", SKILL_ROOT / "scripts/nature_mpl_style.py")
        self.nstyle = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"style_manifest": self.style}):
            spec.loader.exec_module(self.nstyle)

    def merged(self):
        result = copy.deepcopy(self.template)

        def merge(existing, changes):
            for key, value in changes.items():
                self.assertIn(key, existing, f"new schema field: {key}")
                if isinstance(value, dict):
                    merge(existing[key], value)
                else:
                    existing[key] = value
        merge(result, self.tokens)
        return result

    def task_manifest(self, *tasks):
        keys = set(self.style.COMMON_REQUIRED_SECTIONS)
        for task in tasks:
            keys.update(self.style.TASK_REQUIRED_SECTIONS[task])
        return {key: copy.deepcopy(value) for key, value in self.template.items() if key in keys}

    def test_minimal_svg_manifest_has_no_unrelated_sections_or_notes(self):
        manifest = self.task_manifest("svg")
        self.assertEqual([], self.style.validate_style_manifest(manifest, tasks=["svg"])[0])
        for key in ("architecture", "powerpoint", "axes", "charts"):
            self.assertNotIn(key, manifest)
        before = copy.deepcopy(manifest)
        self.style.validate_style_manifest(manifest, tasks=["svg"])
        self.assertEqual(before, manifest)

    def test_task_specific_sections_and_common_fields_remain_required(self):
        for task in ("svg", "plot", "architecture", "powerpoint"):
            complete = self.task_manifest(task)
            self.assertEqual([], self.style.validate_style_manifest(complete, tasks=[task])[0])
            required = self.style.COMMON_REQUIRED_SECTIONS | self.style.TASK_REQUIRED_SECTIONS[task]
            for field in required:
                with self.subTest(task=task, field=field):
                    incomplete = copy.deepcopy(complete)
                    del incomplete[field]
                    self.assertIn(f"missing required section: {field}",
                                  self.style.validate_style_manifest(incomplete, tasks=[task])[0])

    def test_full_legacy_and_mixed_task_manifests_remain_compatible(self):
        before = copy.deepcopy(self.template)
        for tasks in (None, ["svg"], ["plot"], ["architecture"], ["powerpoint"], ["plot", "powerpoint"]):
            self.assertEqual([], self.style.validate_style_manifest(self.template, tasks=tasks)[0])
        self.assertEqual(before, self.template)
        plot = self.task_manifest("plot")
        self.assertTrue(any("powerpoint" in issue for issue in
                            self.style.validate_style_manifest(plot, tasks=["plot", "powerpoint"])[0]))

    def test_schema_version_legacy_numeric_and_string_forms_are_preserved(self):
        for version in (1.0, 1, "1.0"):
            for task in ("svg", "plot", "powerpoint"):
                with self.subTest(version=version, task=task):
                    manifest = self.task_manifest(task)
                    manifest["schema_version"] = version
                    before = copy.deepcopy(manifest)
                    self.assertEqual([], self.style.validate_style_manifest(manifest, tasks=[task])[0])
                    self.assertEqual(before, manifest)
                    self.assertIs(type(version), type(manifest["schema_version"]))

    def test_schema_version_unknown_versions_and_invalid_types_are_rejected(self):
        for version in (None, True, False, 0, 2, 1.1, float("nan"), float("inf"),
                        "", "1", "1.0 ", "2.0", "True", [], {}, ["1.0"]):
            with self.subTest(version=version):
                manifest = self.task_manifest("svg")
                manifest["schema_version"] = version
                errors, _ = self.style.validate_style_manifest(manifest, tasks=["svg"])
                self.assertTrue(any("schema_version" in error for error in errors), errors)

    def test_declared_optional_sections_and_colours_cannot_bypass_checks(self):
        for section, value in (("architecture", []), ("powerpoint", None),
                               ("axes", "invalid"), ("precedence", {})):
            with self.subTest(section=section):
                manifest = self.task_manifest("svg")
                manifest[section] = value
                self.assertTrue(self.style.validate_style_manifest(manifest, tasks=["svg"])[0])
        for value in ("red", "#123", "#GG0000", None, False, 123):
            with self.subTest(colour=value):
                manifest = self.task_manifest("svg")
                manifest["neutral_colors"]["text"] = value
                self.assertTrue(any("six-digit hex" in error for error in
                                    self.style.validate_style_manifest(manifest, tasks=["svg"])[0]))

    def test_unknown_tasks_and_invalid_identity_are_rejected(self):
        manifest = self.task_manifest("svg")
        self.assertTrue(self.style.validate_style_manifest(manifest, tasks=["powerpiont"])[0])
        for field, value in (("project_id", ""), ("schema_version", None),
                             ("references", {}), ("state", {"locked": True, "status": "approved"})):
            with self.subTest(field=field):
                broken = copy.deepcopy(manifest)
                broken[field] = value
                self.assertTrue(self.style.validate_style_manifest(broken, tasks=["svg"])[0])

    def test_validator_cli_svg_and_mixed_task_requirements(self):
        cli = SKILL_ROOT / "scripts/validate_style_manifest.py"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "style.json"
            path.write_text(json.dumps(self.task_manifest("svg")), encoding="utf-8")
            before = path.read_bytes()
            command = [sys.executable, "-X", "utf8", "-B", str(cli), "--manifest", str(path)]
            svg = subprocess.run([*command, "--task", "svg"], capture_output=True, text=True)
            self.assertEqual(0, svg.returncode, svg.stdout + svg.stderr)
            self.assertEqual(before, path.read_bytes())
            self.assertEqual(["style.json"], sorted(p.name for p in root.iterdir()))
            failed = subprocess.run([*command, "--task", "plot", "--task", "powerpoint"], capture_output=True, text=True)
            self.assertEqual(1, failed.returncode)
            self.assertIn("missing required section: axes", failed.stdout)
            self.assertIn("missing required section: powerpoint", failed.stdout)
            unknown = subprocess.run([*command, "--task", "unknown"], capture_output=True, text=True)
            self.assertEqual(2, unknown.returncode)

    def test_matplotlib_consumer_accepts_plot_without_architecture_or_ppt(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "style.json"
            path.write_text(json.dumps(self.task_manifest("plot")), encoding="utf-8")
            matplotlib = MagicMock()
            matplotlib.rcParams = {}
            self.nstyle.apply_nature_style(matplotlib, style_manifest_path=path)
            self.assertEqual("none", matplotlib.rcParams["svg.fonttype"])
            path.write_text(json.dumps(self.task_manifest("svg")), encoding="utf-8")
            with self.assertRaisesRegex(self.style.StyleManifestError, "axes"):
                self.nstyle.apply_nature_style(matplotlib, style_manifest_path=path)

    @unittest.skipUnless(importlib.util.find_spec("matplotlib"), "Matplotlib unavailable; isolated plot CLI untested")
    def test_plot_cli_task_scope_and_required_data_checks(self):
        import os
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            data = root / "input.csv"
            data.write_text("x,y,se\n0,1,0.1\n1,1.5,0.2\n2,2,0.1\n", encoding="utf-8")
            data_before = data.read_bytes()
            style = root / "plot-style.json"
            style.write_text(json.dumps(self.task_manifest("plot")), encoding="utf-8")
            spec = root / "panels.json"
            panel = dict(panel="a", claim="Synthetic fixture only", data="input.csv", plot_type="errorbar",
                         x="x", y="y", yerr="se", color_role="treatment", xlabel="Index", ylabel="Test value",
                         metric_definition="Synthetic test values", error_source="Declared synthetic spread", expected_sample_size=3)
            spec.write_text(json.dumps([panel]), encoding="utf-8")
            environment = {**os.environ, "MPLCONFIGDIR": str(root / "mpl-cache")}
            command = [sys.executable, "-X", "utf8", "-B", str(SKILL_ROOT / "scripts/make_nature_multipanel.py"),
                       "--spec", str(spec), "--data-root", str(root), "--style-manifest", str(style),
                       "--column", "single", "--height-mm", "70", "--fixed-canvas", "--stem", "test"]
            output = root / "valid"
            valid = subprocess.run([*command, "--output-dir", str(output)], env=environment, capture_output=True, text=True)
            self.assertEqual(0, valid.returncode, valid.stdout + valid.stderr)
            report = json.loads((output / "test_qa.json").read_text("utf-8"))
            self.assertEqual(3, report["data_audit"][0]["plotted_row_count"])
            self.assertEqual(0, report["data_audit"][0]["skipped_row_count"])
            self.assertEqual(data_before, data.read_bytes())
            self.assertFalse(list(root.rglob("*.pptx")))
            minimal = self.task_manifest("plot")
            del minimal["axes"]
            style.write_text(json.dumps(minimal), encoding="utf-8")
            missing = root / "missing-config"
            invalid = subprocess.run([*command, "--output-dir", str(missing)], env=environment, capture_output=True, text=True)
            self.assertNotEqual(0, invalid.returncode)
            self.assertIn("missing required section: axes", invalid.stderr + invalid.stdout)
            self.assertFalse(missing.exists())
            style.write_text(json.dumps(self.task_manifest("plot")), encoding="utf-8")
            panel["y"] = "absent_scientific_column"
            spec.write_text(json.dumps([panel]), encoding="utf-8")
            bad_data = subprocess.run([*command, "--output-dir", str(root / "bad-data")], env=environment,
                                      capture_output=True, text=True)
            self.assertNotEqual(0, bad_data.returncode)
            self.assertEqual(data_before, data.read_bytes())

    @unittest.skipUnless(shutil.which("node"), "Node unavailable; PPT task preflight untested")
    def test_ppt_builder_refuses_missing_config_before_writes(self):
        builder = SKILL_ROOT / "scripts/build_figure_pptx.mjs"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            valid = self.task_manifest("powerpoint")
            cases = []
            for field in ("project_id", "references", "typography", "powerpoint", "arrows", "panels"):
                broken = copy.deepcopy(valid)
                del broken[field]
                cases.append((f"missing-{field}", broken, f"missing required section: {field}"))
            for section, field in (("semantic_colors", "input"), ("neutral_colors", "text")):
                broken = copy.deepcopy(valid)
                broken[section][field] = "not-a-colour"
                cases.append((f"bad-{section}", broken, f"{section}.{field} must be a six-digit hex"))
            for value in (None, [], False, "bad"):
                broken = copy.deepcopy(valid)
                broken["powerpoint"] = value
                cases.append((f"bad-ppt-type-{type(value).__name__}", broken, "powerpoint must be an object"))
            for version in (True, "2.0"):
                broken = copy.deepcopy(valid)
                broken["schema_version"] = version
                cases.append((f"bad-version-{version}", broken, "schema_version must be"))
            for name, manifest, message in cases:
                for existing in (False, True):
                    with self.subTest(case=name, existing=existing):
                        case_root = root / f"{name}-{existing}"
                        case_root.mkdir()
                        style = case_root / "style.json"
                        style.write_text(json.dumps(manifest), encoding="utf-8")
                        output = case_root / "output" / "figure.pptx"
                        if existing:
                            output.parent.mkdir()
                            output.write_bytes(b"user-owned output must survive")
                            (output.parent / "ppt_manifest.json").write_bytes(b"user-owned manifest")
                        before = {str(p.relative_to(case_root)): p.read_bytes() for p in case_root.rglob("*") if p.is_file()}
                        before_paths = sorted(str(p.relative_to(case_root)) for p in case_root.rglob("*"))
                        command = [shutil.which("node"), str(builder), "--demo", "--style-json", str(style),
                                   "--python", sys.executable, "--output", str(output)]
                        result = subprocess.run(command, capture_output=True, text=True)
                        print("PPT_ENTRY_CASE " + json.dumps(dict(case=name, existing=existing, command=command,
                              exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr)))
                        self.assertNotEqual(0, result.returncode)
                        self.assertIn(message, result.stderr)
                        after = {str(p.relative_to(case_root)): p.read_bytes() for p in case_root.rglob("*") if p.is_file()}
                        self.assertEqual(before, after)
                        self.assertEqual(before_paths, sorted(str(p.relative_to(case_root)) for p in case_root.rglob("*")))
                        if not existing:
                            self.assertFalse(output.parent.exists())

    @unittest.skipUnless(shutil.which("node"), "Node unavailable; PPT shared validation untested")
    def test_ppt_shared_validator_accepts_normal_full_and_task_manifests(self):
        builder = SKILL_ROOT / "scripts/build_figure_pptx.mjs"
        manifests = []
        for base in (self.template, self.task_manifest("powerpoint"), self.merged()):
            for version in (1.0, "1.0"):
                manifest = copy.deepcopy(base)
                manifest["schema_version"] = version
                manifests.append(manifest)
        program = (f"import {{requirePowerpointStyle}} from {json.dumps(builder.as_uri())};"
                   "import assert from 'node:assert/strict';"
                   f"for (const style of {json.dumps(manifests)}) {{"
                   f"const result = await requirePowerpointStyle(style, {json.dumps(sys.executable)});"
                   "assert.deepEqual(result.errors, []);}")
        result = subprocess.run([shutil.which("node"), "--input-type=module"], input=program, capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)

    @unittest.skipUnless(shutil.which("node"), "Node unavailable; normal PPT entry preflight untested")
    def test_ppt_entry_normal_style_passes_to_assembly_validation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            style = root / "style.json"
            style.write_text(json.dumps(self.task_manifest("powerpoint")), encoding="utf-8")
            # A deliberate later assembly error shows the actual CLI accepted
            # the normal PPT style, without requiring the optional renderer.
            spec = root / "empty-spec.json"
            spec.write_text('{"slides": []}', encoding="utf-8")
            command = [shutil.which("node"), str(SKILL_ROOT / "scripts/build_figure_pptx.mjs"),
                       "--spec", str(spec), "--style-json", str(style), "--python", sys.executable,
                       "--output", str(root / "output" / "figure.pptx")]
            result = subprocess.run(command, capture_output=True, text=True)
            print("PPT_ENTRY_CASE " + json.dumps(dict(case="normal-style-later-assembly-error", command=command,
                  exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr)))
            self.assertNotEqual(0, result.returncode)
            self.assertIn("Assembly spec needs at least one slide", result.stderr)
            self.assertNotIn("PPT style validation failed", result.stderr)
            self.assertFalse((root / "output").exists())

    @unittest.skipUnless(shutil.which("node"), "Node unavailable; normal PPT demo export untested")
    def test_ppt_entry_normal_demo_export_when_backend_available(self):
        import os
        roots = [os.environ.get("RUNTIME_NODE_MODULES"),
                 *os.environ.get("NODE_PATH", "").split(os.pathsep),
                 str(Path.cwd() / "node_modules"), str(SKILL_ROOT / "scripts/node_modules")]
        if not any((Path(root) / "@oai/artifact-tool/dist/artifact_tool.mjs").is_file() for root in roots if root):
            self.skipTest("Configured @oai/artifact-tool unavailable; actual PPT export untested (no install/environment change)")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            style = root / "style.json"
            style.write_text(json.dumps(self.task_manifest("powerpoint")), encoding="utf-8")
            output = root / "output/figure.pptx"
            command = [shutil.which("node"), str(SKILL_ROOT / "scripts/build_figure_pptx.mjs"), "--demo",
                       "--style-json", str(style), "--python", sys.executable, "--output", str(output)]
            result = subprocess.run(command, capture_output=True, text=True)
            print("PPT_ENTRY_CASE " + json.dumps(dict(case="normal-style-demo-export", command=command,
                  exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr)))
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertTrue(output.read_bytes().startswith(b"PK"))
            self.assertTrue((output.parent / "ppt_manifest.json").is_file())

    @unittest.skipUnless(shutil.which("node"), "Node unavailable; PPT entry interpreter failure untested")
    def test_ppt_entry_missing_python_fails_closed_before_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            style = root / "style.json"
            style.write_text(json.dumps(self.task_manifest("powerpoint")), encoding="utf-8")
            command = [shutil.which("node"), str(SKILL_ROOT / "scripts/build_figure_pptx.mjs"), "--demo",
                       "--style-json", str(style), "--python", str(root / "absent-python"),
                       "--output", str(root / "output" / "figure.pptx")]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("PPT style validation failed", result.stderr)
            self.assertFalse((root / "output").exists())

    def test_optional_tokens_use_existing_schema_and_keep_scientific_encodings(self):
        revised = self.merged()
        errors, _ = self.style.validate_style_manifest(revised)
        self.assertEqual([], errors)
        self.assertEqual(self.template["schema_version"], revised["schema_version"])
        for key in ("semantic_colors", "axes", "markers", "charts", "arrows", "overrides", "state"):
            self.assertEqual(self.template[key], revised[key], key)

    def test_only_actually_used_roles_are_required(self):
        compact = copy.deepcopy(self.template)
        compact["semantic_colors"] = {"baseline": "#8A8A8A", "proposed_method": "#2F5D8C"}
        self.assertEqual([], self.style.validate_style_manifest(compact, used_roles=["control", "treatment"])[0])
        self.assertTrue(self.style.validate_style_manifest(compact, used_roles=["missing_stage"])[0])
        self.assertEqual([], self.style.validate_style_manifest(self.template)[0])

    def test_no_manifest_keeps_existing_defaults_and_vector_text(self):
        defaults = self.nstyle.nature_rcparams()
        self.assertEqual(6, defaults["font.size"])
        self.assertEqual("#FFFFFF", defaults["axes.facecolor"])
        self.assertEqual("none", defaults["svg.fonttype"])
        self.assertEqual(42, defaults["pdf.fonttype"])
        selected = self.nstyle.nature_rcparams(self.merged())
        self.assertEqual(7.0, selected["font.size"])
        self.assertEqual(defaults, self.nstyle.nature_rcparams())

    def test_explicit_semantic_roles_win_over_compatibility_aliases(self):
        manifest = copy.deepcopy(self.template)
        manifest["semantic_colors"] = {"control": "#AABBCC", "baseline": "#112233",
                                       "treatment": "#445566", "proposed_method": "#778899"}
        self.assertEqual([], self.style.validate_style_manifest(manifest, used_roles=["control", "treatment"])[0])
        self.nstyle._ACTIVE_MANIFEST = manifest
        self.assertEqual("#AABBCC", self.nstyle.role_colour("control"))
        self.assertEqual("#445566", self.nstyle.role_colour("treatment"))
        self.assertEqual("#112233", self.nstyle.role_colour("baseline"))

    def test_missing_alias_role_keeps_legacy_colour_mapping(self):
        self.nstyle._ACTIVE_MANIFEST = {"semantic_colors": {"baseline": "#112233", "proposed_method": "#778899"}}
        self.assertEqual("#112233", self.nstyle.role_colour("control"))
        self.assertEqual("#778899", self.nstyle.role_colour("treatment"))
        self.nstyle._ACTIVE_MANIFEST = None
        self.assertEqual(self.nstyle.DEFAULT_ROLE_COLOURS, self.nstyle.role_colours())

    def test_invalid_semantic_colours_fail_closed(self):
        for value in (None, True, 42, {}, [], "", "None", "#abc", "#GGHHII"):
            for role in ("control", "baseline"):
                with self.subTest(value=value, role=role):
                    manifest = copy.deepcopy(self.template)
                    manifest["semantic_colors"][role] = value
                    self.assertTrue(self.style.validate_style_manifest(manifest, used_roles=["control"])[0])
                    self.nstyle._ACTIVE_MANIFEST = manifest
                    with self.assertRaises(ValueError):
                        self.nstyle.role_colour("control")

    def test_invalid_semantic_container_does_not_become_defaults(self):
        for value in (None, [], False, "invalid"):
            with self.subTest(value=value):
                manifest = copy.deepcopy(self.template)
                manifest["semantic_colors"] = value
                self.assertTrue(self.style.validate_style_manifest(manifest)[0])
                self.nstyle._ACTIVE_MANIFEST = manifest
                with self.assertRaises(ValueError):
                    self.nstyle.role_colours()

    def test_explicit_height_preserved_and_default_sizes_unchanged(self):
        for height in (175.37678, 180.0, 170.0, 80.0):
            with self.subTest(height=height):
                self.assertAlmostEqual(height, self.nstyle.figure_size("double", height)[1] * 25.4)
        for column, width in (("single", 89), ("double", 183)):
            actual = self.nstyle.figure_size(column)
            self.assertAlmostEqual(width, actual[0] * 25.4)
            self.assertAlmostEqual(width * 0.62, actual[1] * 25.4)

    def test_invalid_explicit_height_is_rejected_not_clamped(self):
        for value in (0, -1, float("nan"), float("inf"), -float("inf"), True, "invalid"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.nstyle.figure_size("double", value)

    def test_reading_locked_style_does_not_apply_optional_patch_or_write(self):
        locked = copy.deepcopy(self.template)
        locked["state"] = {"locked": True, "status": "locked"}
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "style_manifest.yaml"
            path.write_bytes(json.dumps(locked).encode("utf-8"))
            before = path.read_bytes()
            loaded = self.style.load_style_manifest(path)
            self.nstyle.nature_rcparams(loaded)
            self.assertEqual(locked, loaded)
            self.assertEqual(before, path.read_bytes())
            self.assertEqual([], self.style.validate_style_manifest(loaded)[0])

    def test_apple_label_cannot_hide_scientific_uncertainty_change(self):
        previous = base_contract()
        current = copy.deepcopy(previous)
        current["style_manifest"] = "style/apple-example.yaml"
        current["panels"][0]["uncertainty"]["meaning"] = "a different statistical interpretation"
        current["revision"] = {"change_class": "visual", "changed_refs": ["style_manifest"], "invalidated_outputs": []}
        errors = MODULE.compare_contracts(previous, current)
        self.assertTrue(any("change_class is visual" in issue for issue in errors))


class FigureMechanismRegressionTests(unittest.TestCase):
    def setUp(self):
        with patch.object(sys, "path", [str(SKILL_ROOT / "scripts"), *sys.path]):
            import make_nature_multipanel
            import qa_plot_ppt_scale
        self.plot = make_nature_multipanel
        self.scale = qa_plot_ppt_scale

    def render_calls(self, csv_text, kind="bar", **fields):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "input.csv").write_text(csv_text, encoding="utf-8")
            raw = dict(panel="a", claim="Synthetic test", data="input.csv", plot_type=kind,
                       x="x", y="y", xlabel="X", ylabel="Y", metric_definition="Synthetic value")
            raw.update(fields)
            ax = MagicMock()
            issues, audit = self.plot.plot_panel(ax, self.plot.PanelSpec.from_row(raw, 0), root, None)
            return ax, issues, audit

    def test_categorical_bar_preserves_rows_and_first_seen_order(self):
        ax, issues, audit = self.render_calls("x,y\nBeta,0.7\nAlpha,0.8\n")
        self.assertEqual([], issues)
        self.assertEqual(2, audit["plotted_row_count"])
        self.assertEqual([0.0, 1.0], ax.bar.call_args.args[0])
        self.assertEqual([0.7, 0.8], ax.bar.call_args.args[1])
        self.assertEqual(["Beta", "Alpha"], ax.set_xticklabels.call_args.args[0])

    def test_grouped_bar_matches_categories_instead_of_group_row_position(self):
        ax, issues, audit = self.render_calls("x,y,g\nA,1,one\nB,2,one\nB,3,two\n", group="g")
        self.assertEqual([], issues)
        self.assertEqual(3, audit["plotted_row_count"])
        self.assertEqual([1.2], ax.bar.call_args.args[0])

    def test_bar_keeps_declared_errorbars(self):
        ax, issues, audit = self.render_calls("x,y,e\nA,1,0.2\n", yerr="e", error_source="prescribed SD")
        self.assertEqual([], issues)
        self.assertEqual([0.2], ax.bar.call_args.kwargs["yerr"])

    def test_invalid_and_nonfinite_values_are_explicit_not_counted_as_drawn(self):
        for bad in ("", "NaN", "inf", "not-a-number"):
            with self.subTest(bad=bad):
                _, issues, audit = self.render_calls(f"x,y\n1,0.7\n{bad},0.8\n", kind="line")
                self.assertEqual(1, audit["skipped_row_count"])
                self.assertEqual(1, audit["plotted_row_count"])
                self.assertTrue(issues)

    def test_explicit_line_marker_policy_does_not_change_data(self):
        ax, issues, audit = self.render_calls("x,y\n1,0.7\n2,0.8\n", kind="line", marker="none")
        self.assertEqual([], issues)
        self.assertIsNone(ax.plot.call_args.kwargs["marker"])
        self.assertEqual([1.0, 2.0], ax.plot.call_args.args[0])
        self.assertEqual(2, audit["plotted_row_count"])

    def test_duplicate_bar_categories_report_ambiguous_aggregation(self):
        _, issues, _ = self.render_calls("x,y\nA,1\nA,2\n")
        self.assertTrue(any("duplicate categories" in item for item in issues))

    def test_histogram_does_not_require_unused_y(self):
        ax, issues, audit = self.render_calls("x\n1\n2\n", kind="hist", y="", ylabel="Count")
        self.assertEqual([], issues)
        self.assertEqual([1.0, 2.0], ax.hist.call_args.args[0])

    def layout(self):
        reference = (SKILL_ROOT / "references/plot-to-ppt-scale-contract.md").read_text("utf-8")
        return json.loads(re.search(r"```json\n(.*?)\n```", reference, re.S).group(1))

    def test_document_layout_and_legacy_alias_are_explicitly_readable(self):
        layout = self.layout()
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "layout.json"
            for legacy in (False, True):
                current = copy.deepcopy(layout)
                if legacy:
                    slide = current.pop("slide_px")
                    current["slide"] = dict(width_px=slide["width"], height_px=slide["height"])
                path.write_text(json.dumps(current), encoding="utf-8")
                parsed = self.scale.load_layout(path)
                self.assertEqual(layout["slide_px"], parsed["slide_px"])

    def test_layout_conflict_or_missing_metrics_fail_closed(self):
        for variant in ("conflict", "missing", "empty", "nonfinite_threshold"):
            current = self.layout()
            if variant == "conflict": current["slide"] = dict(width_px=100, height_px=100)
            if variant == "missing": current["panels"]["a"].pop("final_metrics_pt")
            if variant == "empty": current["panels"] = {}
            if variant == "nonfinite_threshold": current["qa_thresholds"]["minimum_final_text_pt"] = float("nan")
            with tempfile.TemporaryDirectory() as temp:
                path = Path(temp) / "layout.json"
                path.write_text(json.dumps(current), encoding="utf-8")
                with self.assertRaises((ValueError, KeyError)):
                    self.scale.load_layout(path)

    def test_relocating_identical_template_is_not_scientific_change(self):
        before = base_contract()
        before["architecture"] = {"nodes": [], "edges": [], "template_baseline": {
            "path": "old/template.pptx", "sha256": "a" * 64, "approval_ref": "owner"}}
        after = copy.deepcopy(before)
        after["architecture"]["template_baseline"]["path"] = "new/template.pptx"
        after["revision"] = dict(change_class="visual", changed_refs=["template_baseline.path"], invalidated_outputs=[])
        self.assertEqual([], MODULE.compare_contracts(before, after))
        after["architecture"]["template_baseline"]["sha256"] = "b" * 64
        self.assertTrue(MODULE.compare_contracts(before, after))

    @unittest.skipUnless(shutil.which("node"), "Node unavailable; actual PPT font helper untested")
    def test_ppt_native_font_scale_compensates_only_declared_final_width(self):
        uri = (SKILL_ROOT / "scripts/build_figure_pptx.mjs").as_uri()
        command = f"import {{fontPx,publicationScale}} from '{uri}';const s=publicationScale({{slide_size:{{width:1600}},target_publication_width_mm:183}}); console.log(JSON.stringify([fontPx({{}},'body',6.5),fontPx({{}},'body',6.5,s)*.75*s,publicationScale({{}})]));"
        completed = subprocess.run([shutil.which("node"), "--input-type=module", "-e", command], capture_output=True, text=True)
        self.assertEqual(0, completed.returncode, completed.stderr)
        values = json.loads(completed.stdout)
        self.assertAlmostEqual(6.5*96/72, values[0])
        self.assertAlmostEqual(6.5, values[1])
        self.assertEqual(1, values[2])


@unittest.skipUnless(shutil.which("node"), "Node unavailable; preview filesystem safety untested")
class PreviewSafetyRegressionTests(unittest.TestCase):
    def run_node(self, body):
        uri = (SKILL_ROOT / "scripts/build_figure_pptx.mjs").as_uri()
        with tempfile.TemporaryDirectory() as temporary:
            script = (
                "import assert from 'node:assert/strict';import fs from 'node:fs/promises';import path from 'node:path';"
                f"import {{createPreviewDirectory,writePreview}} from '{uri}';"
                "const root=process.argv[1];" + body
            )
            completed = subprocess.run([shutil.which("node"), "--input-type=module", "-e", script, temporary],
                                       capture_output=True, text=True)
            if completed.returncode == 77 and "LINK_PERMISSION_UNAVAILABLE" in completed.stderr:
                self.skipTest(completed.stderr.strip())
            self.assertEqual(0, completed.returncode, completed.stderr)

    def test_default_previews_are_unique_and_preserve_existing_preview(self):
        self.run_node("""
            const old=path.join(root,'preview');await fs.mkdir(old);
            const file=path.join(old,'slide-01.png');await fs.writeFile(file,'USER PREVIEW');
            const a=await createPreviewDirectory(root,null,1), b=await createPreviewDirectory(root,null,1);
            assert.notEqual(a.directory,b.directory);assert.notEqual(a.directory,old);
            await writePreview(a,'slide-01.png',Buffer.from('new A'));
            await writePreview(b,'slide-01.png',Buffer.from('new B'));
            assert.equal(await fs.readFile(file,'utf8'),'USER PREVIEW');
            assert.equal(await fs.readFile(path.join(a.directory,'slide-01.png'),'utf8'),'new A');
        """)

    def test_explicit_preview_conflict_stops_before_any_preview_write(self):
        self.run_node("""
            const dir=path.join(root,'chosen');await fs.mkdir(dir);
            const file=path.join(dir,'slide-02.layout.json');await fs.writeFile(file,'USER LAYOUT');
            await assert.rejects(createPreviewDirectory(root,dir,2),/refuse overwrite/);
            assert.deepEqual(await fs.readdir(dir),['slide-02.layout.json']);
            assert.equal(await fs.readFile(file,'utf8'),'USER LAYOUT');
        """)

    def test_existing_unrelated_files_and_empty_explicit_directory_are_supported(self):
        self.run_node("""
            const dir=path.join(root,'chosen');await fs.mkdir(dir);
            await fs.writeFile(path.join(dir,'readme.txt'),'USER NOTES');
            const p=await createPreviewDirectory(root,dir,1);await writePreview(p,'slide-01.png',Buffer.from('new'));
            assert.equal(await fs.readFile(path.join(dir,'readme.txt'),'utf8'),'USER NOTES');
            await assert.rejects(writePreview(p,'../escape.txt','bad'),/basename/);
        """)

    def test_file_created_after_preflight_is_not_overwritten(self):
        self.run_node("""
            const p=await createPreviewDirectory(root,null,1), f=path.join(p.directory,'slide-01.png');
            await fs.writeFile(f,'CONCURRENT EDIT');
            await assert.rejects(writePreview(p,'slide-01.png','replacement'),{code:'EEXIST'});
            assert.equal(await fs.readFile(f,'utf8'),'CONCURRENT EDIT');
        """)

    def test_preview_and_other_output_paths_must_not_collide(self):
        self.run_node("""
            const dir=path.join(root,'previews');
            for (const name of ['slide-01.png','slide-01.layout.json','deck-montage.webp']) {
                await assert.rejects(createPreviewDirectory(root,dir,1,[path.join(dir,name)]),/Output path collision/);
                assert.deepEqual(await fs.readdir(dir),[]);
            }
            const same=path.join(root,'same-output.json');
            await assert.rejects(createPreviewDirectory(root,dir,1,[same,same]),/Output path collision/);
        """)

    def test_distinct_output_paths_keep_explicit_directory_compatible(self):
        self.run_node("""
            const dir=path.join(root,'previews');
            const outputs=[path.join(dir,'figure.pptx'),path.join(dir,'ppt_manifest.json')];
            const p=await createPreviewDirectory(root,dir,1,outputs);
            await writePreview(p,'slide-01.png','new preview');
            assert.equal(await fs.readFile(path.join(dir,'slide-01.png'),'utf8'),'new preview');
            if (process.platform==='win32') {
                await assert.rejects(createPreviewDirectory(root,path.join(root,'other'),1,
                    [path.join(root,'same.json'),path.join(root,'SAME.JSON')]),/Output path collision/);
            }
        """)

    def test_output_collision_resolves_linked_parent_alias(self):
        self.run_node("""
            const target=path.join(root,'previews'), link=path.join(root,'alias');await fs.mkdir(target);
            try { await fs.symlink(target,link,process.platform==='win32'?'junction':'dir'); }
            catch(e) { if(['EPERM','EACCES','ENOTSUP'].includes(e.code)) {
                console.error('LINK_PERMISSION_UNAVAILABLE',e.code);process.exit(77); } throw e; }
            await assert.rejects(createPreviewDirectory(root,target,1,
                [path.join(link,'slide-01.layout.json')]),/Output path collision/);
            assert.deepEqual(await fs.readdir(target),[]);
        """)

    def test_dangling_output_file_link_is_not_treated_as_missing(self):
        self.run_node("""
            const dir=path.join(root,'previews');await fs.mkdir(dir);
            const link=path.join(root,'manifest.json');
            try { await fs.symlink(path.join(dir,'slide-01.layout.json'),link,'file'); }
            catch(e) { if(['EPERM','EACCES','ENOTSUP'].includes(e.code)) {
                console.error('LINK_PERMISSION_UNAVAILABLE',e.code);process.exit(77); } throw e; }
            await assert.rejects(createPreviewDirectory(root,dir,1,[link]),/Linked output file/);
            assert.deepEqual(await fs.readdir(dir),[]);
        """)

    def test_replaced_directory_identity_stops_write(self):
        self.run_node("""
            const p=await createPreviewDirectory(root,null,1);await fs.rename(p.directory,p.directory+'-saved');
            await fs.mkdir(p.directory);
            await assert.rejects(writePreview(p,'slide-01.png','bad'),/identity changed/);
            assert.deepEqual(await fs.readdir(p.directory),[]);
        """)

    def test_linked_preview_and_linked_ancestor_are_rejected(self):
        self.run_node("""
            const target=path.join(root,'target'), link=path.join(root,'linked');await fs.mkdir(target);
            try { await fs.symlink(target,link,process.platform==='win32'?'junction':'dir'); }
            catch(e) { if(['EPERM','EACCES','ENOTSUP'].includes(e.code)) {
                console.error('LINK_PERMISSION_UNAVAILABLE',e.code);process.exit(77); } throw e; }
            await assert.rejects(createPreviewDirectory(root,link,1),/linked or non-directory/);
            await assert.rejects(createPreviewDirectory(root,path.join(link,'child'),1),/linked or non-directory/);
            assert.deepEqual(await fs.readdir(target),[]);
        """)

    def test_late_linked_directory_is_rejected(self):
        self.run_node("""
            const p=await createPreviewDirectory(root,null,1), target=path.join(root,'target');await fs.mkdir(target);
            await fs.rename(p.directory,p.directory+'-saved');
            try { await fs.symlink(target,p.directory,process.platform==='win32'?'junction':'dir'); }
            catch(e) { if(['EPERM','EACCES','ENOTSUP'].includes(e.code)) {
                console.error('LINK_PERMISSION_UNAVAILABLE',e.code);process.exit(77); } throw e; }
            await assert.rejects(writePreview(p,'slide-01.png','bad'),/linked or non-directory/);
            assert.deepEqual(await fs.readdir(target),[]);
        """)


if __name__ == "__main__":
    unittest.main()
