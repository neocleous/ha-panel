#!/bin/sh
# Main board rev 3.2, fab issue 2026-11-16: from rev 3.2 as left on 2026-11-14 to the board the fab files are made of.
# usage: fab32.sh <rev3.2/main-board-rev3.2-2026-11-14.kicad_pcb> <work dir> [pad ...]
#   The work dir gets the board as main-board.kicad_pcb beside main-board.kicad_pro, the schematic files, the library
#   tables and lib/, because KiCad's Python reads the board's rules (net classes, clearances) only from a project file
#   that lies beside the board, and the board check compares with the schematic.
#   The pads named are those whose via is also made 0.2/0.45 (2026-11-16: F4.1 R3.2 C3.2 R8.2 C10.2).
# Result: <work dir>/main-board.kicad_pcb, via-plan.json, via-plan-run.txt, fab32-run.txt, erc.txt, drc.txt
set -e
SRC="$1"; W="$2"; shift 2
G="$(cd "$(dirname "$0")" && pwd)"; M="$(dirname "$G")"; PY="${PYTHON:-python3}"
F='wx\|gtk\|Debug\|memory leak'
export PYTHONHASHSEED=0
mkdir -p "$W"
cp "$M"/main-board.kicad_pro "$M"/*.kicad_sch "$M"/fp-lib-table "$M"/sym-lib-table "$W"/
rm -rf "$W/lib"; cp -r "$M/lib" "$W/lib"
cp "$SRC" "$W/src.kicad_pcb"; cp "$M/main-board.kicad_pro" "$W/src.kicad_pro"
"$PY" "$G/fab32_vias.py" plan "$W/src.kicad_pcb" "$W/via-plan.json" "$@" 2>&1 | grep -v -i "$F" > "$W/via-plan-run.txt"
tail -1 "$W/via-plan-run.txt"
"$PY" "$G/fab32.py" "$W/src.kicad_pcb" "$W/via-plan.json" "$W/main-board.kicad_pcb" 2>&1 | grep -v -i "$F" | tee "$W/fab32-run.txt"
( cd "$W" && kicad-cli sch erc --severity-all --format report -o erc.txt main-board.kicad_sch 2>&1 | grep -i 'found' ; \
  kicad-cli pcb drc --severity-all --schematic-parity --format report -o drc.txt main-board.kicad_pcb 2>&1 | grep -i 'found' )
"$PY" "$G/fab32_vias.py" check "$W/main-board.kicad_pcb" 2>&1 | grep -v -i "$F" | tee "$W/via-check.txt"
rm -f "$W/src.kicad_pcb" "$W/src.kicad_pro" "$W"/*.kicad_prl
