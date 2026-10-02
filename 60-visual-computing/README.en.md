# Real-time visual computing

[中文](README.md) | [Repository overview](../README.en.md)

`60-visual-computing` contains reusable Skills for real-time visual computing on
the web. Its Skills cover representation, materials, animation, performance, and
reproducible validation for real-time graphics; they do not replace astronomy
questions, scientific modelling, or domain conclusions for a particular project.

## Current Skill

| Skill | Purpose | Boundary |
|---|---|---|
| `celestial-body-formation-skill` | Build, improve, or audit real-time web visuals for planets, stars, black holes, their surfaces, and emitting structures from first principles of geometry, energy, time, and sampling. | Not for astronomy Q&A, and never present a visual approximation as a scientific simulation of celestial formation or evolution. |

## Use and boundary

Read [`celestial-body-formation-skill/SKILL.md`](celestial-body-formation-skill/SKILL.md) first. It binds spatial, energy, temporal, and sampling relations to the actual entry point, device, and evidence. Visual approval, runtime evidence, and scientific conclusions remain independent facts.

The Skill's public references describe general rendering choices and adversarial verification. Project-specific cases, machine paths, internal build records, and conversation material are intentionally excluded from this category and must not be restored to the public repository. Trace a particular project only inside its authorized workspace.

## Sources and license

This category was imported from a local Codex Skill at the user's direction. Its
`references/` cite [PBRT](https://www.pbr-book.org/) and the
[WGSL specification](https://www.w3.org/TR/WGSL/) as methodological sources;
neither implementation nor documentation was copied from them. Relicensable
repository content is covered by the root [MIT License](../LICENSE); external
materials retain their own terms.

## Verification

Run from the repository root:

```powershell
python -X utf8 -B "$env:CODEX_HOME\skills\.system\skill-creator\scripts\quick_validate.py" ".\60-visual-computing\celestial-body-formation-skill"
```
