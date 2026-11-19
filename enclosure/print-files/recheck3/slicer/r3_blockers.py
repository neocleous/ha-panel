# recheck3: the shell's support blockers, version 3 = the settled 14 boxes (shell_plan_blk_v2.stl: the chin's bed edges, the ten lip pockets, the exhaust rows)
#   plus one cylinder along each of the four post insert holes (r 2.35, from 0.6 before the mouth to 0.3 past the blind end), so that no support is built inside
#   the holes. Bed frame of the shell (print files' matrix). Also the adhesion test's set (the first 8 mm). Not print files.
import sys, math, numpy as np, trimesh
sys.path.insert(0, '/home/claude/r3/offline')
from r3_gq import BedPart
C12, S12 = math.cos(math.radians(12)), math.sin(math.radians(12))
def slab_to_world(x, up, d): return np.array([x, -d * C12 - up * S12, 143.3 - d * S12 + up * C12])
bp = BedPart('shell', (0, 0, 0)); out = sys.argv[1]
cyls = []
for x, up, d0 in ((70, 27, 12.8), (-70, 27, 12.8), (85, -82, 11.6), (-85, -82, 11.6)):
    a = bp.to_bed(slab_to_world(x, up, d0 - 0.6))[0]; b = bp.to_bed(slab_to_world(x, up, d0 + 6.35 + 0.3))[0]
    c = trimesh.creation.cylinder(radius=2.35, segment=[a, b], sections=48); cyls.append(c)
    print('hole x %+d up %+d: mouth bed %s, blind end bed %s' % (x, up, np.round(bp.to_bed(slab_to_world(x, up, d0))[0], 3), np.round(bp.to_bed(slab_to_world(x, up, d0 + 6.35))[0], 3)))
v2 = trimesh.load('/mnt/user-data/uploads/HA_panel_renders/print_files/_work/orient/shell_plan_blk_v2.stl')
v3 = trimesh.util.concatenate([v2] + cyls); v3.export(out + '/shell_plan_blk_v3.stl')
c8 = trimesh.load('/mnt/user-data/uploads/HA_panel_renders/print_files/_work/orient/shell_chin8_blk.stl')
cut = trimesh.creation.box(extents=(400, 400, 9.0)); cut.apply_translation((128, 128, 3.5))
low = [trimesh.boolean.intersection([c, cut], engine='manifold') for c in cyls[2:]]
a8 = trimesh.util.concatenate([c8] + low); a8.export(out + '/shell_chin8_blk_v3.stl')
print('v3 faces', len(v3.faces), np.round(v3.bounds, 2).tolist(), '| chin8 v3 faces', len(a8.faces), np.round(a8.bounds, 2).tolist())
