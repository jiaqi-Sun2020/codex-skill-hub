# Real-time visual computing

[中文](README.md) | [Repository overview](../README.en.md)

`60-visual-computing` contains reusable Skills for real-time visual computing on
the web. Its Skills cover real-time graphics, GSAP interaction animation,
performance, and reproducible validation; they do not replace astronomy questions,
scientific modelling, or a project's existing animation-library choice.

## Current Skill

| Skill | Purpose | Boundary |
|---|---|---|
| `celestial-body-formation-skill` | Build, improve, or audit real-time web visuals for planets, stars, neutron stars, black holes, their surfaces, and emitting structures from first principles of geometry, energy, time, and sampling. | Not for astronomy Q&A, and never present a visual approximation as a scientific simulation of celestial formation or evolution. |
| `gsap-core` | Use the GSAP core tween, easing, stagger, defaults, and responsive-animation APIs. | Use only where GSAP is chosen or needed; do not replace an existing animation library. |
| `gsap-timeline` | Sequence multi-step animation with timelines, position parameters, nesting, and playback. | Do not treat chained independent delays as reliable choreography. |
| `gsap-scrolltrigger` | Build scroll-triggered, pinned, scrubbed, and parallax-style animation. | It owns scroll interaction only; the host framework still owns unmount and layout-change handling. |
| `gsap-plugins` | Register and use interaction, SVG, text, physics, and easing plugins. | Do not generate private registries, `.npmrc`, or authentication tokens. |
| `gsap-utils` | Map, clamp, interpolate, randomize, snap, and handle collections with `gsap.utils`. | Utilities do not replace product state, accessibility, or interaction design. |
| `gsap-react` | Use `useGSAP`, refs, scope, and cleanup in React or Next.js. | Do not apply React lifecycle patterns to Vue or Svelte. |
| `gsap-performance` | Prefer transforms, batching, and bounded `will-change` to reduce jank. | Verify performance guidance on the target page and device. |
| `gsap-frameworks` | Manage mount, selector scope, and unmount cleanup in Vue, Svelte, and other non-React frameworks. | Use `gsap-react` for React. |

## Use and boundary

Read [`celestial-body-formation-skill/SKILL.md`](celestial-body-formation-skill/SKILL.md) first. It binds spatial, energy, temporal, and sampling relations to the actual entry point, device, and evidence. Visual approval, runtime evidence, and scientific conclusions remain independent facts.

The celestial Skill's public references describe general rendering choices and adversarial verification. The stellar-prominence and neutron-star material pages provide reusable rendering representations, generation order, and verification boundaries only; they do not turn a visual reference into a scientific model. The GSAP Skills route by core API, timeline, scroll, plugins, utilities, framework, and performance; they do not install dependencies, rewrite bundler configuration, or override the animation library selected by the user. Project-specific cases, machine paths, internal build records, and conversation material are intentionally excluded from this category and must not be restored to the public repository. Trace a particular project only inside its authorized workspace.

## Sources and license

The celestial Skill was imported from a local Codex Skill at the user's direction.
Its `references/` cite [PBRT](https://www.pbr-book.org/) and the
[WGSL specification](https://www.w3.org/TR/WGSL/) as methodological sources;
neither implementation nor documentation was copied from them.

The eight GSAP Skills were imported with user confirmation from [GreenSock's
official `gsap-skills` project](https://github.com/greensock/gsap-skills); only
their `SKILL.md` execution contracts are retained. That upstream project declares
MIT, and this category retains its [MIT notice](GSAP_SKILLS_LICENSE). This does
not alter or replace the GSAP runtime's own license or dependency requirements.

Relicensable repository content is covered by the root [MIT License](../LICENSE);
external materials retain their own terms.

## Verification

Run from the repository root:

```powershell
$skills = @('celestial-body-formation-skill', 'gsap-core', 'gsap-timeline', 'gsap-scrolltrigger', 'gsap-plugins', 'gsap-utils', 'gsap-react', 'gsap-performance', 'gsap-frameworks')
foreach ($skill in $skills) {
  python -X utf8 -B "$env:CODEX_HOME\skills\.system\skill-creator\scripts\quick_validate.py" ".\60-visual-computing\$skill"
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
```
