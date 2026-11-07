# P5 / P9: horizontal faces in the build frame -> nominal z, printed z (PrusaSlicer convention: layer k printed iff its
# mid-plane + 2e-4 lies inside the solid; first layer 0.2), error; thin horizontal slabs (< 0.2) found by pairing an up face
# with the down face directly below it.
import sys, json, numpy as np, trimesh
sys.path.insert(0, '/home/claude/pa')
from pa_geom import *
def printed_top(zt):     # top face at zt -> printed top
    k = np.floor((zt - 0.1 - EPS) / 0.2)    # last layer whose mid+eps < zt
    return (k + 1) * 0.2
def printed_bot(zb):     # bottom face at zb -> printed bottom (first layer whose mid+eps > zb)
    k = np.ceil((zb - 0.1 - EPS) / 0.2)
    return max(k, 0) * 0.2
out = {}
for tag in ORIENT:
    mw = load_world(tag); mb, M = to_build(mw, ORIENT[tag]['plan'])
    n = mb.face_normals; a = mb.area_faces; c = mb.triangles_center
    rows = []
    for sgn, kind in ((1, 'up'), (-1, 'down')):
        sel = (n[:, 2] * sgn) > 0.9995
        if not sel.any(): continue
        zz = np.round(c[sel, 2], 3); aa = a[sel]
        for zv in np.unique(zz):
            A_ = float(aa[zz == zv].sum())
            if A_ < 0.5: continue
            pz = printed_top(zv) if kind == 'up' else printed_bot(zv)
            rows.append([kind, float(zv), round(A_, 1), round(float(pz), 2), round(float(pz - zv), 3)])
    rows.sort(key=lambda r: r[1])
    out[tag] = rows
    bad = [r for r in rows if abs(r[4]) >= 0.099]
    print(tag, 'levels', len(rows), 'with |error| ~0.1:', len(bad), [(r[0], r[1], r[2]) for r in bad][:12])
json.dump(out, open('/home/claude/pa/data/zq.json', 'w'))
