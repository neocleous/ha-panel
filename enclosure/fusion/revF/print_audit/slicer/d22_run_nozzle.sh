#!/bin/bash
# Door and speaker boxes: 0.4 / 0.20 (the audit's ASSUMED profile) vs 0.6 / 0.30, same flow cap (18 mm3/s), with and without supports.
cd "$(dirname "$0")"
U=/mnt/user-data/uploads/HA_panel_renders/print_audit/exports
O6="--nozzle-diameter 0.6 --layer-height 0.3 --first-layer-height 0.3 --external-perimeter-extrusion-width 0.62 --perimeter-extrusion-width 0.65 --extrusion-width 0.65 --infill-extrusion-width 0.65 --solid-infill-extrusion-width 0.62 --top-infill-extrusion-width 0.62 --first-layer-extrusion-width 0.7 --support-material-extrusion-width 0.62 --support-material-contact-distance 0.3"
NOS="--no-support-material --no-support-material-auto"
run() { # tag stl rot extra...
  local t=$1 f=$2 r=$3; shift 3; local S=$SECONDS
  prusa-slicer --load x2d_asa_assumed.ini $r "$@" --export-gcode --output gc_$t.gcode $f > log_$t.txt 2>&1
  echo "$t exit $? $((SECONDS-S)) s"
}
run door_04 $U/door.stl ""
run door_06 $U/door.stl "" $O6
run door_04_nosup $U/door.stl "" $NOS
run door_06_nosup $U/door.stl "" $O6 $NOS
for b in spkbox_L spkbox_R; do
  run ${b}_04 $U/$b.stl "--rotate-x 90"
  run ${b}_06 $U/$b.stl "--rotate-x 90" $O6
done
echo ALLDONE
