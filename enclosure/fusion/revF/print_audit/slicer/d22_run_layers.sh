#!/bin/bash
# Visible prints at the planned layer heights vs the audit's 0.20 (0.4 nozzle, ASSUMED profile; first layer 0.20).
cd "$(dirname "$0")"
U=/mnt/user-data/uploads/HA_panel_renders/print_audit/exports
run() { local t=$1 f=$2 r=$3; shift 3; local S=$SECONDS
  prusa-slicer --load x2d_asa_assumed.ini $r "$@" --export-gcode --output gc_$t.gcode $f > log_$t.txt 2>&1
  echo "$t exit $? $((SECONDS-S)) s"; }
run cap_020 $U/cap.stl "--rotate-x 180"
run cap_012 $U/cap.stl "--rotate-x 180" --layer-height 0.12
run slab_020 $U/slab.stl "--rotate-x -102"
run slab_010 $U/slab.stl "--rotate-x -102" --layer-height 0.1
run grommet_020 $U/grommet.stl ""
run grommet_012 $U/grommet.stl "" --layer-height 0.12
echo ALLDONE
