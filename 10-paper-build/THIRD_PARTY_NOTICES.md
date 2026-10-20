# Third-party notices: literature, scientific reasoning, goal clarification, and figure workflow

## Fixed source snapshots

- Matt Pocock, [mattpocock/skills](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336),
  commit `49dd158d1076134a641b33efb035946536778336`: `grill-me` delegates to
  `grilling`; their dependency-frontier interview and explicit user decisions
  inform the local repeatable goal-clarification reference. We do not install
  either Skill or copy the upstream runtime call. Local adaptation bounds the
  interview to the next action, separates science from permission, and reuses
  managed decisions without promising persistence of unsaved chat.
- Wen-Yu Chang, [WenyuChiou/research-hub](https://github.com/WenyuChiou/research-hub/tree/cfc40cc27d45a78783266f9f4312290778ae6f5e),
  commit `cfc40cc27d45a78783266f9f4312290778ae6f5e`: adapted
  `skills/literature-triage-matrix/SKILL.md`. The central Skill is self-contained,
  uses optional Pipeline paths, preserves requested columns and explicit source
  gaps, and has no dependency on the rest of Research Hub. Upstream eval scenarios
  inform the local regression/review cases; no separate eval folder is introduced.
- K-Dense Inc., [scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills/tree/92ace75ac21efe19a620434e0ca4e356081fe807),
  commit `92ace75ac21efe19a620434e0ca4e356081fe807`: adapted
  `skills/literature-review/` (upstream version 1.11). Retained the entry,
  five workflow/search/style references, review template, and the record-processing
  and DOI-metadata scripts. References/template are scoped to the lightweight
  local workflow; DOI checks are optional, stdout-default and registration-only.
  Output files are create-new, duplicate/version data are retained, and unknown
  dates are pending. Excluded generate_pdf.py, generate_schematic.py and
  generate_schematic_ai.py; no PDF, paid AI, new authentication or automatic citation.
- From that same K-Dense snapshot, scientific-brainstorming v1.4 informed
  research-logic's candidate/assumption/counterevidence/decision separation and
  reopening ideation. scientific-critical-thinking v1.5 informed source-linked,
  proportionate critique in research-logic, experiment-design, data-analysis and
  literature-review. Their standalone Skills, scripts and paid figure routes
  are not imported. Clinical frameworks are conditional, not universal.
- Existing method-integration guidance and its QWTA/TGN example were moved from
  research-logic's entry to a conditional local reference; this is not attributed
  to either new upstream source.

## Academic figure workflow sources

- naplesblue, [apple-design-skill](https://github.com/naplesblue/apple-design-skill/tree/e81692da299d64b9bf38ae26db2d709fc60c8bf3),
  commit `e81692da299d64b9bf38ae26db2d709fc60c8bf3`, MIT: independently adapted
  restrained cool neutrals, clear hierarchy, spacing, and reduced fragmentation
  into `academic-figure-workflow/references/apple-inspired-academic-figure-style.md`.
  Glass, UI, font, and motion recipes are excluded.
- 2TheFar, [apple-inspired-design-skill](https://github.com/2TheFar/apple-inspired-design-skill/tree/f709388017307d8cefcdab4b9bc0f9f54e32bb8e),
  commit `f709388017307d8cefcdab4b9bc0f9f54e32bb8e`, MIT: independently adapted
  task-first design, semantic tokens, accessibility, rendered verification, and
  explicit risk reporting into the same optional reference. It never becomes a
  default style, a second manifest, or permission to change scientific content.
- Nicolas P. Rougier, Michael Droettboom, and Philip E. Bourne, [*Ten Simple
  Rules for Better Figures*](https://doi.org/10.1371/journal.pcbi.1003833),
  PLOS Computational Biology 10(9): e1003833 (2014), CC0 Public Domain
  Dedication: retained as `academic-figure-workflow/Ten Simple Rules for Better
  Figures.pdf` (SHA-256 `95B6714AA1CE1E058475C9A807FA85E058BDAA5C3261E792DC5E8DFD9AE83AD6`).
  It is an optional general-design reading source, not a venue rule, scientific
  evidence input, or a substitute for the local figure contracts.

These are adapted sources, not unmodified upstream releases. MIT notices below
apply to derivative portions and do not imply endorsement or scientific validity.
Copyright acknowledgement is not automatic manuscript citation. Any academic
reference needs verified metadata, material relevance and author-controlled use.
Future updates require reviewing the pinned diff and local adaptations, not
blindly replacing central files. No user-level installation is performed.

## naplesblue and 2TheFar MIT notice

```text
MIT License

Copyright (c) 2026 naplesblue
Copyright (c) 2026 2TheFar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Matt Pocock MIT notice

```text
MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Research Hub MIT notice

```text
MIT License

Copyright (c) 2026 Wen-Yu Chang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## K-Dense MIT notice

```text
MIT License

Copyright (c) 2025 K-Dense Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
