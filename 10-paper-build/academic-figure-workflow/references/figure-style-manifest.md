# Figure Style Manifest

Use this reference to create and maintain `<figure-root>/style/style_manifest.yaml`. The manifest is the sole paper-wide visual source of truth for SVG, Draw.io, Matplotlib, and PowerPoint outputs.

## Storage Contract

Use the canonical minimal storage/retention rules in
[figure-package-hygiene.md](figure-package-hygiene.md#one-figure-one-folder).
Only actual deliverables belong in a figure package; PPTX and shared style
directories are not mandatory for an unrelated local preview.

Resolve `<figure-root>` once for the active manuscript:

- inside a generated paper pipeline, use
  `05_manuscript_zh/figures/`;
- in standalone use, default to `<project>/figures/` or use the explicit root
  selected by the user;
- do not create both locations for the same manuscript or add an extra
  `<paper>/` layer unless a multi-paper workspace explicitly requires it.

Create `style/` only when the project needs a shared visual system. A paper
with no figure work must not receive an empty manifest or placeholder style
files.

Use dedicated temporary directories for rendered QA. Retention and cleanup
follow only [figure-package-hygiene.md](figure-package-hygiene.md#default-retention):
keep previews while review is pending; afterward remove only classified
transients within explicitly authorized cleanup scope. Export success is not
review approval, and referenced evidence remains protected.

Start from `assets/style_manifest.template.yaml`. It is JSON-compatible YAML so bundled scripts can read it without installing a YAML package. Full YAML syntax is allowed when a YAML parser is already available; do not silently install one.

## Required Sections

The manifest must contain:

- `schema_version`, `project_id`, and `state` with `locked` and `status`;
- `references` with role, source path, and confidence;
- `precedence` for reference conflicts;
- `palette` with primary, secondary, accent, and neutral colours;
- `semantic_colors` for the roles actually used; the full template's model roles
  are examples, not mandatory vocabulary for every discipline;
- `neutral_colors` and `backgrounds`;
- `typography` with family and hierarchy;
- `strokes`, `arrows`, `borders`, `corners`, `fills`, and `shadows`;
- `spacing`, `panels`, `axes`, `ticks`, `legend`, `grid`, `markers`, and `charts`;
- for plot-to-PPT work, `chart_contrast` thresholds and a `publication_layout` target width or an external shared layout contract;
- `architecture` grammar and semantic module roles;
- `powerpoint` slide and object defaults;
- `overrides`, `conflicts`, and `unresolved_issues`.

Every colour must be a six-digit hex value. Sizes must state their unit in the key or containing object. Do not mix point, millimetre, pixel, and PowerPoint-coordinate values implicitly.

## Locking

Use these states:

- `provisional`: extracted or default tokens need review;
- `approved`: tokens were reviewed but later figures may still reveal gaps;
- `locked`: later figures must inherit the tokens unless the user explicitly overrides them.

When the user says “以后所有图片沿用这个风格” or equivalent:

1. read the existing manifest;
2. update only the approved reference and derived tokens;
3. set `state.locked: true` and `state.status: locked` after confirmation;
4. log the source and decision in `style_report.md`;
5. apply the manifest to all later figures.

Never create figure-local random palettes. When a needed semantic role is absent, add it at project level and record the change.

## Precedence and encoding scope

Scientific integrity comes first, then the actual medium/venue requirements,
then the user's current specifically authorized changes, then the approved
project/template and selected references for everything not overridden, then
the existing method default. A new reference or a generic clean/minimal request
cannot unlock a baseline. A different delivery target may be agreed, but must
not be reported as satisfying an incompatible venue requirement.

Declare the primary colour meaning per figure/comparison in the existing source
or style report: method, role, process stage, numerical quantity, or another
evidence-backed object. Role and stage cannot both control the same fill.
Keep meanings stable within that declared scope; a topology, algebra diagram or
result plot may need a different encoding from a process diagram. This is not
permission for undocumented arbitrary palettes or changes to comparison data.

## Override Contract

A figure-local override must include:

```yaml
overrides:
  - figure_id: fig04
    token: axes.y_scale
    old_value: linear
    new_value: log
    reason: manuscript evidence requires logarithmic scale
    approved_by: user
```

Scientific overrides such as log scale are not merely stylistic; verify them against data and manuscript evidence.

## Consumer Mapping

### Matplotlib

Map manifest tokens to `rcParams`, axes, semantic plot colours, marker families, grids, legends, and panel labels. Preserve:

```python
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["pdf.fonttype"] = 42
```

The bundled multi-panel generator accepts `--style-manifest` and records the manifest path in QA output.

### SVG and Draw.io

Use semantic colours as reusable classes or styles. Keep labels as text, arrows as vectors, and modules as independent groups. Record the manifest path in figure metadata or the figure package report.

### PowerPoint

Use the same background, typography, fills, borders, connectors, panel labels, chart palette, and spacing. Do not fall back to Office theme colours when an equivalent manifest token exists.

Fine marks may use darker companion tokens than pale fills. For example, preserve a light `training_spectra_fill` while defining a darker `training_spectra_outline`; this is a semantic-role refinement, not a random figure-local colour.

## Validation

Run:

```powershell
# Directory: the academic-figure-workflow skill directory
python .\scripts\validate_style_manifest.py --manifest <figure-root>\style\style_manifest.yaml
```

Validation checks sections, declared colours, lock state and reference roles.
Use repeatable `--used-role` for actual consumers; the plotting script supplies
its roles automatically. Legacy full manifests stay readable. The validator does
not enforce authorization, measure final typography or validate every possible
unit/override. Inspect the rendered figures and `style_report.md`.
