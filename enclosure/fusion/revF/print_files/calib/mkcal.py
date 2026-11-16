# Calibration plate parts (print files, 2026-11-16), bed frame, mm, each centred on (0, 0) and standing on z = 0.
#   cal_frame   square frame 120 x 120 outside, 108 x 108 inside, 5.0 tall: Shrinkage (XY) from outside + inside sizes
#               (line-width errors push the outside out and the inside in by the same amount; their sum keeps only the scale)
#   cal_tower   block 20 x 20 x 30.0: Z shrink (its height) and elephant foot (width at the first layer against mid-height)
#   cal_holes   block 40 x 16 x 8.0: two blind 4.0 holes 6.0 deep (Ruthex M3 x 5.7 hole), two 3.4 through holes (M3 clearance)
# Usage: python3 mkcal.py <outdir>
import sys, os
import numpy as np
import trimesh

out = sys.argv[1] if len(sys.argv) > 1 else 'cal'
os.makedirs(out, exist_ok=True)


def box(sx, sy, sz, cx=0.0, cy=0.0, z0=0.0):
    b = trimesh.creation.box(extents=(sx, sy, sz))
    b.apply_translation((cx, cy, z0 + sz / 2.0))
    return b


def cyl(d, h, cx, cy, z0, sections=96):
    c = trimesh.creation.cylinder(radius=d / 2.0, height=h, sections=sections)
    c.apply_translation((cx, cy, z0 + h / 2.0))
    return c


parts = {}
parts['cal_frame'] = trimesh.boolean.difference([box(120.0, 120.0, 5.0), box(108.0, 108.0, 7.0, z0=-1.0)], engine='manifold')
parts['cal_tower'] = box(20.0, 20.0, 30.0)
blk = box(40.0, 16.0, 8.0)
holes = [cyl(4.0, 6.0 + 1.0, -13.0, 0.0, 2.0), cyl(4.0, 6.0 + 1.0, -4.0, 0.0, 2.0),
         cyl(3.4, 10.0, 5.0, 0.0, -1.0), cyl(3.4, 10.0, 14.0, 0.0, -1.0)]
parts['cal_holes'] = trimesh.boolean.difference([blk] + holes, engine='manifold')

for name, m in parts.items():
    m.merge_vertices(); m.fix_normals()
    assert m.is_watertight and m.is_winding_consistent, name
    p = os.path.join(out, name + '.stl')
    m.export(p)
    print(name, 'tris', len(m.faces), 'vol %.2f' % m.volume, 'bounds', np.round(m.bounds, 3).tolist())
