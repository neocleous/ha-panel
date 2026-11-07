# HA panel print audit, P9 cross-check: are the negative spots from pa_fits.py real overlaps or sign errors?
#   pa_fits.py signs the distance with the normal of the closest triangle; next to a convex edge or corner that sign can
#   flip, which gives false "inside" points. Here each point that pa_fits would call inside (sd < -0.02) is re-tested
#   with the generalised winding number of B (solid-angle sum; robust for B meshes that are not watertight, e.g. the front)
#   and the pair is also run the other way round (points on B tested against A with A.contains, A watertight).
#   Usage: python3 pa_fits_verify.py A B   -> prints and appends to data/fits_verify.jsonl
import sys, json, numpy as np, trimesh
sys.path.insert(0, '/home/claude/pa')
from pa_geom import load_world
from scipy.spatial import cKDTree


def winding(mesh, P, chunk=200000):
    """Generalised winding number of points P (n,3) w.r.t. triangle soup mesh (Van Oosterom-Strackee solid angles)."""
    T = mesh.triangles
    w = np.zeros(len(P))
    for i, p in enumerate(P):
        acc = 0.0
        for s in range(0, len(T), chunk):
            a = T[s:s + chunk, 0] - p; b = T[s:s + chunk, 1] - p; c = T[s:s + chunk, 2] - p
            la = np.linalg.norm(a, axis=1); lb = np.linalg.norm(b, axis=1); lc = np.linalg.norm(c, axis=1)
            num = np.einsum('ij,ij->i', a, np.cross(b, c))
            den = la * lb * lc + np.einsum('ij,ij->i', a, b) * lc + np.einsum('ij,ij->i', b, c) * la + np.einsum('ij,ij->i', c, a) * lb
            acc += np.sum(2.0 * np.arctan2(num, den))
        w[i] = acc / (4 * np.pi)
    return w


def sample_near(A, B, n_max=120000):
    lo = np.maximum(A.bounds[0], B.bounds[0]) - 1.0; hi = np.minimum(A.bounds[1], B.bounds[1]) + 1.0
    fa = A.triangles
    ma = np.all(fa.max(1) >= lo, axis=1) & np.all(fa.min(1) <= hi, axis=1)
    Ac = A.submesh([np.nonzero(ma)[0]], append=True)
    fb = B.triangles
    mb = np.all(fb.max(1) >= lo - 1, axis=1) & np.all(fb.min(1) <= hi + 1, axis=1)
    Bc = B.submesh([np.nonzero(mb)[0]], append=True)
    n = int(min(n_max, max(5000, Ac.area * 4)))
    np.random.seed(7)
    pts, _ = trimesh.sample.sample_surface(Ac, n)
    dv, _ = cKDTree(Bc.vertices).query(pts, distance_upper_bound=4.0)
    pts = pts[dv < 4.0]
    sd = np.empty(len(pts))
    for s in range(0, len(pts), 5000):                     # batches keep trimesh's candidate lists small
        q = pts[s:s + 5000]
        cp, dist, tri = trimesh.proximity.closest_point(Bc, q)
        sgn = np.sign(np.einsum('ij,ij->i', q - cp, Bc.face_normals[tri]))
        sd[s:s + 5000] = np.where(sgn < 0, -dist, dist)
    return pts, sd, Bc


def run(a, b):
    A = load_world(a); B = load_world(b)
    rec = {'pair': [a, b], 'B_watertight': bool(B.is_watertight), 'A_watertight': bool(A.is_watertight)}
    pts, sd, Bc = sample_near(A, B)
    neg = sd < -0.02
    rec['n_samples'] = int(len(pts)); rec['n_neg_facesign'] = int(neg.sum())
    rec['min_facesign'] = round(float(sd.min()), 3)
    if neg.any():
        P = pts[neg]; D = sd[neg]
        if len(P) > 300:                                   # the 150 deepest and 150 others at random
            o = np.argsort(D); rest = np.random.RandomState(3).choice(o[150:], 150, replace=False)
            keep = np.concatenate([o[:150], rest]); P = P[keep]; D = D[keep]
            rec['n_winding_tested'] = 300
        w = winding(B, P)
        inside = w > 0.5
        rec['n_inside_winding'] = int(inside.sum())
        rec['min_depth_winding'] = round(float(D[inside].min()), 3) if inside.any() else None
        rec['neg_points'] = [[round(float(d), 3), [round(float(x), 2) for x in p], round(float(ww), 3)] for d, p, ww in
                             sorted(zip(D, P, w), key=lambda t: t[0])[:12]]
    # reverse: points on B near A, tested with A.contains (A watertight)
    ptsB, sdB, _ = sample_near(B, A)
    if A.is_watertight:
        insA = A.contains(ptsB)
        rec['rev_n_samples'] = int(len(ptsB)); rec['rev_n_inside_contains'] = int(insA.sum())
        rec['rev_min_dist_inside'] = round(float(-np.abs(sdB[insA]).max()), 3) if insA.any() else None
    return rec


if __name__ == '__main__':
    r = run(sys.argv[1], sys.argv[2])
    with open('/home/claude/pa/data/fits_verify.jsonl', 'a') as f:
        f.write(json.dumps(r) + '\n')
    print(json.dumps(r), flush=True)
