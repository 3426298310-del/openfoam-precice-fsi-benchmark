# Sources, Versions, and Reused Components

This is a learning-oriented, partitioned-coupling reproduction of the Turek–Hron
FSI case. It is **not** the official, verified CalculiX FSI3 release from
preCICE.

## Upstream sources

- **preCICE tutorials mainline**:
  <https://github.com/precice/tutorials>, commit
  `17015c10387c222a70eb73de6702b48187dd29f7`.
- **CalculiX FSI3 case**: [pull request #304](https://github.com/precice/tutorials/pull/304)
  by JoSchrdr (unmerged at the time of retrieval), commit
  `3cb8e705636dcaf8b0e5f10f3c899200b3867c2e`. The original files are preserved
  under `third_party/reference_case/`.
- **Official FSI3 tutorial**: <https://precice.org/tutorials-turek-hron-fsi3>
  (the official structure solver is deal.II/Nutils; this project instead uses
  CalculiX from the PR above).

## Software versions

- **OpenFOAM adapter** v1.3.0:
  <https://github.com/precice/openfoam-adapter/tree/v1.3.0>, commit
  `74b8719ce874c793a581fd009a54c0e1c7923b1e` (preCICE v3, OpenFOAM v2312).
- **CalculiX adapter** v2.20.2:
  <https://github.com/precice/calculix-adapter/tree/v2.20.2>, commit
  `f362a16d54a31985712f4c4302128f6923bd1d00`, based on CalculiX 2.20.
- **preCICE** 3.2.0:
  <https://github.com/precice/precice/releases/tag/v3.2.0> (Ubuntu noble binary).
- **CalculiX** 2.20 source:
  <https://www.dhondt.de/ccx_2.20.src.tar.bz2>.

## Benchmark reference

J. Hron, S. Turek, *A monolithic FEM solver for an ALE formulation of
fluid–structure interaction with configuration for numerical benchmarking*,
ECCOMAS CFD 2006:
<https://wwwold.mathematik.tu-dortmund.de/papers/HronTurek2006a.pdf>.

## What was reused (from the upstream PR)

- Geometry, fluid block mesh, structural mesh, and material input.
- The original coupling algorithm and thresholds (used as the starting point).

## What was modified in this repository

1. Migrated the preCICE XML configuration from v2 to v3 syntax: removed
   `solver-interface`, declared mesh dimensions explicitly, used
   `provide-mesh`/`receive-mesh`, socket `acceptor`/`connector`, and the new
   RBF-mapping syntax.
2. Replaced the `groovyBC` inlet dependency with a native OpenFOAM
   `codedFixedValue` parabolic inlet (with the standard 0–2 s cosine start-up
   ramp), removing the groovyBC shared-library dependency.
3. Corrected the force-monitoring density `rhoInf` from 1 to 1000 and added the
   0.01 m unit-depth conversion for per-meter forces.
4. Added isolated run directories, failure propagation, log capture,
   post-processing, and documentation; reduced structural field output
   frequency while keeping a watchpoint for every time window.
5. Reorganized the case into `fluid/` / `solid/` / `coupling/` and fixed the
   relative paths in the configuration.

## License

The tutorial repository carries LGPL-3.0 (see the root `LICENSE`); reused
tutorial files keep that license. The OpenFOAM adapter is GPL-3.0; the CalculiX
adapter is GPL-3.0 overall (the modified CalculiX files are
GPL-2.0-or-later). Downloaded third-party papers and system binaries are not
packaged into Git. New scripts and documentation are released under the root
LGPL-3.0 license.
