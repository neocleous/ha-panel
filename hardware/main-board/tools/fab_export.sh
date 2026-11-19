#!/bin/sh
# One JLC fab set from one KiCad board: Gerbers, drill files, drill report, job file and the zip to upload.
# usage: fab_export.sh <board.kicad_pcb> <stem> <fab dir> <date> <layers, comma separated>
#   <stem>  the name every file gets, with board and revision in it (e.g. main-board-rev3.2), so that the files of
#           two sets cannot be mixed. The board is plotted from a copy of that name: KiCad names its outputs after
#           the board file, and the Gerbers' own header then carries it too.
#   Result: <fab dir>/<stem>-jlc-<date>.zip, <fab dir>/gerbers/ (the same files unzipped), <fab dir>/drill-report.txt
# Settings: JLC's "How to generate Gerber and Drill files in KiCad 9" (read 2026-11-16): Protel extensions, X2
# attributes, netlist attributes, format 4.6 mm; drill files Excellon, plated and non-plated holes in separate files,
# absolute origin, millimetres, decimal zeros, oval holes in alternate mode. Also: no value texts, and the soldermask
# is subtracted from the silkscreen (not in JLC's guide; it keeps the print off the pads). kicad-cli 9.0.9.
set -e
B="$1"; STEM="$2"; OUT="$3"; DATE="$4"; LAYERS="$5"
SRC="$(cd "$(dirname "$B")" && pwd)"; BASE="$(basename "$B" .kicad_pcb)"
T="$(mktemp -d)"
cp "$B" "$T/$STEM.kicad_pcb"
[ -f "$SRC/$BASE.kicad_pro" ] && cp "$SRC/$BASE.kicad_pro" "$T/$STEM.kicad_pro"
mkdir -p "$T/g" "$OUT"
kicad-cli pcb export gerbers --layers "$LAYERS" --exclude-value --subtract-soldermask -o "$T/g/" "$T/$STEM.kicad_pcb" 2>&1 | grep -v -i 'wx\|gtk\|Debug' || true
kicad-cli pcb export drill --format excellon --drill-origin absolute --excellon-zeros-format decimal --excellon-units mm \
  --excellon-separate-th --excellon-oval-format alternate --generate-report --report-path "$T/drill-report.txt" -o "$T/g/" "$T/$STEM.kicad_pcb" 2>&1 | grep -v -i 'wx\|gtk\|Debug' || true
rm -rf "$OUT/gerbers"; mkdir -p "$OUT/gerbers"
cp "$T"/g/* "$OUT/gerbers/"
cp "$T/drill-report.txt" "$OUT/drill-report.txt"
rm -f "$OUT/$STEM-jlc-$DATE.zip"
( cd "$OUT/gerbers" && zip -q -X "../$STEM-jlc-$DATE.zip" * )
rm -rf "$T"
ls "$OUT/gerbers" | tr '\n' ' '; echo
sha256sum "$OUT/$STEM-jlc-$DATE.zip"
