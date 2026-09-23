#!/usr/bin/env bash
set -eo pipefail
source "$(dirname "$0")/env.sh"
mkdir -p "$FSI_ROOT/results/install"
cd "$FSI_ROOT/upstream/calculix-adapter"
make -j2 CCX="$FSI_ROOT/upstream/CalculiX/ccx_2.20/src" ADDITIONAL_FFLAGS=-fallow-argument-mismatch > "$FSI_ROOT/results/install/build-calculix.log" 2>&1
cd "$FSI_ROOT/upstream/openfoam-adapter"
export WM_NCOMPPROCS=2
./Allwmake > "$FSI_ROOT/results/install/build-openfoam-adapter.log" 2>&1
