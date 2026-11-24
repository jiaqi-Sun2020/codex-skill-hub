#!/usr/bin/env python3
"""Read-only discovery and hash-bound, create-only paper entry initialization."""
from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import uuid

VERSION = 'paper-project-initialization/v1'
TARGETS = ('00_research_logic/intake.md', 'pipeline_context.md')
RULES = ('AGENTS.md', 'CLAUDE.md', '.agents/AGENTS.md', 'README.md')
INPUT_KEYS = {'title', 'work_goal', 'acceptance', 'goal_source', 'formal_goal_ref',
              'intake_ref', 'references', 'start_stage', 'next_action'}
LIMIT = 2 * 1024 * 1024


class Blocked(ValueError):
    pass


class PublishedCleanupFailure(OSError):
    """Preserve verified publication progress when owned-temp cleanup fails."""

    def __init__(self, completed: dict, error: Exception):
        super().__init__('Published entry retained; temporary cleanup failed: ' + str(error))
        self.completed = completed


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':')).encode('utf-8')


def check_raw(path: Path) -> None:
    """Check lexical ancestors BEFORE resolving aliases or .. ."""
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        try:
            info = current.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise Blocked('Linked/reparse path: ' + str(current))


def project_root(value: str) -> Path:
    raw = Path(os.path.abspath(value)) if '..' not in Path(value).parts else Path(value)
    if not raw.is_absolute():
        raw = Path.cwd() / raw
    check_raw(raw)
    root = raw.resolve(strict=True)
    if not root.is_dir():
        raise Blocked('An existing project directory is required; directory creation is separate.')
    return root


def contained(root: Path, relative: str) -> Path:
    p = Path(relative)
    if p.is_absolute() or p.drive or '..' in p.parts or not p.parts or ':' in relative:
        raise Blocked('Expected a project-contained relative path: ' + relative)
    if any(part.lower() in {'.env', '.aws'} or any(word in part.lower()
           for word in ('credential', 'password', 'private_key', 'secret', 'token')) for part in p.parts):
        raise Blocked('Sensitive path not inspected: ' + relative)
    raw = root / p
    check_raw(raw)
    resolved = raw.resolve()
    if not resolved.is_relative_to(root):
        raise Blocked('Outside project: ' + relative)
    return resolved


def snapshot(path: Path) -> dict:
    check_raw(path)
    try:
        info = path.lstat()
    except FileNotFoundError:
        return {'kind': 'absent'}
    # Windows file IDs and nanoseconds exceed JavaScript's exact integer range.
    # Preserve identity across JSON tools rather than rounding a recovery packet.
    identity = {'dev': str(info.st_dev), 'ino': str(info.st_ino)}
    if stat.S_ISDIR(info.st_mode):
        return {'kind': 'directory', **identity}
    if not stat.S_ISREG(info.st_mode) or info.st_size > LIMIT:
        raise Blocked('Not a bounded regular input file: ' + str(path))
    data = path.read_bytes()
    after = path.lstat()
    if (info.st_dev, info.st_ino, info.st_mtime_ns, info.st_size) != (
            after.st_dev, after.st_ino, after.st_mtime_ns, after.st_size):
        raise Blocked('Input changed while reading: ' + str(path))
    return {'kind': 'file', **identity, 'bytes': len(data), 'sha256': digest(data),
            'mtime_ns': str(info.st_mtime_ns)}


def read_packet_file(value: str) -> str:
    """Bound packet/receipt reads, including approved external temporary files."""
    raw = Path(value)
    if not raw.is_absolute():
        raw = Path.cwd() / raw
    check_raw(raw)
    before = raw.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_size > LIMIT:
        raise Blocked('Not a bounded regular packet/receipt file: ' + str(raw))

    def identity(info):
        return (info.st_dev, info.st_ino, info.st_mtime_ns, info.st_size)

    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0)
    with os.fdopen(os.open(raw, flags), 'rb') as stream:
        if identity(os.fstat(stream.fileno())) != identity(before):
            raise Blocked('Packet/receipt changed before reading')
        data = stream.read(LIMIT + 1)
        if len(data) > LIMIT:
            raise Blocked('Packet/receipt too large')
        after = os.fstat(stream.fileno())
    check_raw(raw)
    if identity(before) != identity(after) or identity(before) != identity(raw.lstat()):
        raise Blocked('Packet/receipt changed while reading')
    return data.decode('utf-8-sig')


def tools() -> dict:
    here = Path(__file__).resolve()
    paper = here.parents[2] / 'latex-paper-build-skill'
    paths = {'initializer': here, 'template': paper / 'scripts/create_paper_pipeline.py',
             'goal_protocol': paper / 'references/goal-clarification.md'}
    for path in paths.values():
        check_raw(path)
    return {name: {'path': str(path), 'sha256': digest(path.read_bytes())}
            for name, path in paths.items()}


