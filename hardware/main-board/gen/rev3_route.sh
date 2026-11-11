#!/bin/sh
# Main board rev 3: build the board from the netlist and the floor plan, then route it. Every stage leaves a file.
# usage: rev3_route.sh <netlist> <work dir>       (run from hardware/main-board; the work dir needs copies of the
#        schematic files and lib tables if the last check is to include schematic parity)
set -e
NET="$1"; W="$2"; G="$(cd "$(dirname "$0")" && pwd)"; HERE="$(pwd)"
F='wx\|gtk\|Debug\|memory leak'
python3 "$G/pcb_rev3.py" "$NET" rev3/floorplan.json rev2.1/main-board.kicad_pcb "$W/s0.kicad_pcb" 2>&1 | grep -v -i "$F" | tail -1
cd "$W"
python3 "$G/route_rev3.py" s0.kicad_pcb s2.kicad_pcb power planes 2>&1 | grep -v -i "$F" | grep -E "plane|False|stubs" || true
python3 "$G/route_rev3.py" s2.kicad_pcb s3.kicad_pcb signals fill 2>&1 | grep -v -i "$F" | grep -E "round|OPEN|THIN|rror" || true
cp s3.kicad_pcb s4.kicad_pcb; cp s3.kicad_pro s4.kicad_pro; "$G/loose.sh" s4.kicad_pcb | tr '\n' ' '; echo
python3 "$G/route_rev3.py" s4.kicad_pcb s5.kicad_pcb finish 2>&1 | grep -v -i "$F" | grep -E "stitch vias|rror" || true
"$G/loose.sh" s5.kicad_pcb | tr '\n' ' '; echo
python3 "$G/route_rev3.py" s5.kicad_pcb s6.kicad_pcb silk 2>&1 | grep -v -i "$F" | grep -E "silk|rror" || true
kicad-cli pcb drc --format json --severity-all -o drc6.json s6.kicad_pcb >/dev/null 2>&1
python3 - <<'PY'
import json
d = json.load(open('drc6.json'))
from collections import Counter
print('check of s6:', dict(Counter((v['severity'], v['type']) for v in d['violations'])), '| open connections:', len(d['unconnected_items']))
PY
cd "$HERE"
