# recheck3: support blockers for the screen plate: one box over the peg pocket and one over the peg slot (bed z -0.2 to 1.6, 0.6 beyond each outline),
#   so that the border's support does not also fill them: their floors bridge as before (PR19). Bed frame of the screen plate. Not a print file.
import sys, numpy as np, trimesh, shapely
sys.path.insert(0, '/home/claude/r3/offline')
from r3_gq import BedPart, polys_of
bp = BedPart('screen', (0, 0, 0)); L1 = bp.layer(0.1); L8 = bp.layer(1.5); out = sys.argv[1]; boxes = []
for p in polys_of(L1):
    for r in p.interiors:
        H = shapely.geometry.Polygon(r)
        if 40 < H.area < 100:                                          # the peg pocket (53.4 mm2) and the peg slot (80.4 mm2), 1.4 deep, a screw hole through each
            b = H.bounds; w = bp.to_world([[b[0], b[1], 0], [b[2], b[3], 0]])
            print('hole %.1f mm2 bed x %.2f..%.2f y %.2f..%.2f | world x %.1f..%.1f z %.1f..%.1f' % (H.area, b[0], b[2], b[1], b[3], w[:, 0].min(), w[:, 0].max(), w[:, 2].min(), w[:, 2].max()))
            m = trimesh.creation.box(extents=(b[2] - b[0] + 1.2, b[3] - b[1] + 1.2, 1.8)); m.apply_translation(((b[0] + b[2]) / 2, (b[1] + b[3]) / 2, 0.7)); boxes.append(m)
assert len(boxes) == 2
trimesh.util.concatenate(boxes).export(out + '/screen_plan_blk.stl'); print('written', len(boxes), 'boxes')