def render(inputs: dict) -> dict:
    if set(inputs) != INPUT_KEYS or not isinstance(inputs['references'], list):
        raise Blocked('Unknown or missing input fields')
    for key in INPUT_KEYS - {'references'}:
        if not isinstance(inputs[key], str) or len(inputs[key]) > 16000:
            raise Blocked('Invalid input: ' + key)
    if not all(isinstance(p, str) for p in inputs['references']):
        raise Blocked('References must be paths')
    if not all(inputs[k].strip() for k in ('work_goal', 'acceptance', 'goal_source', 'next_action')):
        raise Blocked('Goal/source, acceptance and next action must be explicit; unknown is allowed.')
    if inputs['start_stage'] not in tuple(str(i) for i in range(8)):
        raise Blocked('Use an existing stage 0 through 7')
    path = Path(tools()['template']['path'])
    spec = importlib.util.spec_from_file_location('paper_initialization_templates', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.initialization_entries(inputs)


def inspect(root_value: str) -> dict:
    root = project_root(root_value)
    entries = {p: snapshot(contained(root, p)) for p in TARGETS}
    rules = {p: snapshot(contained(root, p)) for p in RULES}
    present = sum(s['kind'] == 'file' for s in entries.values())
    return {'root': str(root), 'entries': entries, 'rules': rules,
            'entry_state': ('present' if present == 2 else 'partial_or_unknown' if present else 'absent'),
            'history': 'Not inferred from missing files',
            'agent_framework': snapshot(contained(root, '.agents/AGENTS.md')),
            'writes': False}


def preview(root_value: str, inputs: dict) -> dict:
    root = project_root(root_value)
    content = render(inputs)
    refs = set(RULES) | set(inputs['references'])
    refs.update(p for p in (inputs['formal_goal_ref'], inputs['intake_ref']) if p)
    sources = {p: snapshot(contained(root, p)) for p in sorted(refs) if p not in TARGETS}
    for p in (inputs['formal_goal_ref'], inputs['intake_ref']):
        if p and snapshot(contained(root, p))['kind'] != 'file':
            raise Blocked('Referenced authority/entry was not located: ' + p)
    targets = []
    for p in TARGETS:
        before = snapshot(contained(root, p))
        if before['kind'] not in ('file', 'absent'):
            raise Blocked('Entry path is not a file or missing: ' + p)
        data = content[p].encode('utf-8')
        targets.append({'path': p, 'before': before,
                        'action': 'reference' if before['kind'] == 'file' or (p == TARGETS[0] and inputs['intake_ref']) else 'create',
                        'content_base64': base64.b64encode(data).decode('ascii'),
                        'bytes': len(data), 'sha256': digest(data)})
    plan = {'version': VERSION, 'input_version': 1, 'root': str(root),
            'root_state': snapshot(root), 'inputs': inputs, 'tools': tools(), 'sources': sources,
            'parents': {'00_research_logic': snapshot(contained(root, '00_research_logic'))},
            'targets': targets, 'scope': 'two paper entries only; no Agent/Hook/memory operations'}
    plan['plan_sha256'] = digest(canonical(plan))
    return plan


def filesystem(root: Path) -> None:
    """Conservative platform support; no install or privilege changes."""
    if os.name == 'nt':
        import ctypes
        volume = ctypes.create_unicode_buffer(32768)
        fs = ctypes.create_unicode_buffer(64)
        kernel = ctypes.windll.kernel32
        if not kernel.GetVolumePathNameW(str(root), volume, len(volume)):
            raise Blocked('Cannot identify publication volume')
        if kernel.GetDriveTypeW(volume.value) not in (2, 3) or not kernel.GetVolumeInformationW(
                volume.value, None, 0, None, None, None, fs, len(fs)) or fs.value != 'NTFS':
            raise Blocked('Only local NTFS is supported on Windows')
    elif sys.platform.startswith('linux'):
        # Fail closed on unverified mounts; hardlink success alone is not a semantic proof.
        mounts = []
        for line in Path('/proc/self/mountinfo').read_text().splitlines():
            fields, extra = line.split(' - ', 1)
            mount = Path(fields.split()[4].replace('\\040', ' '))
            if root.is_relative_to(mount):
                mounts.append((len(mount.parts), extra.split()[0]))
        kind = max(mounts)[1] if mounts else ''
        if kind not in {'ext2', 'ext3', 'ext4', 'xfs', 'btrfs', 'tmpfs', 'overlay'}:
            raise Blocked('Unverified filesystem: ' + kind)
    else:
        raise Blocked('Unsupported publication platform')


def publish(root: Path, relative: str, data: bytes, parent_state: dict) -> dict:
    target = contained(root, relative)
    parent = target.parent
    name = parent / ('.pi-' + uuid.uuid4().hex[:12])
    fd = os.open(name, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, 'O_BINARY', 0), 0o600)
    owned = None
    verified = None
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        owned = snapshot(name)
        if owned['sha256'] != digest(data) or owned['bytes'] != len(data):
            raise Blocked('Temporary content mismatch')
        if snapshot(parent) != parent_state or snapshot(target)['kind'] != 'absent':
            raise Blocked('Publication precondition changed')
        contained(root, relative)
        os.link(name, target)  # Atomic create-new. NEVER fall back to replace/rename/write_text.
        final = snapshot(target)
        if final != owned:
            raise Blocked('Published identity mismatch; preserve result for review')
        verified = final
        return final
    finally:
        # Do not remove unknown/replaced temporary content or any final artifact.
        try:
            if owned is not None and snapshot(name) == owned:
                name.unlink()
        except (OSError, ValueError) as error:
            if verified is not None:
                raise PublishedCleanupFailure(verified, error) from error
            raise


