"""Block 0/1: the audit meshes against the guard volumes; print frames; first-layer areas."""
import sys, time, numpy as np
from fdm_lib import *
for name in GUARD:
    t0 = time.time()
    m = load_model_mesh(name)
    dv = m.volume - GUARD[name]
    line = '%-16s wt %s vol %.2f (guard %+.3f) tris %d' % (name, m.is_watertight, m.volume, dv, len(m.faces))
    if PARTS[name]['up'] is not None:
        p = Part(name)
        w = p.uvh_to_world([[0, 0, 0]])[0]
        line += ' | height %.2f bed@world (y %.3f z %.3f)' % (p.height, w[1], w[2])
    print(line)
# BME hood: largest planar facet groups
m = load_model_mesh('BME_HOOD')
fa = m.area_faces; fn = m.face_normals
keys = np.round(fn, 3)
uniq, inv = np.unique(keys, axis=0, return_inverse=True)
ar = np.bincount(inv.ravel(), weights=fa)
o = np.argsort(-ar)[:6]
for i in o:
    print('hood normal', uniq[i], 'area %.1f' % ar[i], 'world n', np.round([uniq[i]@XW, uniq[i]@YW, uniq[i]@ZW], 3))
