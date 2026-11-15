# recheck2: world -> bed matrices for the planned orientations (r2_geom.ORIENT), bbox centre at (cx, cy) on the bed, z_min 0.
# Usage: python3 orient2.py tag[:okey[:spin[:cx:cy]]] ...  -> /home/claude/r2/data/orient_<tag>_<okey>.json (+ prints a summary)
import sys, json, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r2_geom as g
for arg in sys.argv[1:]:
    p = arg.split(':'); tag = p[0]; okey = p[1] if len(p) > 1 else 'plan'
    spin = float(p[2]) if len(p) > 2 and p[2] != 'x' else 0.0; cx, cy = (float(p[3]), float(p[4])) if len(p) > 4 else (128.0, 128.0)
    U = g.ORIENT[tag][okey]
    mw = g.load_world(tag)
    mb, M = g.to_build(mw, U, 0.0)
    if p[2:3] == ['x']:                      # spin so that world +x runs along bed +x
        v = M[:3, :3] @ np.array([1.0, 0.0, 0.0]); spin = -np.degrees(np.arctan2(v[1], v[0]))
    mb, M = g.to_build(mw, U, spin)
    c = (mb.bounds[0][:2] + mb.bounds[1][:2]) / 2
    T = np.eye(4); T[0, 3] = cx - c[0]; T[1, 3] = cy - c[1]
    mb.apply_transform(T); M = T @ M
    out = {'tag': tag, 'okey': okey, 'U': list(map(float, U)), 'spin': spin, 'M_world_to_bed': M.tolist(),
           'bounds_bed': mb.bounds.tolist(), 'vol_mm3': float(mb.volume)}
    json.dump(out, open('/home/claude/r2/data/orient_%s_%s.json' % (tag, okey), 'w'), indent=1)
    # which world axis runs along bed x / y
    R = M[:3, :3]
    print(tag, okey, 'spin', spin, 'bed bounds', np.round(mb.bounds, 2).tolist(), 'bed x <- world', np.round(R[0], 3).tolist(), 'bed y <- world', np.round(R[1], 3).tolist())