def validated_progress(root: Path, plan: dict, prior: dict) -> dict:
    """A receipt may explain only verified, planned create-only progress."""
    progress = {}
    for key in ('completed', 'directories'):
        value = prior.get(key, {})
        if not isinstance(value, dict):
            raise Blocked('Receipt progress must be an object: ' + key)
        progress[key] = dict(value)
    targets = {row['path']: row for row in plan['targets']}
    for p, recorded in progress['completed'].items():
        row = targets.get(p)
        if row is None or row['action'] != 'create' or row['before']['kind'] != 'absent':
            raise Blocked('Unapproved receipt completion: ' + str(p))
        if (not isinstance(recorded, dict) or recorded.get('kind') != 'file'
                or recorded.get('bytes') != row['bytes'] or recorded.get('sha256') != row['sha256']):
            raise Blocked('Receipt completion does not match planned file: ' + p)
        if snapshot(contained(root, p)) != recorded:
            raise Blocked('Completed entry changed: ' + p)
    for p, recorded in progress['directories'].items():
        if (p not in plan['parents'] or plan['parents'][p]['kind'] != 'absent'
                or not any(row['action'] == 'create' and str(Path(row['path']).parent).replace('\\', '/') == p
                           for row in targets.values())):
            raise Blocked('Unapproved receipt directory: ' + str(p))
        if not isinstance(recorded, dict) or recorded.get('kind') != 'directory':
            raise Blocked('Receipt parent is not a directory: ' + p)
        if snapshot(contained(root, p)) != recorded:
            raise Blocked('Created parent changed: ' + p)
    return progress


