# Third-party reference material

This directory contains **upstream reference material** that is **not authored
by this project**. It is retained here for traceability only, so reviewers can
see exactly what the project was derived from.

- **Content** — `reference_case/`: the original CalculiX FSI3 tutorial case
  submitted to the preCICE tutorials repository as
  [pull request #304](https://github.com/precice/tutorials/pull/304) by
  JoSchrdr, at commit `3cb8e705636dcaf8b0e5f10f3c899200b3867c2e`.
- **What was reused** — geometry, the fluid block mesh, the structural mesh,
  material input, and the original coupling algorithm and thresholds.
- **License** — follows the upstream tutorial repository (LGPL-3.0).

The actual project implementation lives in:

- `fluid/` — OpenFOAM case (modified)
- `solid/` — CalculiX input (modified)
- `coupling/` — preCICE configuration (rewritten for preCICE 3.x)
- `scripts/` — install / run / post-processing pipeline
- `experimental/fsi3/` — FSI3 configuration (prepared, not fully run)
