# The diagnostic box for X7_T4_lipfill (slicer/diag67.py; not a print file): x 36 to 220, y 87.15 to 89.35, z 0 to 0.45 in the
#   shell's bed frame, joined to the shell in that job so that the band along the chin's top edge stands on the bed.
# Usage: python3 diag_lipfill_box.py <out.stl>
import sys, trimesh
b = trimesh.creation.box(extents=(220 - 36, 89.35 - 87.15, 0.45)); b.apply_translation(((36 + 220) / 2, (87.15 + 89.35) / 2, 0.225))
b.export(sys.argv[1]); print(b.bounds.tolist(), round(b.volume, 2), b.is_watertight)
