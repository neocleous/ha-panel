#!/bin/sh
# Does a board file still give the fab set that is already uploaded? Exports the set afresh and compares it, file by
# file, with the zip. Lines that carry the time of the export are left out of the comparison; nothing else is.
# usage: fab_same.sh board   <board.kicad_pcb> <stem> <layers, comma separated> <uploaded.zip>
#        fab_same.sh stencil <stencil.kicad_pcb> <stem> <uploaded.zip>
#   <stem> and <layers> as in fab_export.sh / stencil_export.sh, which make the fresh set (same settings as the upload).
# Prints one line per file and the zip's sha256; ends with status 1 if a file differs or is missing.
# Use: after a change that must not reach the fab (a value, a part number, a field), to prove that it did not.
set -e
MODE="$1"; B="$2"; STEM="$3"
G="$(cd "$(dirname "$0")" && pwd)"
T="$(mktemp -d)"
if [ "$MODE" = board ]; then
  LAYERS="$4"; ZIP="$5"
  sh "$G/fab_export.sh" "$B" "$STEM" "$T/new" 0000-00-00 "$LAYERS" > /dev/null
else
  ZIP="$4"
  sh "$G/stencil_export.sh" "$B" "$STEM" "$T/new" 0000-00-00 > /dev/null
fi
mkdir "$T/old"; unzip -q "$ZIP" -d "$T/old"
F='CreationDate\|^G04 Created by KiCad\|^; DRILL file {KiCad'
BAD=0
echo "fresh export of $(basename "$B") against $(basename "$ZIP")"
for f in $(ls "$T/old"); do
  if [ ! -f "$T/new/gerbers/$f" ]; then echo "  $f: MISSING in the fresh export"; BAD=1; continue; fi
  grep -v "$F" "$T/old/$f" > "$T/a"; grep -v "$F" "$T/new/gerbers/$f" > "$T/b"
  N=$(diff "$T/a" "$T/b" | grep -c '^[<>]' || true)
  D=$(grep -c "$F" "$T/old/$f" || true)
  echo "  $f: $(wc -l < "$T/old/$f") lines, $D with the export's time left out, $N differ"
  [ "$N" = 0 ] || BAD=1
done
for f in $(ls "$T/new/gerbers"); do [ -f "$T/old/$f" ] || { echo "  $f: only in the fresh export"; BAD=1; }; done
echo "  zip sha256 $(sha256sum "$ZIP" | cut -d' ' -f1)"
[ "$BAD" = 0 ] && echo "  result: the same set" || echo "  result: DIFFERENT"
rm -rf "$T"
exit $BAD
