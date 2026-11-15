# recheck2 block 1: geometry survey of one printed part in its planned orientation (world STL -> build frame).
#   Usage: python3 r2_survey.py <tag> [px]   -> /home/claude/r2/data/survey_<tag>.json
#   Mesh check (watertight, volume against Fusion's B-rep), build height and layers (0.20 first, 0.20 after; Bambu samples each layer
#   on its mid-plane), bed contact (faces on z 0 facing down) and the first layer's section, down-facing area by angle from vertical
#   (bed excluded), down-facing area grouped by height band, islands (regions of a layer that have nothing under them in the layer
#   below), centre of mass against the first layer's hull.
import sys, json, math, os, numpy as np, trimesh
from scipy import ndimage as ndi
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r2_geom as g

tag = sys.argv[1]; px = float(sys.argv[2]) if len(sys.argv) > 2 else 0.1
FUS = {}
for f in ('r2_1_export_screen.json', 'r2_1_export_carrier.json'):
    p = '/mnt/user-data/uploads/print_audit_recheck2/data/' + f
    if os.path.exists(p):
        FUS.update({k: v for k, v in json.load(open(p)).items() if isinstance(v, dict)})
mw = g.load_world(tag)
U = g.ORIENT[tag]['plan']
mb, M = g.to_build(mw, U)
out = {'tag': tag, 'U': list(map(float, U)), 'watertight': bool(mw.is_watertight), 'vol_mesh': round(float(mw.volume), 2),
       'vol_brep': FUS.get(tag, {}).get('vol_mm3'), 'tris': int(len(mw.faces))}
out['height'] = round(float(mb.extents[2]), 3)
out['bbox_build'] = np.round(mb.bounds, 3).tolist()
H = mb.extents[2]
mids = g.layer_mids(H)
out['layers'] = int(len(mids))
# bed faces
n = mb.face_normals; a = mb.area_faces; fz = mb.vertices[mb.faces][:, :, 2]
bed = (fz < 0.01).all(1) & (n[:, 2] < -0.99)
out['bed_faces_mm2'] = round(float(a[bed].sum()), 1)
out['overhang'] = g.overhang_stats(mb)
# down-facing (>= 45 deg from vertical, not bed) by height band
down = (n[:, 2] < -math.sin(math.radians(45))) & ~bed
zc = fz.mean(1)
bands = [0, 0.3, 1, 2, 5, 10, 20, 30, 40, 50, 60, 70, 80, 200]
out['down45_by_height'] = {'%g-%g' % (bands[i], bands[i + 1]): round(float(a[down & (zc >= bands[i]) & (zc < bands[i + 1])].sum()), 1)
                           for i in range(len(bands) - 1) if a[down & (zc >= bands[i]) & (zc < bands[i + 1])].sum() > 0.05}
# sections: first layer and islands
S = g.Slicer(mb)
x0, y0, W, Hh = g.grid_for(mb, px)
prev = None; isl = []; areas = []
for k, z in enumerate(mids):
    zz = z + g.EPS
    R = g.raster(S.segments(zz), x0, y0, px, W, Hh)
    areas.append(float(R.sum()) * px * px)
    if k == 0:
        out['first_layer_mm2'] = round(areas[0], 1)
        ys, xs = np.nonzero(R)
        if len(xs):
            from shapely.geometry import MultiPoint
            pts = np.c_[x0 + (xs + 0.5) * px, y0 + (ys + 0.5) * px]
            hull = MultiPoint(pts[::max(1, len(pts) // 20000)]).convex_hull
            com_b = (M @ np.r_[mw.center_mass, 1.0])[:3]
            from shapely.geometry import Point
            out['com_build'] = np.round(com_b, 2).tolist()
            out['com_in_first_hull'] = bool(hull.contains(Point(com_b[0], com_b[1])))
            out['com_to_hull_edge'] = round(float(hull.exterior.distance(Point(com_b[0], com_b[1]))), 2)
            out['first_hull_mm2'] = round(hull.area, 1)
    else:
        lab, nl = ndi.label(R)
        if nl:
            sup = ndi.binary_dilation(prev, iterations=max(1, int(round(0.2 / px))))   # 0.2 overlap tolerance
            hit = ndi.sum(sup, lab, index=np.arange(1, nl + 1))
            cnt = ndi.sum(np.ones_like(R), lab, index=np.arange(1, nl + 1))
            for i in np.nonzero(hit == 0)[0]:
                ar = float(cnt[i]) * px * px
                if ar >= 0.05:
                    ys, xs = np.nonzero(lab == i + 1)
                    cb = (x0 + (xs.mean() + 0.5) * px, y0 + (ys.mean() + 0.5) * px, z)
                    cw = g.b2w(M, [cb])[0]
                    isl.append({'layer': k, 'z': round(float(z), 2), 'area': round(ar, 2), 'world': np.round(cw, 1).tolist()})
    prev = R
out['islands'] = isl[:200]; out['n_islands'] = len(isl)
out['area_by_layer_max'] = round(max(areas), 1)
out['M_world_to_build'] = M.tolist()
os.makedirs('/home/claude/r2/data', exist_ok=True)
json.dump(out, open('/home/claude/r2/data/survey_%s.json' % tag, 'w'), indent=1)
o = dict(out); o.pop('M_world_to_build'); o['islands'] = isl[:25]
print(json.dumps(o))
