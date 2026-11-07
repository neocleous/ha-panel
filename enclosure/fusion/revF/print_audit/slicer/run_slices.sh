cd /home/claude/pa/slice
for t in clip_L clip_R grommet bme_hood cradle bracket_L bracket_R resp_carrier cap spkbox_L spkbox_R door slab front; do
  S=$SECONDS
  prusa-slicer --load x2d_asa_assumed.ini --export-gcode --output gc_${t}_plan.gcode orient/${t}_plan.stl > log_${t}_plan.txt 2>&1
  echo "$t exit $? $((SECONDS-S)) s"
done
echo ALLDONE
