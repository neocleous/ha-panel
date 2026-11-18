# recheck3: the calibration plate's hole block for version 67 (FDM9's first-print test). The print files' block (print_files/calib/mkcal.py:
#   40 x 16 x 8, two blind 4.0 holes 6 deep, two 3.4 through holes) with a lug joined to its end: 8 long, 16 wide, 6.7 tall, and a
#   sideways pilot 2.7 x 5.5 lying in the layers, axis 3.35 above the bed. As in the boxes' touch-clip block (version 67) the pilot has
#   2.0 of plastic under it and 2.0 over it along the print height, and 6.65 beside it in the layers (6.6 in the boxes).
#   Bed frame, mm; the 40 x 16 block centred on (0, 0) as before, the lug from x 20 to 28. Not a print file.
import sys, os, numpy as np, trimesh
out = sys.argv[1]
def box(x0, x1, y0, y1, z0, z1):
    b = trimesh.creation.box(extents=(x1 - x0, y1 - y0, z1 - z0)); b.apply_translation(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)); return b
def cylz(d, h, cx, cy, z0, sections=96):
    c = trimesh.creation.cylinder(radius=d / 2.0, height=h, sections=sections); c.apply_translation((cx, cy, z0 + h / 2.0)); return c
def cylx(d, x0, x1, cy, cz, sections=96):
    c = trimesh.creation.cylinder(radius=d / 2.0, height=x1 - x0, sections=sections)
    c.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0])); c.apply_translation(((x0 + x1) / 2, cy, cz)); return c
body = trimesh.boolean.union([box(-20, 20, -8, 8, 0, 8), box(19.9, 28, -8, 8, 0, 6.7)], engine='manifold')
holes = [cylz(4.0, 7.0, -13.0, 0.0, 2.0), cylz(4.0, 7.0, -4.0, 0.0, 2.0), cylz(3.4, 10.0, 5.0, 0.0, -1.0), cylz(3.4, 10.0, 14.0, 0.0, -1.0),
         cylx(2.7, 22.5, 29.0, 0.0, 3.35)]
m = trimesh.boolean.difference([body] + holes, engine='manifold')
m.merge_vertices(); m.fix_normals()
assert m.is_watertight and m.is_winding_consistent
m.export(os.path.join(out, 'cal_holes_v67.stl'))
print('cal_holes_v67 tris', len(m.faces), 'vol %.2f' % m.volume, 'bounds', np.round(m.bounds, 3).tolist())
