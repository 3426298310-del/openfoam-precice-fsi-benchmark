#!/usr/bin/env bash
# Ubuntu 24.04 amd64. Run as the normal user; sudo prompts interactively.
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$root/downloads" "$root/upstream" "$root/results/install"
curl -fsSL https://dl.openfoam.com/add-debian-repo.sh -o "$root/downloads/add-debian-repo.sh"
sudo bash "$root/downloads/add-debian-repo.sh"
curl -fL https://github.com/precice/precice/releases/download/v3.2.0/libprecice3_3.2.0_noble.deb -o "$root/downloads/libprecice3_3.2.0_noble.deb"
sudo apt-get install -y --no-remove --no-install-recommends \
  build-essential cmake git curl pkg-config gfortran libopenmpi-dev \
  openfoam2312-dev=2312.260127-2 libarpack2-dev libspooles-dev libyaml-cpp-dev \
  python3-numpy python3-matplotlib python3-scipy python3-vtk9 paraview \
  "$root/downloads/libprecice3_3.2.0_noble.deb"
# python3-paraview conflicts with the pre-existing ROS/VTK environment on this VM.
clone_at() {
  local repo=$1 rev=$2 path=$3
  if [[ ! -d "$path/.git" ]]; then git clone "$repo" "$path"; fi
  git -C "$path" fetch origin "$rev"
  git -C "$path" checkout --detach "$rev"
}
clone_at https://github.com/precice/openfoam-adapter.git 74b8719ce874c793a581fd009a54c0e1c7923b1e "$root/upstream/openfoam-adapter"
clone_at https://github.com/precice/calculix-adapter.git f362a16d54a31985712f4c4302128f6923bd1d00 "$root/upstream/calculix-adapter"
curl -fL https://www.dhondt.de/ccx_2.20.src.tar.bz2 -o "$root/downloads/ccx_2.20.src.tar.bz2"
tar -xjf "$root/downloads/ccx_2.20.src.tar.bz2" -C "$root/upstream"
"$root/scripts/build-adapters.sh"