def apply(plan: dict, confirmation: str, authority_ref: str, prior: dict | None = None) -> dict:
    if not isinstance(plan, dict):
        return {'status': 'blocked', 'error': 'Plan must be a JSON object'}
    receipt = {'version': VERSION + '/receipt', 'plan_sha256': plan.get('plan_sha256'),
               'authority_ref': authority_ref, 'completed': {}, 'directories': {}, 'status': 'blocked'}
    try:
        if not isinstance(authority_ref, str) or not authority_ref.strip():
            raise Blocked('Locate original user authorization before applying; a plan is not authority')
        body = {k: v for k, v in plan.items() if k != 'plan_sha256'}
        if confirmation != plan.get('plan_sha256') or confirmation != digest(canonical(body)):
            raise Blocked('Confirmation does not match the original plan')
        if plan.get('version') != VERSION or plan.get('input_version') != 1:
            raise Blocked('Unknown plan version')
        root = project_root(plan['root'])
        # Reject changed code BEFORE importing/executing the template. Later
        # checks remain necessary; this is not a hostile-race guarantee.
        if tools() != plan.get('tools'):
            raise Blocked('Tool identity changed before rendering')
        content = render(plan['inputs'])
        # Reconstruct expected packet using original preconditions, not a new approval.
        expected = preview(str(root), plan['inputs'])
        for key in ('root_state', 'parents', 'targets'):
            expected[key] = plan[key]
        for row in plan['targets']:
            p = row['path']
            if p not in TARGETS:
                raise Blocked('Unapproved target')
            data = content[p].encode('utf-8')
            if (row['content_base64'], row['bytes'], row['sha256']) != (
                    base64.b64encode(data).decode('ascii'), len(data), digest(data)):
                raise Blocked('Planned content differs from the approved template')
            before = row['before']
            action = 'reference' if before['kind'] == 'file' or (p == TARGETS[0] and plan['inputs']['intake_ref']) else 'create'
            if row['action'] != action or before['kind'] not in ('file', 'absent'):
                raise Blocked('Invalid action/precondition')
        expected.pop('plan_sha256')
        if expected != body or [r['path'] for r in plan['targets']] != list(TARGETS):
            raise Blocked('Input, sources, tool identity or packet shape changed')
        if snapshot(root) != plan['root_state']:
            raise Blocked('Project identity changed')
        if prior is not None and not isinstance(prior, dict):
            raise Blocked('Receipt must be a JSON object')
        prior = prior or {}
        if prior and (prior.get('version') != receipt['version'] or prior.get('plan_sha256') != confirmation):
            raise Blocked('Receipt belongs to another plan')
        # Do not copy unvalidated claims into the new receipt or its status.
        receipt.update(validated_progress(root, plan, prior))

        def check_preconditions():
            if tools() != plan['tools'] or snapshot(root) != plan['root_state']:
                raise Blocked('Tool/project changed')
            for p, before in plan['sources'].items():
                if snapshot(contained(root, p)) != before:
                    raise Blocked('Source changed: ' + p)
            for p, before in plan['parents'].items():
                current = snapshot(contained(root, p))
                if current != before and current != receipt['directories'].get(p):
                    raise Blocked('Unknown parent change: ' + p)
            for row in plan['targets']:
                current = snapshot(contained(root, row['path']))
                if current != row['before'] and current != receipt['completed'].get(row['path']):
                    raise Blocked('Unknown entry change; retain file and obtain confirmation: ' + row['path'])
                if row['path'] in receipt['completed'] and current != receipt['completed'][row['path']]:
                    raise Blocked('Completed entry changed')

        check_preconditions()
        if any(row['action'] == 'create' and row['path'] not in receipt['completed']
               for row in plan['targets']):
            filesystem(root)
        for row in plan['targets']:
            if row['action'] == 'reference' or row['path'] in receipt['completed']:
                continue
            check_preconditions()
            target = contained(root, row['path'])
            if snapshot(target.parent)['kind'] == 'absent':
                target.parent.mkdir()  # EEXIST/race is a failure, not silently accepted.
                receipt['directories']['00_research_logic'] = snapshot(target.parent)
            check_preconditions()
            try:
                receipt['completed'][row['path']] = publish(root, row['path'], content[row['path']].encode('utf-8'), snapshot(target.parent))
            except PublishedCleanupFailure as error:
                receipt['completed'][row['path']] = error.completed
                raise
        check_preconditions()
        receipt.update(status='paper_entries_checked', start_stage=plan['inputs']['start_stage'],
                       next_action=plan['inputs']['next_action'],
                       research_readiness='unreviewed', agent_hook_memory='not operated')
    except (ValueError, OSError, KeyError, TypeError) as error:
        receipt['status'] = 'partial' if receipt['completed'] or receipt['directories'] else 'blocked'
        receipt['error'] = str(error)
    return receipt


def main() -> int:
    if sys.version_info < (3, 11):
        print(json.dumps({'status': 'blocked', 'error': 'Python 3.11+ required; use an existing interpreter, do not auto-install'}))
        return 2
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    sub.add_parser('inspect').add_argument('--project', required=True)
    p = sub.add_parser('preview')
    p.add_argument('--project', required=True)
    for name, default in [('title', 'unknown'), ('work-goal', None), ('acceptance', None),
                          ('goal-source', None), ('formal-goal-ref', ''), ('intake-ref', ''),
                          ('start-stage', None), ('next-action', None)]:
        p.add_argument('--' + name, default=default, required=default is None)
    p.add_argument('--reference', action='append', default=[])
    a = sub.add_parser('apply')
    a.add_argument('--plan', required=True, help='Saved original packet, or - for stdin')
    a.add_argument('--confirm-plan-sha256', required=True)
    a.add_argument('--authority-ref', required=True, help='Original scoped user confirmation; not authenticated by this helper')
    a.add_argument('--receipt', help='Prior same-plan receipt for an interrupted attempt')
    args = parser.parse_args()
    try:
        if args.operation == 'inspect':
            result = inspect(args.project)
        elif args.operation == 'preview':
            inputs = {key: getattr(args, key) for key in INPUT_KEYS - {'references'}}
            inputs['references'] = args.reference
            result = preview(args.project, inputs)
        else:
            raw = sys.stdin.read(LIMIT + 1) if args.plan == '-' else read_packet_file(args.plan)
            if len(raw.encode('utf-8')) > LIMIT:
                raise Blocked('Packet too large')
            prior = json.loads(read_packet_file(args.receipt)) if args.receipt else None
            result = apply(json.loads(raw), args.confirm_plan_sha256, args.authority_ref, prior)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if result.get('status') in ('blocked', 'partial') else 0
    except (ValueError, OSError) as error:
        print(json.dumps({'status': 'blocked', 'error': str(error)}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
