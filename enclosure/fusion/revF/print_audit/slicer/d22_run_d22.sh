#!/bin/bash
# The built d22 front (v5f_d22f export), same settings as the audit's front slice.
cd "$(dirname "$0")"
S=$SECONDS
prusa-slicer --load x2d_asa_assumed.ini --dont-arrange --center 128,128 /mnt/user-data/uploads/HA_panel_renders/print_audit/exports/front_d22.stl --export-gcode --output gc_front_d22.gcode > log_front_d22.txt 2>&1
echo "front_d22 exit $? $((SECONDS-S)) s"
