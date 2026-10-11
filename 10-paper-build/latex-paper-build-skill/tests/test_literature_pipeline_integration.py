"""Offline integration checks; template structure is not interaction quality."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

HUB = Path(__file__).resolve().parents[2]
REVIEW = HUB / "literature-review"
PIPELINE = HUB / "latex-paper-build-skill"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LiteraturePipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.search = load("literature_search", REVIEW / "scripts/search_databases.py")
        cls.verify = load("literature_verify", REVIEW / "scripts/verify_citations.py")
        cls.pipeline = load("literature_pipeline", PIPELINE / "scripts/create_paper_pipeline.py")

    def test_optional_lane_is_lazy_and_legacy_contract_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "paper"
            args = self.pipeline.parse_args(["--project", str(root), "--title",
                                            "Qualitative theory", "--no-template"])
            self.pipeline.create_pipeline(args)
            self.assertFalse((root / "00_research_logic/literature").exists())
            self.assertFalse((root / ".research").exists())
            self.assertFalse((root / "05_manuscript_zh/figures").exists())
            self.assertEqual(json.loads((root / "paper_config.json").read_text())["schema_version"], 1)
            context = (root / "pipeline_context.md").read_text()
            self.assertIn("literature-review", context)
            self.assertIn("literature-triage-matrix", context)
            self.assertEqual(len(self.pipeline.STAGE_DIRS), 8)

    def test_duplicate_versions_preserve_counterevidence_without_mutating_input(self):
        records = [
            {"doi": "https://doi.org/10.1234/ABC", "title": "Initial",
             "year": 2020, "finding": "positive", "record_id": "R1"},
            {"doi": "doi:10.1234/abc", "title": "Correction",
             "year": 2025, "finding": "negative", "record_id": "R2"},
        ]
        before = json.dumps(records)
        grouped = self.search.deduplicate_results(records)
        self.assertEqual(len(grouped), 1)
        self.assertEqual(grouped[0]["triage_duplicate_records"][0]["finding"], "negative")
        self.assertEqual(grouped[0]["triage_duplicate_indices"], [1])
        self.assertEqual(json.dumps(records), before)
        filtered = self.search.filter_by_year(grouped, 2024, 2026)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["triage_year_state"], "pending_version_conflict")

    def test_identical_title_distinct_dois_are_not_one_study(self):
        records = [{"doi": "10.1234/a", "title": "Shared title"},
                   {"doi": "10.1234/b", "title": "Shared title"},
                   {"title": ""}, {"title": ""}]
        self.assertEqual(len(self.search.deduplicate_results(records)), 4)

    def test_unknown_year_retained_pending_not_eligible(self):
        records = [{"title": "Current", "year": 2025},
                   {"title": "Unknown", "year": None},
                   {"title": "Old", "year": 2020},
                   {"title": "Bad", "year": True}]
        result = self.search.filter_by_year(records, 2024, 2026)
        self.assertEqual([r["title"] for r in result], ["Current", "Unknown", "Bad"])
        self.assertEqual(result[1]["triage_year_state"], "pending")
        self.assertNotIn("triage_year_state", records[1])
        text = self.search.format_search_results(result, "markdown")
        self.assertEqual(text.count("**Year review**"), 2)

    def test_ordering_does_not_remove_low_or_missing_citation_records(self):
        records = [{"title": "Negative", "citations": 0},
                   {"title": "Unknown", "citations": None},
                   {"title": "Popular", "citations": 1000}]
        ranked = self.search.rank_results(records, "citations")
        self.assertEqual({r["title"] for r in ranked}, {r["title"] for r in records})
        self.assertEqual(len(ranked), 3)

    def record_cli(self, records, *options):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "records.json"
            source.write_text(json.dumps(records), encoding="utf-8")
            before = source.read_bytes()
            run = subprocess.run([sys.executable, "-X", "utf8", "-B",
                str(REVIEW / "scripts/search_databases.py"), str(source),
                "--format", "json", "--summary", *options], text=True, capture_output=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(source.read_bytes(), before)
            self.assertEqual(list(Path(directory).iterdir()), [source])
            return json.loads(run.stdout), json.loads(run.stderr)

    def test_default_example_without_year_options_reports_pending_years(self):
        records = [{"title": "Undated", "year": None},
                   {"title": "Missing"}, {"title": "Dated", "year": "2025"}]
        result, summary = self.record_cli(records, "--deduplicate")
        self.assertEqual(summary["pending_years"], [0, 1])
        self.assertEqual([r["triage_year_information_state"] for r in result],
                         ["missing", "missing", "parsed"])
        self.assertTrue(all(r["triage_year_range_state"] == "not_requested" for r in result))
        self.assertNotIn("year", result[1])
        self.assertEqual(result[2]["year"], "2025")
        self.assertIn("**Year review**", self.search.format_search_results(result, "markdown"))

    def test_empty_and_invalid_year_values_default_to_pending_without_guessing(self):
        raw = [None, "", "  ", "unknown", "202X", True, 2025.0, 0, "0000",
               "2025-01-01", [2025], {"print": 2025}]
        result, summary = self.record_cli([{"year": y} for y in raw])
        self.assertEqual(summary["pending_years"], list(range(len(raw))))
        self.assertEqual([r["year"] for r in result], raw)
        self.assertTrue(all(r["triage_year_state"] == "pending" for r in result))
        self.assertEqual(result[0]["triage_year_information_state"], "missing")
        self.assertEqual(result[3]["triage_year_information_state"], "unparseable")

    def test_start_only_filter_retains_unknown_and_inclusive_boundary(self):
        result, summary = self.record_cli([
            {"year": 2023}, {"year": 2024}, {"year": None}, {"year": 9999}],
            "--year-start", "2024")
        self.assertEqual([r["year"] for r in result], [2024, None, 9999])
        self.assertEqual(summary["pending_years"], [2])
        self.assertEqual(result[1]["triage_year_range_state"], "pending_review")

    def test_end_only_filter_retains_unknown_and_inclusive_boundary(self):
        result, summary = self.record_cli([
            {"year": 1000}, {"year": 2026}, {"year": "bad"}, {"year": 2027}],
            "--year-end", "2026")
        self.assertEqual([r["year"] for r in result], [1000, 2026, "bad"])
        self.assertEqual(summary["pending_years"], [2])

    def test_full_range_filters_known_dates_only_and_keeps_original_indices(self):
        result, summary = self.record_cli([
            {"year": 2023}, {"year": 2024}, {"year": None},
            {"year": 2026}, {"year": 2027}, {"year": "bad"}],
            "--year-start", "2024", "--year-end", "2026", "--rank", "year")
        self.assertEqual({r["triage_source_index"] for r in result}, {1, 2, 3, 5})
        self.assertEqual(set(summary["pending_years"]), {2, 5})
        self.assertEqual(result[0]["year"], 2026)

    def test_calendar_bounds_are_parsed_without_filter_not_scientifically_verified(self):
        result, summary = self.record_cli([{"year": y} for y in ["0001", 1000, "9999", "0000"]])
        self.assertEqual(summary["pending_years"], [3])
        self.assertTrue(all(r["triage_year_state"] == "parsed_not_range_filtered" for r in result[:3]))
        self.assertTrue(all(r["triage_year_information_state"] == "parsed" for r in result[:3]))

    def test_conflicting_group_is_pending_with_and_without_range(self):
        records = [{"doi": "10.1234/a", "year": 2020, "source": "Export A"},
                   {"doi": "10.1234/a", "year": 2025, "source": "Export B"}]
        for options in [(), ("--year-start", "2024"), ("--year-end", "2021"),
                        ("--year-start", "2024", "--year-end", "2026")]:
            with self.subTest(options=options):
                result, summary = self.record_cli(records, "--deduplicate", *options)
                self.assertEqual(summary["pending_years"], [0])
                self.assertEqual(result[0]["triage_year_information_state"], "conflicting")
                self.assertEqual(result[0]["year"], 2020)
                self.assertEqual(result[0]["source"], "Export A")
                self.assertEqual(result[0]["triage_duplicate_records"], [records[1]])

    def test_same_parsed_year_does_not_invent_conflict_between_string_and_integer(self):
        result, summary = self.record_cli([
            {"doi": "10.1234/a", "year": 2025, "source": "A"},
            {"doi": "10.1234/a", "year": "2025", "source": "B"}], "--deduplicate")
        self.assertEqual(summary["pending_years"], [])
        self.assertEqual(result[0]["triage_year_information_state"], "parsed")
        self.assertEqual(result[0]["triage_duplicate_records"][0]["year"], "2025")
        self.assertEqual(result[0]["triage_duplicate_review"], "pending")

    def test_known_unknown_source_disagreement_does_not_silently_resolve_year(self):
        result, summary = self.record_cli([
            {"doi": "10.1234/a", "year": 2025, "source": "A"},
            {"doi": "10.1234/a", "year": None, "source": "B"}], "--deduplicate")
        self.assertEqual(summary["pending_years"], [0])
        self.assertEqual(result[0]["triage_year_state"], "pending_version_conflict")

    def test_empty_corpus_is_not_turned_into_literature_evidence(self):
        result, summary = self.record_cli([], "--deduplicate")
        self.assertEqual(result, [])
        self.assertEqual(summary["total_results"], 0)
        self.assertEqual(summary["pending_years"], [])

    def test_record_cli_preserves_raw_input_and_emits_uncertainty(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "records.json"
            source.write_text(json.dumps([
                {"doi": "10.1234/a", "year": None, "title": "Abstract lead"},
                {"doi": "10.1234/a", "year": None, "title": "Version B"}]), encoding="utf-8")
            before = source.read_bytes()
            result = subprocess.run([sys.executable, "-X", "utf8", "-B",
                str(REVIEW / "scripts/search_databases.py"), str(source),
                "--deduplicate", "--year-start", "2024", "--format", "json", "--summary"],
                text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)[0]["triage_year_state"], "pending")
            summary = json.loads(result.stderr)
            self.assertEqual(summary["pending_years"], [0])
            self.assertEqual(summary["duplicate_groups"][0]["duplicate_indices"], [1])
            self.assertEqual(source.read_bytes(), before)
            self.assertEqual(list(Path(directory).iterdir()), [source])

    def test_both_writers_refuse_existing_output_and_preserve_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "owner.txt"
            target.write_text("owner content", encoding="utf-8")
            for module in (self.search, self.verify):
                with self.subTest(module=module.__name__):
                    with self.assertRaises(FileExistsError):
                        module.write_new_output(target, "replacement")
                    self.assertEqual(target.read_text(), "owner content")
                    fresh = Path(directory) / (module.__name__ + ".json")
                    module.write_new_output(fresh, "{}")
                    self.assertEqual(fresh.read_text(), "{}")

    def test_both_writers_reject_reparse_flag(self):
        fake_info = types.SimpleNamespace(st_mode=0o040755, st_file_attributes=0x400)
        for module in (self.search, self.verify):
            with mock.patch.object(Path, "lstat", return_value=fake_info):
                with self.assertRaisesRegex(ValueError, "reparse"):
                    module.validate_output(Path("new-result.json"))

    def test_both_writers_reject_linked_parent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            real = root / "real"
            real.mkdir()
            link = root / "link"
            try:
                link.symlink_to(real, target_is_directory=True)
            except OSError:
                self.skipTest("symlink creation unavailable on this platform")
            for module in (self.search, self.verify):
                with self.assertRaises(ValueError):
                    module.write_new_output(link / "result.json", "{}")
            self.assertFalse((real / "result.json").exists())

    def verifier(self):
        instance = self.verify.CitationVerifier.__new__(self.verify.CitationVerifier)
        instance.email = None
        instance.session = mock.Mock()
        return instance

    @unittest.skipUnless(os.name == "nt", "Windows junction semantics")
    def test_both_writers_reject_actual_junction(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            real, link = root / "real", root / "junction"
            real.mkdir()
            creation = subprocess.run(["cmd", "/d", "/c", "mklink", "/J",
                                       str(link), str(real)], capture_output=True, text=True)
            self.assertEqual(creation.returncode, 0, creation.stderr)
            for module in (self.search, self.verify):
                with self.assertRaises(ValueError):
                    module.write_new_output(link / "result.json", "{}")
            self.assertFalse((real / "result.json").exists())

    @unittest.skipUnless(os.name == "nt", "Windows junction semantics")
    def test_writers_reject_junction_even_with_parent_escape_component(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            real, link = root / "real", root / "junction"
            real.mkdir()
            creation = subprocess.run(["cmd", "/d", "/c", "mklink", "/J",
                                       str(link), str(real)], capture_output=True, text=True)
            self.assertEqual(creation.returncode, 0, creation.stderr)
            for module in (self.search, self.verify):
                with self.assertRaises(ValueError):
                    module.write_new_output(link / ".." / "escaped.json", "{}")
            self.assertFalse((root / "escaped.json").exists())

    @unittest.skipUnless(os.name == "nt", "Windows junction semantics")
    def test_generator_refuses_junction_root_and_stage_before_any_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            outside = root / "outside"
            outside.mkdir()
            for is_root in (True, False):
                with self.subTest(is_root=is_root):
                    project = root / ("alias" if is_root else "project")
                    if not is_root:
                        project.mkdir()
                    link = project if is_root else project / "00_research_logic"
                    creation = subprocess.run(["cmd", "/d", "/c", "mklink", "/J",
                        str(link), str(outside)], capture_output=True, text=True)
                    self.assertEqual(creation.returncode, 0, creation.stderr)
                    args = self.pipeline.parse_args(["--project", str(project), "--title", "Scope", "--no-template"])
                    with self.assertRaisesRegex(ValueError, "reparse"):
                        self.pipeline.create_pipeline(args)
                    self.assertEqual(list(outside.iterdir()), [])
                    self.assertFalse((project / "paper_config.json").exists())

    def test_generator_rerun_preserves_existing_frontmatter_without_force(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            args = self.pipeline.parse_args(["--project", str(project), "--title", "Scope"])
            with contextlib.redirect_stdout(io.StringIO()):
                self.pipeline.create_pipeline(args)
            manuscript = project / "05_manuscript_zh"
            self.assertIn(r"\title{Scope}", (manuscript / "frontmatter.tex").read_text(encoding="utf-8"))
            owner = {"frontmatter.tex": "owner frontmatter", "preamble.tex": "owner preamble"}
            for name, content in owner.items():
                (manuscript / name).write_text(content, encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.pipeline.create_pipeline(args)
            for name, content in owner.items():
                self.assertEqual((manuscript / name).read_text(encoding="utf-8"), content)

    def test_generator_reparse_preflight_has_no_directory_side_effect(self):
        fake_info = types.SimpleNamespace(st_mode=0o040755, st_file_attributes=0x400)
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "new-project"
            args = self.pipeline.parse_args(["--project", str(project), "--title", "Scope", "--no-template"])
            with mock.patch.object(Path, "lstat", return_value=fake_info):
                with self.assertRaisesRegex(ValueError, "reparse"):
                    self.pipeline.create_pipeline(args)
            self.assertFalse(project.exists())

    def test_registered_doi_never_establishes_claim_support(self):
        instance = self.verifier()
        responses = [mock.Mock(status_code=200), mock.Mock(status_code=200)]
        responses[0].json.return_value = {"responseCode": 1, "handle": "10.1234/a"}
        responses[1].json.return_value = {"message": {"DOI": "10.1234/a",
                                                    "title": ["Unrelated study"]}}
        with tempfile.TemporaryDirectory() as directory:
            paper = Path(directory) / "review.md"
            paper.write_text("Claim supported? DOI 10.1234/a", encoding="utf-8")
            with mock.patch.object(instance, "_get", side_effect=responses), \
                 mock.patch.object(self.verify.time, "sleep"):
                report = instance.verify_citations_in_file(str(paper))
        self.assertEqual(report["outcome"], "registration_checked")
        self.assertEqual(report["verified"], ["10.1234/a"])
        self.assertEqual(report["claim_support_state"], "unassessed")
        self.assertIn("not claim support", report["verification_scope"])
        checks = report["citation_checks"]["10.1234/a"]
        self.assertEqual(checks["doi_registration_state"], "registered")
        self.assertEqual(checks["metadata_identity_state"], "matched_doi")
        for axis in ("metadata_match_state", "claim_support_state", "retraction_state",
                     "scientific_quality_state"):
            self.assertEqual(checks[axis], "unassessed")
            self.assertEqual(report[axis], "unassessed")

    def test_registered_doi_with_unavailable_metadata_keeps_report_incomplete(self):
        instance = self.verifier()
        response = mock.Mock(status_code=200)
        response.json.return_value = {"responseCode": 1, "handle": "10.1234/a"}
        with tempfile.TemporaryDirectory() as directory:
            paper = Path(directory) / "review.md"
            paper.write_text("10.1234/a", encoding="utf-8")
            with mock.patch.object(instance, "_get", side_effect=[response, mock.Mock(status_code=503)]), \
                 mock.patch.object(self.verify.time, "sleep"):
                report = instance.verify_citations_in_file(str(paper))
        self.assertEqual(report["outcome"], "incomplete")
        self.assertEqual(report["verified"], ["10.1234/a"])
        self.assertEqual(report["metadata_unavailable"], ["10.1234/a"])
        self.assertEqual(report["citation_checks"]["10.1234/a"]["metadata_match_state"], "unassessed")

    def test_network_failure_retains_incomplete_report_and_unassessed_axes(self):
        class RequestFailure(Exception):
            pass
        instance = self.verifier()
        with tempfile.TemporaryDirectory() as directory:
            paper = Path(directory) / "review.md"
            paper.write_text("10.1234/a", encoding="utf-8")
            with mock.patch.object(self.verify, "requests", types.SimpleNamespace(RequestException=RequestFailure)), \
                 mock.patch.object(instance, "_get", side_effect=RequestFailure("offline timeout")), \
                 mock.patch.object(self.verify.time, "sleep"):
                report = instance.verify_citations_in_file(str(paper))
        self.assertEqual(report["outcome"], "incomplete")
        self.assertEqual(report["inconclusive"], ["10.1234/a"])
        self.assertEqual(report["missing"], [])
        self.assertEqual(report["citation_checks"]["10.1234/a"]["doi_registration_state"], "inconclusive")
        self.assertEqual(report["scientific_quality_state"], "unassessed")

    def test_record_cli_refuses_existing_output_before_processing(self):
        with tempfile.TemporaryDirectory() as directory:
            source, target = Path(directory) / "records.json", Path(directory) / "owner.json"
            source.write_text('[{"year":null}]', encoding="utf-8")
            target.write_text("owner bytes", encoding="utf-8")
            run = subprocess.run([sys.executable, "-X", "utf8", "-B",
                str(REVIEW / "scripts/search_databases.py"), str(source), "--output", str(target)],
                text=True, capture_output=True)
            self.assertEqual(run.returncode, 1)
            self.assertEqual(target.read_text(), "owner bytes")

    def test_both_writers_reject_dangling_symlink_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "link.json"
            missing = Path(directory) / "missing.json"
            try:
                target.symlink_to(missing)
            except OSError:
                self.skipTest("symlink creation unavailable on this platform")
            for module in (self.search, self.verify):
                with self.assertRaises(ValueError):
                    module.write_new_output(target, "{}")
            self.assertFalse(missing.exists())

    def test_both_writers_do_not_create_missing_parent_or_hide_io_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "missing" / "output.json"
            for module in (self.search, self.verify):
                with self.assertRaises(FileNotFoundError):
                    module.write_new_output(target, "{}")
            self.assertFalse(target.parent.exists())

    def test_mismatched_registered_identity_remains_unresolved(self):
        instance = self.verifier()
        response = mock.Mock(status_code=200)
        response.json.return_value = {"responseCode": 1, "handle": "10.1234/wrong"}
        with mock.patch.object(instance, "_get", return_value=response):
            registered, detail = instance.verify_doi("10.1234/a")
        self.assertFalse(registered)
        self.assertEqual(detail["status"], "inconclusive")

    def test_timeout_is_inconclusive_not_fabrication(self):
        class RequestFailure(Exception):
            pass
        instance = self.verifier()
        fake_requests = types.SimpleNamespace(RequestException=RequestFailure)
        with mock.patch.object(self.verify, "requests", fake_requests), \
             mock.patch.object(instance, "_get", side_effect=RequestFailure("timeout")):
            registered, detail = instance.verify_doi("10.1234/a")
        self.assertFalse(registered)
        self.assertEqual(detail["status"], "inconclusive")

    def test_missing_optional_dependency_preserves_offline_path(self):
        with mock.patch.object(self.verify, "requests", None):
            instance = self.verify.CitationVerifier()
            self.assertEqual(instance.extract_dois("10.1234/A"), ["10.1234/a"])
            registered, detail = instance.verify_doi("10.1234/a")
            self.assertFalse(registered)
            self.assertEqual(detail["reason"], "optional_requests_unavailable")

    def test_no_doi_cli_returns_incomplete_without_new_files(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "review.md"
            source.write_text("Historical archive with no DOI; verify manually.", encoding="utf-8")
            result = subprocess.run([sys.executable, "-X", "utf8", "-B",
                str(REVIEW / "scripts/verify_citations.py"), str(source)],
                text=True, capture_output=True)
            self.assertEqual(result.returncode, 2)
            report = json.loads(result.stdout)
            self.assertEqual(report["outcome"], "incomplete")
            self.assertEqual(report["claim_support_state"], "unassessed")
            self.assertEqual(list(Path(directory).iterdir()), [source])

    def test_unsafe_output_is_rejected_before_network(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "review.md", Path(directory) / "owner.json"
            source.write_text("DOI 10.1234/a", encoding="utf-8")
            output.write_text("owner", encoding="utf-8")
            with mock.patch.object(sys, "argv", ["verify", str(source), "--output", str(output)]), \
                 mock.patch.object(self.verify, "CitationVerifier") as verifier, \
                 contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    self.verify.main()
                self.assertEqual(raised.exception.code, 1)
                verifier.assert_not_called()
            self.assertEqual(output.read_text(), "owner")

    def test_markdown_routes_resolve_for_changed_skills_and_notices(self):
        roots = [REVIEW, HUB / "literature-triage-matrix", HUB / "research-logic-skill",
                 HUB / "experiment-design-skill", HUB / "data-analysis"]
        broken = []
        for root in roots:
            for file in root.rglob("*.md"):
                for target in re.findall(r"\[[^\]]+\]\(([^)#]+)(?:#[^)]+)?\)", file.read_text(encoding="utf-8")):
                    if target.startswith(("https://", "http://", "mailto:", "#")):
                        continue
                    if not (file.parent / target).exists():
                        broken.append((str(file), target))
        self.assertEqual(broken, [])

    def test_new_skill_layout_excludes_paid_and_pdf_generators(self):
        files = {p.name for p in (REVIEW / "scripts").glob("*.py")}
        self.assertEqual(files, {"search_databases.py", "verify_citations.py"})
        self.assertEqual(len([p for p in HUB.iterdir() if (p / "SKILL.md").is_file()]), 12)


class GoalClarificationIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pipeline = load('goal_pipeline', PIPELINE / 'scripts/create_paper_pipeline.py')

    def test_goal_templates_use_existing_artifacts_without_extra_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'paper'
            args = self.pipeline.parse_args(['--project', str(root), '--title',
                                            'Qualitative theory', '--no-template'])
            with contextlib.redirect_stdout(io.StringIO()):
                self.pipeline.create_pipeline(args)
            files = {str(p.relative_to(root)).replace('\\', '/')
                     for p in root.rglob('*') if p.is_file()}
            self.assertEqual(files, {
                'paper_config.json', 'pipeline_context.md',
                '00_research_logic/intake.md', '00_research_logic/research_logic.md',
                '01_experiment_design/experiment_plan.md',
                '06_review_gate/author_review_checklist.md',
                '07_polished_submission/build_report.md'})
            intake = (root / '00_research_logic/intake.md').read_text(encoding='utf-8')
            context = (root / 'pipeline_context.md').read_text(encoding='utf-8')
            logic = (root / '00_research_logic/research_logic.md').read_text(encoding='utf-8')
            self.assertIn('## Work Goal and Decision Source', intake)
            self.assertNotIn('## Work Goal and Decision Source', context)
            self.assertNotIn('## Work Goal and Decision Source', logic)
            self.assertIn('references/goal-clarification.md', context)
            self.assertIn('## Focal Question and Mode', logic)
            self.assertEqual(json.loads((root / 'paper_config.json').read_text())['schema_version'], 1)

    def test_legacy_goal_artifacts_preserve_raw_bytes_and_tree_without_force(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'paper'
            args = self.pipeline.parse_args(['--project', str(root), '--title',
                                            'Legacy paper', '--no-template'])
            with contextlib.redirect_stdout(io.StringIO()):
                self.pipeline.create_pipeline(args)
            for relative in ('pipeline_context.md', '00_research_logic/intake.md',
                             '00_research_logic/research_logic.md',
                             '01_experiment_design/experiment_plan.md',
                             '06_review_gate/author_review_checklist.md',
                             '07_polished_submission/build_report.md'):
                (root / relative).write_bytes(b'\xef\xbb\xbf# Owner legacy document\r\n\r\n'
                    + '只改语言，原审批保持；没有新目标字段。\r\n'.encode('utf-8'))
            before = {str(p.relative_to(root)): p.read_bytes()
                      for p in root.rglob('*') if p.is_file()}
            directories = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_dir()}
            run = subprocess.run([sys.executable, '-X', 'utf8', '-B',
                str(PIPELINE / 'scripts/create_paper_pipeline.py'), '--project', str(root),
                '--title', 'Ignored replacement title', '--no-template'],
                text=True, capture_output=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual({str(p.relative_to(root)): p.read_bytes()
                              for p in root.rglob('*') if p.is_file()}, before)
            self.assertEqual({str(p.relative_to(root)) for p in root.rglob('*') if p.is_dir()}, directories)

    def test_new_review_handoff_has_goal_authority_and_nontext_change_checks(self):
        # These are template checks only, not proof of reviewer/agent behavior.
        review = self.pipeline.review_gate_template()
        report = self.pipeline.build_report_template()
        self.assertIn('method, data, source-evidence and figure-meaning changes', review)
        self.assertIn('Author approval is separate from action authority', review)
        self.assertIn('Post-outcome amendments', review)
        self.assertIn('Authority for the proposed next action', report)

    def test_changed_goal_documents_have_resolvable_local_links(self):
        paths = [PIPELINE / 'SKILL.md', PIPELINE / 'references/paper-pipeline.md',
                 PIPELINE / 'references/goal-clarification.md',
                 HUB / 'research-logic-skill/SKILL.md', HUB / 'README.md',
                 HUB / 'README.en.md', HUB / 'THIRD_PARTY_NOTICES.md']
        broken = []
        for file in paths:
            for target in re.findall(r'\[[^\]]+\]\(([^)#]+)(?:#[^)]+)?\)',
                                     file.read_text(encoding='utf-8')):
                if target.startswith(('https://', 'http://', 'mailto:', '#')):
                    continue
                if not (file.parent / target).exists():
                    broken.append((str(file), target))
        self.assertEqual(broken, [])

    def test_bilingual_navigation_keeps_counts_and_heading_levels_aligned(self):
        chinese = (HUB / 'README.md').read_text(encoding='utf-8')
        english = (HUB / 'README.en.md').read_text(encoding='utf-8')
        heading_levels = lambda text: [len(m) for m in re.findall(r'^(#+) ', text, re.M)]
        self.assertEqual(heading_levels(chinese), heading_levels(english))
        for text in (chinese, english):
            self.assertEqual(text.count('(latex-paper-build-skill/references/goal-clarification.md)'), 1)
        self.assertEqual(len([p for p in HUB.iterdir() if (p / 'SKILL.md').is_file()]), 12)


if __name__ == "__main__":
    unittest.main()
