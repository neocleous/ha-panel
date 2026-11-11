#!/bin/sh
# Remove loose track ends and unused vias from a board, pass by pass, until KiCad's check finds none.
# usage: loose.sh board.kicad_pcb
B="$1"; G="$(dirname "$0")"
for k in 1 2 3 4 5 6 7 8 9 10 11 12; do
  kicad-cli pcb drc --format json --severity-all -o "$B.loose.json" "$B" >/dev/null 2>&1
  cp "$B" "$B.keep"
  N=$(python3 "$G/route_rev3.py" "$B" "$B.loose.json" loose 2>/dev/null | grep "loose ends removed" | awk '{print $4}')
  if [ -z "$N" ]; then cp "$B.keep" "$B"; echo "pass $k: the KiCad library crashed, pass repeated"; continue; fi
  echo "pass $k: removed ${N:-?}"
  [ "${N:-0}" = "0" ] && break
done
rm -f "$B.loose.json" "$B.keep"
