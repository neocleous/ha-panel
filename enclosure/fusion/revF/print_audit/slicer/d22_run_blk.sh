#!/bin/bash
# The built d22 front with the plan's support blockers (pads, exhaust rows, lip magnet pockets) as a 3MF; the audit's settings.
cd "$(dirname "$0")"
python3 d22_blocker_3mf.py /mnt/user-data/uploads/HA_panel_renders/print_audit/exports/front_d22.stl front_d22_blk.3mf all
S=$SECONDS
prusa-slicer --load x2d_asa_assumed.ini --dont-arrange --center 128,128 front_d22_blk.3mf --export-gcode --output gc_front_d22_blk.gcode > log_front_d22_blk.txt 2>&1
echo "front_d22_blk exit $? $((SECONDS-S)) s"
