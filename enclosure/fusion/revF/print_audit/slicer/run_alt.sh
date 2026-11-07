# Alternative orientations (P11 re-check of the Majors). Same assumed profile; nb = dont_support_bridges off.
cd /home/claude/pa/slice
for t in grommet_side+x grommet_side+z grommet_flange_up bracket_L_flat+y bracket_R_flat+y bracket_L_flat-y bracket_R_flat-y; do
  S=$SECONDS
  prusa-slicer --load x2d_asa_assumed.ini --export-gcode --output gc_${t}.gcode orient/${t}.stl > log_${t}.txt 2>&1
  echo "$t exit $? $((SECONDS-S)) s"
done
for t in bracket_L_flat+y bracket_R_flat+y; do
  S=$SECONDS
  prusa-slicer --load x2d_asa_assumed.ini --no-dont-support-bridges --export-gcode --output gc_${t}_nb.gcode orient/${t}.stl > log_${t}_nb.txt 2>&1
  echo "${t}_nb exit $? $((SECONDS-S)) s"
done
echo ALLDONE
