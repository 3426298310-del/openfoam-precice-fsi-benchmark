#!/usr/bin/env bash
# Source this file; do not enable nounset until OpenFOAM has loaded.
FSI_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
fsi_shell_flags=$-
set +eu
source /usr/lib/openfoam/openfoam2312/etc/bashrc
[[ "$fsi_shell_flags" == *e* ]] && set -e
[[ "$fsi_shell_flags" == *u* ]] && set -u
export PATH="$FSI_ROOT/upstream/calculix-adapter/bin:$PATH"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
