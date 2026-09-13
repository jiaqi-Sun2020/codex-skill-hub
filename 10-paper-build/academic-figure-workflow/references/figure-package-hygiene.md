# Figure Package Hygiene

Use this reference after a figure has passed scientific, visual, and structural QA. The goal is a clean project, not deletion during active debugging.

## One Figure, One Folder

Use a project-level style folder and a separate folder for each numbered figure:

```text
figures/<paper>/
├── style/
│   ├── reference_images/
│   ├── style_manifest.yaml
│   └── style_report.md
├── fig01_<short_name>/
│   ├── Figure1_<short_name>.pptx
│   ├── caption.md
│   ├── ppt_manifest.json
│   ├── source/
│   └── exports/
└── fig02_<short_name>/
    └── ...
```

Do not mix Figure 1 and Figure 2 sources, exports, manifests, or QA remnants in the project root.

## Classification

Keep as final deliverables:

- requested PPTX, SVG, PDF, PNG, TIFF, or Draw.io files;
- `caption.md` and the final package manifest;
- requested submission variants.

Keep as reproducibility sources:

- plotting/build scripts, Draw.io/SVG source, source data or a non-duplicating source-data pointer, panel spec, figure argument, style manifest, and source trace;
- derived CSV used directly by the figure when it is small and materially improves auditability;
- backend-specific vector assets only when the PPTX builder requires them and can trace them.

Treat as transient unless the user requests retention:

- rendered previews, montage/contact sheets, slide PNGs, `*.layout.json`, `*.inspect.ndjson`, template starter decks, template inspection folders;
- temporary QA renders and normalized scratch manifests;
- `.tmp`, `__pycache__`, `.pyc`, office lock files, and failed intermediate versions;
- compatibility or debug exports that are not referenced by a final manifest.

## Safe Cleanup Sequence

1. Build in a dedicated temporary directory such as `<workspace>/.tmp/<paper>_<figure>`.
2. Validate the final deliverables before deleting anything.
3. Create a keep list from the package manifest plus user-provided assets.
4. Resolve every deletion target to an absolute path and confirm it is inside the intended figure folder or dedicated temporary directory.
5. Never delete raw datasets, manuscript files, user-edited PPTX/Draw.io/SVG sources, reference images, or locked style files as part of automatic cleanup.
6. Delete only the explicit transient list. Do not use an unresolved wildcard or a recursive delete against the workspace root.
7. Re-list the final project tree, open the final PPTX, and verify that every manifest path still resolves.
8. Report what was deleted and whether any retained intermediate is still required for reproducibility.

## Default Retention

Rendered previews are required during QA but are deleted after a passing final review. Retain them only when the user asks for preview delivery, review history, or visual-regression fixtures.

The final manifest should preserve the validation summary so deleting preview and scratch QA files does not erase the audit outcome.
