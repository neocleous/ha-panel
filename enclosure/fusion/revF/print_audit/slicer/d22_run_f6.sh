#!/bin/bash
cd "$(dirname "$0")"
U=/mnt/user-data/uploads/HA_panel_renders/print_audit/exports
run() { local t=$1; shift; local S=$SECONDS
  prusa-slicer --load x2d_asa_assumed.ini --dont-arrange --center 128,128 "$@" --export-gcode --output gc_$t.gcode > log_$t.txt 2>&1
  echo "$t exit $? $((SECONDS-S)) s"; }
run front_base $U/front.stl &
run front_web --merge $U/front.stl cand_web_SR.stl cand_web_SL.stl &
run front_webfrib --merge $U/front.stl cand_web_SR.stl cand_web_SL.stl cand_frib_SR.stl cand_frib_SL.stl &
wait; echo ALLDONE
