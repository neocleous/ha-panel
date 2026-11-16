#!/bin/sh
# The combined stencil's upload: F.Paste and both outlines from the generated stencil file, nothing else.
# usage: stencil_export.sh <stencil-main-touch.kicad_pcb> <stem> <fab dir> <date>
#   <stem> carries both boards' revisions, e.g. stencil-main-rev3.2-touch-revD (the files are plotted from a copy of
#   that name, as in fab_export.sh). Result: <fab dir>/<stem>-jlc-<date>.zip and <fab dir>/gerbers/. kicad-cli 9.0.9.
set -e
B="$1"; STEM="$2"; OUT="$3"; DATE="$4"
SRC="$(cd "$(dirname "$B")" && pwd)"; BASE="$(basename "$B" .kicad_pcb)"
T="$(mktemp -d)"
cp "$B" "$T/$STEM.kicad_pcb"
[ -f "$SRC/$BASE.kicad_pro" ] && cp "$SRC/$BASE.kicad_pro" "$T/$STEM.kicad_pro"
mkdir -p "$T/g" "$OUT"
kicad-cli pcb export gerbers --layers F.Paste,Edge.Cuts --exclude-value -o "$T/g/" "$T/$STEM.kicad_pcb" 2>&1 | grep -v -i 'wx\|gtk\|Debug' || true
rm -rf "$OUT/gerbers"; mkdir -p "$OUT/gerbers"
cp "$T"/g/* "$OUT/gerbers/"
rm -f "$OUT/$STEM-jlc-$DATE.zip"
( cd "$OUT/gerbers" && zip -q -X "../$STEM-jlc-$DATE.zip" * )
rm -rf "$T"
ls "$OUT/gerbers" | tr '\n' ' '; echo
sha256sum "$OUT/$STEM-jlc-$DATE.zip"
