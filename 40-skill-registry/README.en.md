# Skill Registry compatibility entry

[中文](README.md) | [English](README.en.md) | [Back to the root README](../README.en.md)

`40-skill-registry/` is a compatibility navigation directory, not a second Registry. `skill-registry.lnk` provides only a local convenience entry; the one canonical source is [`50-core-utils/skill-registry/`](../50-core-utils/skill-registry/README.md).

## Canonical-source relationship

```text
40-skill-registry/skill-registry.lnk
  └─ navigates to 50-core-utils/skill-registry/
       ├─ registry.json
       ├─ sources/
       ├─ releases/
       ├─ tools/
       └─ tests/
```

## Usage boundaries

- Do not create a Registry copy, release snapshot, or configuration under `40-skill-registry/`.
- Do not edit immutable material under `releases/`; publish a new version from central source when upgrading.
- Do not treat the `.lnk` file as a portable cross-machine interface.
- Project-owned forks must not be silently overwritten from central historical releases.
- Registry is version-governance infrastructure and is not counted among the 20 active Skills.

## Verification entry

Run from the repository root:

```powershell
python -X utf8 -B ".\50-core-utils\skill-registry\tools\skill_registry.py" registry-check --registry ".\50-core-utils\skill-registry"
```

See the [Registry README](../50-core-utils/skill-registry/README.md) for the complete interface and compatibility policy.
