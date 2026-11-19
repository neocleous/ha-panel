# The adhesion test's blockers: the shell's blocker mesh (recheck2 slicer/orient/shell_plan_blk_v2.stl, bed frame) clipped to the
#   shell's first 8.0 mm (z -1 to 8): keeps the band along the chin's bed edges (three boxes, bed z -0.2 to 2.2).
# Usage: python3 blk_clip.py <shell_plan_blk_v2.stl> <out shell_chin8_blk.stl>
import sys
import numpy as np
import trimesh
m = trimesh.load(sys.argv[1])
cut = trimesh.creation.box(extents=(400, 400, 9.0)); cut.apply_translation((128, 128, 3.5))
parts = [b for b in m.split(only_watertight=False) if b.bounds[0][2] < 8.0]
out = trimesh.util.concatenate([trimesh.boolean.intersection([b, cut], engine='manifold') for b in parts])
out.export(sys.argv[2])
print(len(parts), 'boxes kept', np.round(out.bounds, 3).tolist())
