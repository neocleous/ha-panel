# HA panel print audit, P9: printed-printed clearances in the assembled state (world frame) from the STL meshes.
#   For a pair (A, B): points sampled on A inside the boxes' overlap, B cropped to that region, closest point on B,
#   signed by B's face normal (negative = A's surface inside B). Spots closer than 0.6 mm are clustered on a 3 mm grid and
#   reported with the gap direction A->B. Usage: python3 pa_fits.py A B  (appends to data/fits.jsonl)
import sys, json, numpy as np, trimesh
sys.path.insert(0, '/home/claude/pa')
from pa_geom import load_world
from scipy.spatial import cKDTree


def run(a, b):
    A = load_world(a); B = load_world(b)
    lo = np.maximum(A.bounds[0], B.bounds[0]) - 1.0; hi = np.minimum(A.bounds[1], B.bounds[1]) + 1.0
    rec = {'pair': [a, b]}
    if np.any(lo > hi):
        rec['min'] = None; return rec
    fa = A.triangles
    ma = np.all(fa.max(1) >= lo, axis=1) & np.all(fa.min(1) <= hi, axis=1)
    Ac = A.submesh([np.nonzero(ma)[0]], append=True)
    fb = B.triangles
    mb = np.all(fb.max(1) >= lo - 1, axis=1) & np.all(fb.min(1) <= hi + 1, axis=1)
    if not ma.any() or not mb.any():
        rec['min'] = None; return rec
    Bc = B.submesh([np.nonzero(mb)[0]], append=True)
    n = int(min(120000, max(5000, Ac.area * 4)))
    pts, fi = trimesh.sample.sample_surface(Ac, n)
    tree = cKDTree(Bc.vertices)
    dv, _ = tree.query(pts, distance_upper_bound=4.0)
    pts = pts[dv < 4.0]
    if len(pts) == 0:
        rec['min'] = '>2'; return rec
    cp, dist, tri = trimesh.proximity.closest_point(Bc, pts)
    sgn = np.sign(np.einsum('ij,ij->i', pts - cp, Bc.face_normals[tri]))
    sd = np.where(sgn < 0, -dist, dist)
    rec['min'] = round(float(sd.min()), 3)
    close = sd < 0.6
    rec['n_close'] = int(close.sum())
    if close.any():
        P = pts[close]; D = sd[close]; V = cp[close] - P
        key = np.round(P / 3.0).astype(int)
        uk, inv = np.unique(key, axis=0, return_inverse=True)
        cl = []
        for k in range(len(uk)):
            m = inv.ravel() == k
            j = np.argmin(D[m]); v = V[m][j]; L = np.linalg.norm(v)
            cl.append([round(float(D[m].min()), 3), [round(float(x), 1) for x in P[m][j]], [round(float(x), 2) for x in (v / L if L > 0 else v)], int(m.sum())])
        cl.sort(key=lambda c: c[0])
        rec['spots'] = cl
    return rec


if __name__ == '__main__':
    r = run(sys.argv[1], sys.argv[2])
    with open('/home/claude/pa/data/fits.jsonl', 'a') as f:
        f.write(json.dumps(r) + '\n')
    s = r.get('spots', [])
    print(r['pair'], 'min', r.get('min'), 'n<0.6', r.get('n_close'), 'spots', len(s), s[:5], flush=True)
