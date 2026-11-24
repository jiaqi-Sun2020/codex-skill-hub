"""Mechanism tests; these do not establish natural-language/scientific quality."""
import copy
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[2] / 'paper-project-initializer/scripts/initialize_paper_project.py'
spec = importlib.util.spec_from_file_location('paper_initializer', SCRIPT)
init = importlib.util.module_from_spec(spec)
spec.loader.exec_module(init)


class PaperInitializationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='paper-init-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.inputs = dict(title='unknown', work_goal='Compare supplied abstracts',
                           acceptance='Traceable comparison; uncertainty retained',
                           goal_source='user-request/1', formal_goal_ref='', intake_ref='',
                           references=[], start_stage='0', next_action='Read supplied abstracts')

    def plan(self):
        return init.preview(str(self.root), self.inputs)

    def apply(self, plan=None, prior=None):
        plan = plan or self.plan()
        return init.apply(plan, plan['plan_sha256'], 'user-request/scoped-entry-write', prior)

    def test_preview_stable_and_readonly(self):
        self.assertEqual(self.plan(), self.plan())
        self.assertEqual(list(self.root.iterdir()), [])
        self.assertFalse(init.inspect(str(self.root))['writes'])

    def test_minimal_creation_no_config_or_other_stages(self):
        result = self.apply()
        self.assertEqual(result['status'], 'paper_entries_checked', result)
        files = {p.relative_to(self.root).as_posix() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(files, set(init.TARGETS))
        text = (self.root / init.TARGETS[0]).read_text()
        for unwanted in ('PRA', 'Quantum', 'example@author'):
            self.assertNotIn(unwanted, text)
        self.assertEqual(result['agent_hook_memory'], 'not operated')

    def test_existing_custom_bytes_and_manuscript_preserved(self):
        original = b'\xef\xbb\xbf# Owner goal\r\n'
        for p in ('pipeline_context.md', 'AGENTS.md', 'main.tex'):
            (self.root / p).write_bytes(original)
        result = self.apply()
        self.assertEqual(result['status'], 'paper_entries_checked', result)
        for p in ('pipeline_context.md', 'AGENTS.md', 'main.tex'):
            self.assertEqual((self.root / p).read_bytes(), original)

    def test_equivalent_entry_is_referenced_not_copied(self):
        (self.root / 'owner-goal.md').write_text('Approved custom goal', encoding='utf-8')
        self.inputs['intake_ref'] = 'owner-goal.md'
        self.assertEqual(self.apply()['status'], 'paper_entries_checked')
        self.assertFalse((self.root / init.TARGETS[0]).exists())
        self.assertIn('owner-goal.md', (self.root / init.TARGETS[1]).read_text())

    def test_formal_goal_is_pointer_not_competing_goal(self):
        (self.root / 'contract.md').write_text('Approved scope', encoding='utf-8')
        self.inputs['formal_goal_ref'] = 'contract.md'
        self.assertEqual(self.apply()['status'], 'paper_entries_checked')
        text = (self.root / init.TARGETS[0]).read_text()
        self.assertIn('contract.md', text)
        self.assertNotIn(self.inputs['work_goal'], text)

    def test_repeat_preserves_identity(self):
        plan = self.plan()
        first = self.apply(plan)
        self.assertEqual(first['status'], 'paper_entries_checked', first)
        states = {p: init.snapshot(self.root / p) for p in init.TARGETS}
        self.assertEqual(self.apply(plan, first)['status'], 'paper_entries_checked')
        self.assertEqual(states, {p: init.snapshot(self.root / p) for p in init.TARGETS})
        self.assertEqual(self.apply()['status'], 'paper_entries_checked')

    def test_partial_then_same_plan_resume(self):
        plan = self.plan()
        real_link = os.link
        count = 0

        def fail_second(src, dst):
            nonlocal count
            count += 1
            if count == 2:
                raise OSError('simulated second publication failure')
            return real_link(src, dst)

        with patch.object(init.os, 'link', side_effect=fail_second):
            first = self.apply(plan)
        self.assertEqual(first['status'], 'partial', first)
        self.assertEqual(set(first['completed']), {init.TARGETS[0]})
        before = init.snapshot(self.root / init.TARGETS[0])
        resumed = self.apply(plan, first)
        self.assertEqual(resumed['status'], 'paper_entries_checked', resumed)
        self.assertEqual(init.snapshot(self.root / init.TARGETS[0]), before)

    def test_directory_only_partial_can_resume_same_plan(self):
        plan = self.plan()
        with patch.object(init.os, 'link', side_effect=OSError('first publication interrupted')):
            first = self.apply(plan)
        self.assertEqual(first['status'], 'partial', first)
        self.assertEqual(first['completed'], {})
        self.assertEqual(set(first['directories']), {'00_research_logic'})
        parent = init.snapshot(self.root / '00_research_logic')
        resumed = self.apply(plan, first)
        self.assertEqual(resumed['status'], 'paper_entries_checked', resumed)
        self.assertEqual(parent, init.snapshot(self.root / '00_research_logic'))

    def test_receipt_cannot_complete_an_absent_target(self):
        plan = self.plan()
        prior = dict(version=init.VERSION + '/receipt', plan_sha256=plan['plan_sha256'],
                     completed={init.TARGETS[1]: {'kind': 'absent'}}, directories={})
        result = self.apply(plan, prior)
        self.assertEqual(result['status'], 'blocked', result)
        self.assertEqual(result['completed'], {})
        self.assertEqual(list(self.root.iterdir()), [])

    def test_receipt_cannot_accept_wrong_content_even_with_current_identity(self):
        plan = self.plan()
        prior = self.apply(plan)
        target = self.root / init.TARGETS[1]
        target.write_bytes(b'foreign changed content')
        prior['completed'][init.TARGETS[1]] = init.snapshot(target)
        result = self.apply(plan, prior)
        self.assertEqual(result['status'], 'blocked', result)
        self.assertEqual(result['completed'], {})
        self.assertEqual(target.read_bytes(), b'foreign changed content')

    def test_receipt_extra_targets_or_malformed_progress_are_blocked(self):
        plan = self.plan()
        prior = self.apply(plan)
        states = {p: init.snapshot(self.root / p) for p in init.TARGETS}
        for key, value in [('completed', {'../outside.md': {'kind': 'file'}}),
                           ('directories', {'other': {'kind': 'directory'}}),
                           ('completed', []), ('directories', [])]:
            with self.subTest(key=key, value=value):
                altered = copy.deepcopy(prior)
                altered[key] = value
                result = self.apply(plan, altered)
                self.assertEqual(result['status'], 'blocked', result)
                self.assertEqual(result['completed'], {})
                self.assertEqual(states, {p: init.snapshot(self.root / p) for p in init.TARGETS})

    def test_receipt_cannot_claim_reference_or_preexisting_parent_as_created(self):
        (self.root / '00_research_logic').mkdir()
        (self.root / init.TARGETS[0]).write_bytes(b'owner intake')
        (self.root / init.TARGETS[1]).write_bytes(b'owner context')
        plan = self.plan()
        prior = dict(version=init.VERSION + '/receipt', plan_sha256=plan['plan_sha256'],
                     completed={}, directories={})
        for key, value in [('completed', {init.TARGETS[0]: init.snapshot(self.root / init.TARGETS[0])}),
                           ('directories', {'00_research_logic': init.snapshot(self.root / '00_research_logic')})]:
            with self.subTest(key=key):
                altered = copy.deepcopy(prior)
                altered[key] = value
                self.assertEqual(self.apply(plan, altered)['status'], 'blocked')
        self.assertEqual((self.root / init.TARGETS[0]).read_bytes(), b'owner intake')

    def test_receipt_parent_must_be_a_current_matching_directory(self):
        plan = self.plan()
        prior = self.apply(plan)
        for value in ({'kind': 'absent'}, dict(prior['directories']['00_research_logic'], ino='0')):
            with self.subTest(value=value):
                altered = copy.deepcopy(prior)
                altered['directories']['00_research_logic'] = value
                self.assertEqual(self.apply(plan, altered)['status'], 'blocked')

    def test_reference_only_checks_do_not_require_publication_support(self):
        (self.root / '00_research_logic').mkdir()
        for p in init.TARGETS:
            (self.root / p).write_bytes(b'\xef\xbb\xbf# Owner entry\r\n')
        plan = self.plan()
        states = {p: init.snapshot(self.root / p) for p in init.TARGETS}
        self.assertTrue(all(row['action'] == 'reference' for row in plan['targets']))
        for row in plan['targets']:
            self.assertEqual(row['before'], states[row['path']])
            self.assertNotEqual(row['sha256'], row['before']['sha256'])  # unused v1 candidate
        with patch.object(init, 'filesystem', side_effect=AssertionError('No publication')):
            result = self.apply(plan)
        self.assertEqual(result['status'], 'paper_entries_checked', result)
        self.assertEqual(states, {p: init.snapshot(self.root / p) for p in init.TARGETS})

    def test_all_completed_checks_do_not_require_publication_support(self):
        plan = self.plan()
        prior = self.apply(plan)
        with patch.object(init, 'filesystem', side_effect=AssertionError('No publication')):
            self.assertEqual(self.apply(plan, prior)['status'], 'paper_entries_checked')

    def test_missing_receipt_is_unknown_not_overwritten(self):
        plan = self.plan()
        self.apply(plan)
        result = self.apply(plan)
        self.assertEqual(result['status'], 'blocked')
        self.assertIn('Unknown', result['error'])

    def test_completed_modified_stops(self):
        plan = self.plan()
        receipt = self.apply(plan)
        (self.root / init.TARGETS[0]).write_bytes(b'owner changed content')
        result = self.apply(plan, receipt)
        self.assertNotEqual(result['status'], 'paper_entries_checked')
        self.assertEqual((self.root / init.TARGETS[0]).read_bytes(), b'owner changed content')

    def test_source_changed_stops(self):
        (self.root / 'README.md').write_text('v1', encoding='utf-8')
        plan = self.plan()
        (self.root / 'README.md').write_text('v2', encoding='utf-8')
        self.assertEqual(self.apply(plan)['status'], 'blocked')
        self.assertFalse((self.root / init.TARGETS[0]).exists())

    def test_no_authority_stops(self):
        plan = self.plan()
        result = init.apply(plan, plan['plan_sha256'], '')
        self.assertEqual(result['status'], 'blocked')
        self.assertEqual(list(self.root.iterdir()), [])

    def test_input_or_content_tamper_rejected(self):
        plan = self.plan()
        altered = copy.deepcopy(plan)
        altered['inputs']['next_action'] = 'Changed action'
        self.assertEqual(self.apply(altered)['status'], 'blocked')
        altered = copy.deepcopy(plan)
        altered['targets'][0]['content_base64'] = 'eA=='
        altered['plan_sha256'] = init.digest(init.canonical({k: v for k, v in altered.items() if k != 'plan_sha256'}))
        self.assertEqual(self.apply(altered)['status'], 'blocked')

    def test_extra_target_rejected_even_rehashed(self):
        plan = self.plan()
        plan['targets'][0]['path'] = '../escape.md'
        plan['plan_sha256'] = init.digest(init.canonical({k: v for k, v in plan.items() if k != 'plan_sha256'}))
        self.assertEqual(self.apply(plan)['status'], 'blocked')

    def test_changed_tool_rejected(self):
        plan = self.plan()
        fake = copy.deepcopy(plan['tools'])
        fake['template']['sha256'] = '0' * 64
        with patch.object(init, 'tools', return_value=fake), patch.object(init, 'render') as renderer:
            self.assertEqual(self.apply(plan)['status'], 'blocked')
            renderer.assert_not_called()
        self.assertEqual(list(self.root.iterdir()), [])

    def test_tool_change_after_early_check_still_blocks_publication(self):
        plan = self.plan()
        fake = copy.deepcopy(plan['tools'])
        fake['template']['sha256'] = '0' * 64
        calls = 0

        def changed_after_first_check():
            nonlocal calls
            calls += 1
            return plan['tools'] if calls == 1 else fake

        with patch.object(init, 'tools', side_effect=changed_after_first_check), \
                patch.object(init.os, 'link') as linker:
            self.assertEqual(self.apply(plan)['status'], 'blocked')
            linker.assert_not_called()
        self.assertEqual(list(self.root.iterdir()), [])

    def test_unknown_year_or_science_not_inferred(self):
        self.inputs.update(title='unknown', work_goal='Qualitative negative result',
                           acceptance='Document evidence gaps', next_action='Clarify missing source')
        self.assertEqual(self.apply()['research_readiness'], 'unreviewed')
        self.assertFalse((self.root / 'paper_config.json').exists())

    def test_publication_collision_does_not_overwrite(self):
        target = self.root / 'pipeline_context.md'
        real_link = os.link

        def race(src, dst):
            Path(dst).write_bytes(b'concurrent owner content')
            return real_link(src, dst)

        with patch.object(init.os, 'link', side_effect=race):
            result = self.apply()
        self.assertNotEqual(result['status'], 'paper_entries_checked')
        self.assertEqual((self.root / init.TARGETS[0]).read_bytes(), b'concurrent owner content')
        self.assertFalse(target.exists())

    def test_unsupported_link_no_fallback(self):
        with patch.object(init.os, 'link', side_effect=OSError('unsupported')):
            result = self.apply()
        self.assertEqual(result['status'], 'partial')
        self.assertFalse(any((self.root / p).exists() for p in init.TARGETS))

    def test_unsupported_filesystem_stops_before_mkdir(self):
        with patch.object(init, 'filesystem', side_effect=init.Blocked('unverified filesystem')):
            result = self.apply()
        self.assertEqual(result['status'], 'blocked')
        self.assertEqual(list(self.root.iterdir()), [])

    def test_relative_escape_absolute_sensitive_and_alias_paths(self):
        for path in ('../outside', str(self.root / 'absolute'), '.env', 'credentials.json'):
            with self.assertRaises(init.Blocked):
                init.contained(self.root, path)
        (self.root / 'alias').mkdir()
        plan = init.preview(str(self.root / 'alias/..'), self.inputs)
        self.assertEqual(plan['root'], str(self.root.resolve()))

    def test_chinese_long_path(self):
        nested = self.root / ('论文项目' * 20) / ('文献材料' * 20) / ('阶段入口' * 20)
        self.assertGreater(len(str(nested)), 260)
        try:
            nested.mkdir(parents=True)
        except OSError as error:
            if os.name != 'nt' or getattr(error, 'winerror', None) not in (3, 206):
                raise
            # This machine cannot create >260 paths. Verify explicit safe refusal,
            # not successful long-path support; do not change Windows settings.
            result = subprocess.run([sys.executable, '-X', 'utf8', '-B', str(SCRIPT),
                                     'inspect', '--project', str(nested)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('"status": "blocked"', result.stdout)
            self.assertFalse(any(p.is_file() for p in self.root.rglob('*')))
            return
        plan = init.preview(str(nested), self.inputs)
        result = init.apply(plan, plan['plan_sha256'], 'scoped user approval')
        self.assertEqual(result['status'], 'paper_entries_checked', result)

    def test_same_bytes_replaced_identity_stops(self):
        plan = self.plan()
        receipt = self.apply(plan)
        target = self.root / init.TARGETS[0]
        data = target.read_bytes()
        replacement = target.with_name('replacement')
        replacement.write_bytes(data)
        os.replace(replacement, target)
        self.assertNotEqual(self.apply(plan, receipt)['status'], 'paper_entries_checked')
        self.assertEqual(target.read_bytes(), data)

    def test_cleanup_preserves_replaced_temp(self):
        real_link = os.link

        def replace_temporary(src, dst):
            real_link(src, dst)
            Path(src).unlink()
            Path(src).write_bytes(b'foreign temporary content')

        with patch.object(init.os, 'link', side_effect=replace_temporary):
            result = self.apply()
        self.assertEqual(result['status'], 'paper_entries_checked', result)
        remaining = list(self.root.rglob('.pi-*'))
        self.assertEqual(len(remaining), 2)
        self.assertTrue(all(p.read_bytes() == b'foreign temporary content' for p in remaining))

    def test_cleanup_failure_preserves_completion_and_same_plan_resume(self):
        real_unlink = Path.unlink
        for existing_parent in (False, True):
            for failed_cleanup in (1, 2):
                with self.subTest(existing_parent=existing_parent, failed_cleanup=failed_cleanup):
                    root = self.root / ('cleanup-' + str(existing_parent) + '-' + str(failed_cleanup))
                    root.mkdir()
                    if existing_parent:
                        (root / '00_research_logic').mkdir()
                    plan = init.preview(str(root), self.inputs)
                    cleanups = 0

                    def deny_owned_cleanup(path, *args, **kwargs):
                        nonlocal cleanups
                        if path.name.startswith('.pi-'):
                            cleanups += 1
                            if cleanups == failed_cleanup:
                                raise PermissionError('simulated owned-temp cleanup failure')
                        return real_unlink(path, *args, **kwargs)

                    with patch.object(Path, 'unlink', deny_owned_cleanup):
                        first = init.apply(plan, plan['plan_sha256'], 'scoped cleanup test approval')
                    self.assertEqual(first['status'], 'partial', first)
                    self.assertIn('temporary cleanup failed', first['error'])
                    self.assertEqual(set(first['completed']), set(init.TARGETS[:failed_cleanup]))
                    states = {p: init.snapshot(root / p) for p in first['completed']}
                    remaining = {p: init.snapshot(p) for p in root.rglob('.pi-*')}
                    self.assertEqual(len(remaining), 1)
                    resumed = init.apply(plan, plan['plan_sha256'], 'scoped cleanup test approval', first)
                    self.assertEqual(resumed['status'], 'paper_entries_checked', resumed)
                    self.assertEqual(states, {p: init.snapshot(root / p) for p in states})
                    self.assertEqual(remaining, {p: init.snapshot(p) for p in remaining})

    def test_cleanup_failure_receipt_cannot_hide_changed_final_file(self):
        plan = self.plan()
        with patch.object(Path, 'unlink', side_effect=PermissionError('simulated cleanup denial')):
            first = self.apply(plan)
        target = self.root / init.TARGETS[0]
        target.write_bytes(b'owner edit after interrupted cleanup')
        result = self.apply(plan, first)
        self.assertEqual(result['status'], 'blocked', result)
        self.assertEqual(result['completed'], {})
        self.assertEqual(target.read_bytes(), b'owner edit after interrupted cleanup')
        self.assertFalse((self.root / init.TARGETS[1]).exists())

    def test_cleanup_failure_before_publication_cannot_claim_completion(self):
        plan = self.plan()
        with patch.object(init.os, 'link', side_effect=OSError('publication denied')), \
                patch.object(Path, 'unlink', side_effect=PermissionError('cleanup also denied')):
            first = self.apply(plan)
        self.assertEqual(first['status'], 'partial', first)  # only parent creation succeeded
        self.assertEqual(first['completed'], {})
        self.assertFalse(any((self.root / p).exists() for p in init.TARGETS))
        self.assertEqual(self.apply(plan, first)['status'], 'paper_entries_checked')

    def test_unknown_version_and_command_data_rejected(self):
        for field, value in [('version', 'unknown/v2'), ('command', 'execute me')]:
            plan = self.plan()
            plan[field] = value
            plan['plan_sha256'] = init.digest(init.canonical({k: v for k, v in plan.items() if k != 'plan_sha256'}))
            self.assertEqual(self.apply(plan)['status'], 'blocked')
            self.assertEqual(list(self.root.iterdir()), [])

    def test_cli_preview_apply_and_permission_failure(self):
        import json
        command = [sys.executable, '-X', 'utf8', '-B', str(SCRIPT)]
        flags = ['preview', '--project', str(self.root), '--work-goal', 'Review supplied evidence',
                 '--acceptance', 'Keep unknowns', '--goal-source', 'user/1',
                 '--start-stage', '0', '--next-action', 'Inventory gaps']
        preview = subprocess.run(command + flags, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(preview.returncode, 0, preview.stderr)
        plan = json.loads(preview.stdout)
        apply_flags = ['apply', '--plan', '-', '--confirm-plan-sha256', plan['plan_sha256'], '--authority-ref', '']
        refused = subprocess.run(command + apply_flags, input=preview.stdout, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(refused.returncode, 2)
        self.assertEqual(list(self.root.iterdir()), [])
        apply_flags[-1] = 'original-isolated-write-approval'
        result = subprocess.run(command + apply_flags, input=preview.stdout, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_packet_reads_preserve_utf8_bom_and_reject_oversize_before_open(self):
        packet = self.root / 'packet.json'
        packet.write_bytes(b'\xef\xbb\xbf' + '{"title":"论文"}\r\n'.encode('utf-8'))
        self.assertEqual(init.read_packet_file(str(packet)), '{"title":"论文"}\r\n')
        with patch.object(init, 'LIMIT', 8), patch.object(init.os, 'open', side_effect=AssertionError('Must not read')):
            with self.assertRaises(init.Blocked):
                init.read_packet_file(str(packet))

    def test_packet_reads_reject_directories_and_changes_during_read(self):
        with self.assertRaises(init.Blocked):
            init.read_packet_file(str(self.root))
        packet = self.root / 'packet.json'
        packet.write_bytes(b'{}')
        before = packet.stat()
        from types import SimpleNamespace
        changed = SimpleNamespace(st_dev=before.st_dev, st_ino=before.st_ino,
                                  st_mtime_ns=before.st_mtime_ns + 1, st_size=before.st_size)
        with patch.object(init.os, 'fstat', side_effect=[before, changed]):
            with self.assertRaises(init.Blocked):
                init.read_packet_file(str(packet))

    def test_cli_rejects_oversized_receipt_without_creating_entries(self):
        import json
        plan = self.plan()
        receipt = self.root / 'receipt.json'
        receipt.write_bytes(b' ' * (init.LIMIT + 1))
        result = subprocess.run([sys.executable, '-X', 'utf8', '-B', str(SCRIPT),
                                 'apply', '--plan', '-', '--confirm-plan-sha256', plan['plan_sha256'],
                                 '--authority-ref', 'scoped simulated approval', '--receipt', str(receipt)],
                                input=json.dumps(plan), capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertFalse(any((self.root / p).exists() for p in init.TARGETS))

    def test_symlink_rejected(self):
        try:
            (self.root / '00_research_logic').symlink_to(self.root, target_is_directory=True)
        except OSError as error:
            self.skipTest('Symlink permission unavailable: ' + str(error))
        with self.assertRaises(init.Blocked):
            self.plan()

    @unittest.skipUnless(os.name == 'nt', 'Windows junction only')
    def test_junction_rejected(self):
        link = self.root / '00_research_logic'
        other = self.root / 'other'
        other.mkdir()
        result = subprocess.run(['cmd', '/c', 'mklink', '/J', str(link), str(other)], capture_output=True)
        if result.returncode:
            self.skipTest('Junction unavailable: ' + result.stderr.decode(errors='replace'))
        self.addCleanup(link.rmdir)
        with self.assertRaises(init.Blocked):
            self.plan()
        (other / 'packet.json').write_bytes(b'{}')
        with self.assertRaises(init.Blocked):
            init.read_packet_file(str(link / 'packet.json'))

    def test_cli_inspect_and_unauthorized_apply(self):
        result = subprocess.run([sys.executable, '-X', 'utf8', '-B', str(SCRIPT), 'inspect',
                                 '--project', str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"writes": false', result.stdout)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_old_python_clear_refusal(self):
        import contextlib
        import io
        stream = io.StringIO()
        with patch.object(init.sys, 'version_info', (3, 8)), contextlib.redirect_stdout(stream):
            self.assertEqual(init.main(), 2)
        self.assertIn('Python 3.11+', stream.getvalue())

    def test_identity_json_is_lossless_across_numeric_limited_tools(self):
        import json
        (self.root / 'README.md').write_bytes(b'owner rules')
        state = init.snapshot(self.root / 'README.md')
        for key in ('dev', 'ino', 'mtime_ns'):
            self.assertIsInstance(state[key], str)
            self.assertEqual(state[key], str(int(state[key])))
        plan = self.plan()
        transported = json.loads(json.dumps(plan))
        self.assertEqual(plan['plan_sha256'], transported['plan_sha256'])
        self.assertEqual(self.apply(transported)['status'], 'paper_entries_checked')

    def test_nonobject_packet_and_receipt_rejected(self):
        self.assertEqual(init.apply([], '', '')['status'], 'blocked')
        self.assertEqual(self.apply(self.plan(), prior=['not a receipt'])['status'], 'blocked')
        self.assertEqual(list(self.root.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
