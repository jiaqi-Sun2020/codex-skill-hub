# Figure Style Manifest

Use this reference to create and maintain `<figure-root>/style/style_manifest.yaml`. The manifest is the sole paper-wide visual source of truth for SVG, Draw.io, Matplotlib, and PowerPoint outputs.

## Storage Contract

Recommended project layout:

```text
<figure-root>/
├── style/
│   ├── reference_images/
│   ├── style_manifest.yaml
│   └── style_report.md
├── fig01_architecture/
│   ├── Figure1_architecture.pptx
│   ├── caption.md
│   ├── ppt_manifest.json
│   ├── source/fig01.drawio
│   ├── exports/fig01.svg
│   ├── exports/fig01.pdf
│   └── exports/fig01.png
├── fig02_comparison/
│   ├── Figure2_comparison.pptx
│   ├── caption.md
│   ├── ppt_manifest.json
│   ├── source/data.csv
│   ├── source/fig02.py
│   ├── exports/fig02.svg
│   ├── exports/fig02.pdf
│   └── exports/fig02.png
```

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

Use dedicated temporary directories for rendered QA. Do not retain `preview/`, layout dumps, inspect snapshots, or cache folders in the final project tree unless requested. See [figure-package-hygiene.md](figure-package-hygiene.md).

Start from `assets/style_manifest.template.yaml`. It is JSON-compatible YAML so bundled scripts can read it without installing a YAML package. Full YAML syntax is allowed when a YAML parser is already available; do not silently install one.

## Required Sections

The manifest must contain:

- `schema_version`, `project_id`, and `state` with `locked` and `status`;
- `references` with role, source path, and confidence;
- `precedence` for reference conflicts;
- `palette` with primary, secondary, accent, and neutral colours;
- `semantic_colors` including `proposed_method`, `baseline`, `encoder`, `decoder`, `fusion`, `attention`, `input`, `output`, `uncertainty`, and `highlight`;
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

Validation must report missing required roles, malformed colours, invalid lock state, reference-role conflicts, and unsupported units. A schema-valid manifest can still be visually or scientifically wrong; inspect the rendered figures and `style_report.md`.
