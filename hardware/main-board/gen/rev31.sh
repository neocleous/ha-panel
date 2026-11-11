#!/bin/sh
# Main board rev 3.1: apply the changes to the routed rev 3 board, stage by stage. Every stage leaves a file.
# usage: rev31.sh <rev 3 board.kicad_pcb> <work dir>     (the work dir needs the .kicad_pro, the schematic files,
#        fp-lib-table, sym-lib-table and lib/ beside the board copy, so that the check includes the schematic)
# KiCad's Python library and kicad-cli run in separate processes (lesson of rev 3).
set -e
SRC="$1"; W="$2"; G="$(cd "$(dirname "$0")" && pwd)"; PY="${PYTHON:-python3}"
F='wx\|gtk\|Debug\|memory leak'
export PYTHONHASHSEED=0      # the router walks sets of names: without this, two runs differ
drc() { kicad-cli pcb drc --format json --severity-all --schematic-parity -o "$1.drc.json" "$1.kicad_pcb" >/dev/null 2>&1; }
count() { "$PY" - "$1.drc.json" "$2" <<'PY'
import json, sys
d = json.load(open(sys.argv[1])); T = sys.argv[2].split(',')
print(sum(1 for v in d['violations'] if v['type'] in T))
PY
}
summary() { "$PY" - "$1.drc.json" <<'PY'
import json, sys
from collections import Counter
d = json.load(open(sys.argv[1]))
print('   check:', dict(Counter((v['severity'], v['type']) for v in d['violations'])) or 'no reports', '| open connections:', len(d['unconnected_items']), '| schematic differences:', len(d.get('schematic_parity', [])))
PY
}
cd "$W"
cp "$SRC" s0.kicad_pcb; cp "$(dirname "$SRC")/$(basename "$SRC" .kicad_pcb).kicad_pro" s0.kicad_pro
echo "1 move"; "$PY" "$G/rev31.py" s0.kicad_pcb s1.kicad_pcb move 2>&1 | grep -v -i "$F"
drc s1; cp s1.kicad_pcb s2.kicad_pcb; cp s1.kicad_pro s2.kicad_pro; cp s1.drc.json s2.drc.json
echo "2 rip"
RIP='clearance,shorting_items,tracks_crossing,hole_clearance,items_not_allowed,solder_mask_bridge,copper_edge_clearance,hole_to_hole'
for k in 1 2 3 4 5 6; do
  [ "$(count s2 $RIP)" = "0" ] && break
  "$PY" "$G/rev31.py" s2.kicad_pcb s2.kicad_pcb rip s2.drc.json 2>&1 | grep -v -i "$F"; drc s2
done
echo "3 route"; "$PY" "$G/rev31.py" s2.kicad_pcb s3.kicad_pcb route 2>&1 | grep -v -i "$F"; drc s3; summary s3
echo "4 loose ends"
cp s3.kicad_pcb s4.kicad_pcb; cp s3.kicad_pro s4.kicad_pro
for k in 1 2 3 4 5 6 7 8 9 10 11 12; do
  drc s4; N=$("$PY" "$G/route_rev3.py" s4.kicad_pcb s4.drc.json loose 2>/dev/null | grep "loose ends removed" | awk '{print $4}')
  echo "   pass $k: removed ${N:-?}"; [ "${N:-0}" = "0" ] && break
done
echo "5 copper"; "$PY" "$G/rev31.py" s4.kicad_pcb s5.kicad_pcb copper 2>&1 | grep -v -i "$F"; drc s5; summary s5
echo "6 finish"; "$PY" "$G/rev31.py" s5.kicad_pcb s6.kicad_pcb finish 2>&1 | grep -v -i "$F" | grep -E "stitch vias|rror" || true; drc s6; summary s6
cp s6.kicad_pcb s7.kicad_pcb; cp s6.kicad_pro s7.kicad_pro
for k in 1 2 3 4 5 6; do
  drc s7; N=$("$PY" "$G/route_rev3.py" s7.kicad_pcb s7.drc.json loose 2>/dev/null | grep "loose ends removed" | awk '{print $4}')
  echo "   loose ends after the pours, pass $k: removed ${N:-?}"; [ "${N:-0}" = "0" ] && break
done
echo "7 text"; "$PY" "$G/rev31.py" s7.kicad_pcb s8.kicad_pcb text s7.drc.json 2>&1 | grep -v -i "$F"; drc s8; summary s8
