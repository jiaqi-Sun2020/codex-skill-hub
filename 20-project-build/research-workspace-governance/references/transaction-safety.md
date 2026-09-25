# Transaction and Windows Path Safety

This is the common behavior contract for atomic files and staged directories.
Each Skill keeps its own small implementation so an independently installed
Skill has no runtime dependency on a sibling. Project-specific publishers must
provide conformance tests for the same contract.

## Atomic files

1. Validate the unresolved absolute target and every existing component. Reject
   symbolic links, junctions, reparse points, non-directory parents, and project
   escapes before writing.
2. Create a sibling temporary on the same filesystem. Its name is
   `.tmp-<target-identity16>-<nonce>` and never repeats the target basename.
3. The full target identity is SHA-256 of the normalized target identity. The
   first 16 digits are only a bounded namespace prefix; they are not sufficient
   to prove identity.
4. Create the temporary exclusively, write, flush, and `fsync` it. A name
   collision causes a retry and never deletion of the colliding object.
5. Create-new publication uses an atomic no-clobber primitive. A same-filesystem
   hard link followed by removal of the owned temporary satisfies this contract.
   If unavailable, return a portability failure; do not fall back to
   overwrite-capable `replace`.
6. `replace` is reserved for an explicitly authorized replacement with a
   verified backup and unchanged target identity.
7. Cleanup compares the exact path and file identity recorded when this attempt
   created it. It does not use a glob, filename heuristic, or another writer's
   path. Parent directory sync is required when the platform supports it.

An existing legacy `target.tmp` is reported or retained. It neither blocks a
new random sibling nor becomes an automatic cleanup target.

## Directory transactions

Stage directly beside the final root and publish by same-filesystem rename:

```text
parent/final-root
parent/.txn-<phase-code>-<target-identity16>-<nonce>
```

The manifest inside the transaction carries the full target identity, attempt
ID, intended final path, plan hash, created-path list, and lifecycle state.
Single-experiment and campaign publishers use this same rule; their scientific
contents remain project-owned.

Before creation, record:

```text
portable_limit_chars
final_path_chars
legacy_staging_path_chars
staging_path_chars
max_descendant_relative_chars
```

Require `staging_path_chars + max_descendant_relative_chars` to remain within
the declared portable limit. A final path of 241 characters whose legacy stage
reaches 259 is a mandatory regression fixture. Enabling Windows long paths is
useful environment metadata but never the only mitigation or a pass condition.

## Stale, collision, and legacy handling

- A current-format sibling with the same prefix but a different full identity
  is an identity collision and blocks publication and cleanup.
- The same full identity with another attempt ID is stale and blocks the affected
  operation until reviewed.
- Legacy names such as `<final>.prepare-<nonce>` are recognized and retained.
  If they cannot be uniquely bound to a full target identity, the operation is
  `blocked`.
- A candidate outside the exact parent, or one that is a link, junction, reparse
  point, or non-directory, is unsafe.

Rollback may remove only an exact path in the current attempt's created-path
set, directly below the intended parent, with a matching full identity and
attempt manifest, and with a safe non-link type. It must not delete pre-existing
directories, ambiguous legacy remnants, colliding objects, backup refs, or
anything selected by name pattern alone. A cleanup or rollback failure is
retained as evidence and blocks the next dependent stage.

Windows is a required validation platform. Linux remains a second independent
filesystem implementation check. Tests run twice from an external random
working directory and must not depend on developer-machine remnants.
