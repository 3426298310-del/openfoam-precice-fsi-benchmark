#!/usr/bin/env bash
# Each run is isolated and refuses to overwrite an existing directory.
set -eo pipefail
ulimit -c 0
source "$(dirname "$0")/env.sh"
set -u
name=${1:-smoke}
end=${2:-0.01}
dt=${3:-0.01}
variant=${4:-fsi1}
case_root="$FSI_ROOT"
if [[ "$variant" == fsi3 ]]; then case_root="$FSI_ROOT/experimental/fsi3"; elif [[ "$variant" != fsi1 ]]; then exit 2; fi
[[ "$name" =~ ^[a-zA-Z0-9_-]+$ ]] || { echo 'Invalid run name'; exit 2; }
run="$FSI_ROOT/results/runs/$name"
mkdir -p "$(dirname "$run")"
mkdir "$run"
cp -r "$case_root/fluid" "$case_root/solid" "$case_root/coupling" "$run/"
python3 - "$run" "$end" "$dt" "$variant" <<'PY'
from pathlib import Path
import sys,re,json,datetime
r=Path(sys.argv[1]);end=float(sys.argv[2]);dt=float(sys.argv[3]);assert 0<end<=20 and dt in (0.0005,0.001,0.005,0.01)
p=r/'coupling/precice-config.xml';s=re.sub(r'<max-time value="[^"]+"',f'<max-time value="{end}"',p.read_text());s=re.sub(r'<time-window-size value="[^"]+"',f'<time-window-size value="{dt}"',s);p.write_text(s)
p=r/'fluid/system/controlDict';s=re.sub(r'endTime\s+[^;]+;',f'endTime {end};',p.read_text());s=re.sub(r'writeInterval\s+0.1;',f'writeInterval {min(end,0.1)};',s);s=re.sub(r'deltaT\s+[^;]+;',f'deltaT {dt};',s);p.write_text(s)
p=r/'solid/turekflap.inp';s=re.sub(r'(?m)^0\.0(?:005|1), 20\.0$',f'{dt}, {end}',p.read_text()).replace('*NODE FILE','*NODE FILE, FREQUENCY=200').replace('*EL FILE','*EL FILE, FREQUENCY=200');p.write_text(s)
(r/'run.json').write_text(json.dumps({'name':r.name,'end_time':end,'dt':dt,'benchmark':sys.argv[4],'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'running'},indent=2)+'\n')
PY
cd "$run/fluid"
blockMesh > blockMesh.log 2>&1
checkMesh > checkMesh.log 2>&1
pimpleFoam > fluid.log 2>&1 &
fpid=$!
cd "$run/solid"
ccx_preCICE -i turekflap -precice-participant Solid > solid.log 2>&1 &
spid=$!
cleanup() { kill "$fpid" "$spid" 2>/dev/null || true; }
trap cleanup EXIT INT TERM
# Fail fast if either participant exits unsuccessfully.
set +e
wait -n "$fpid" "$spid"; rc=$?
if [ "$rc" -eq 0 ]; then wait "$fpid"; fr=$?; wait "$spid"; sr=$?; rc=$((fr+sr)); fi
set -e
python3 - "$run" "$rc" <<'PY'
from pathlib import Path
import sys,json,datetime
p=Path(sys.argv[1])/'run.json';d=json.loads(p.read_text());d.update(status='completed' if int(sys.argv[2])==0 else 'failed',exit_code=int(sys.argv[2]),finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());p.write_text(json.dumps(d,indent=2)+'\n')
PY
exit "$rc"
