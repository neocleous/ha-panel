# HA panel print audit, P9 (second pass): printed-printed and printed-component clearances as FACE PAIRS.
#   pa_fits.py listed every sample point within 0.6 mm of the other part, signed by the closest triangle's normal; that
#   mixes real face-to-face gaps with points near edges (where the sign can flip and the "gap" runs along a face, not
#   across it). Here a sample point on A counts only if
#     - its closest point on B lies on a face that faces it (normal of A's face . normal of B's face < -0.8), and
#     - the sign is confirmed: points the face normal calls "inside" are re-tested with B.contains (watertight B) or the
#       generalised winding number (B not watertight, e.g. the front shell); a point that is not inside counts as outside.
#   Kept points (gap < 0.6) are grouped into regions (connected on a 2 mm grid), contact (< 0.05) and gap regions apart;
#   each region gets the number of points, an area estimate, gap min / median / max, its box in world mm (x_rel, y, z) and
#   the mean outward normal of A there (the gap direction A -> B); plus the area per gap band for the whole pair.
#   Usage: python3 pa_fits2.py A B   (A, B are tags of meshes in exports/ or exports/comp/; appends to data/fits2.jsonl)
import sys, json, os, numpy as np, trimesh
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
sys.path.insert(0, '/home/claude/pa')
UPL = '/mnt/user-data/uploads/print_audit/exports/'


def load(tag):
    for p in (UPL + tag + '.stl', UPL + 'comp/' + tag + '.stl', '/home/claude/pa/work/comp/' + tag + '.stl'):
        if os.path.exists(p):
            return trimesh.load(p, force='mesh', process=True)
    raise FileNotFoundError(tag)


def winding(mesh, P, chunk=200000):
    T = mesh.triangles; w = np.zeros(len(P))
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


def run(a, b, limit=0.6):
    A = load(a); B = load(b)
    rec = {'pair': [a, b]}
    lo = np.maximum(A.bounds[0], B.bounds[0]) - 1.0; hi = np.minimum(A.bounds[1], B.bounds[1]) + 1.0
    if np.any(lo > hi):
        rec['result'] = 'boxes apart > 1 mm'; return rec
    fa = A.triangles
    ma = np.all(fa.max(1) >= lo, axis=1) & np.all(fa.min(1) <= hi, axis=1)
    fb = B.triangles
    mb = np.all(fb.max(1) >= lo - 1, axis=1) & np.all(fb.min(1) <= hi + 1, axis=1)
    if not ma.any() or not mb.any():
        rec['result'] = 'no faces in the shared box'; return rec
    Ac = A.submesh([np.nonzero(ma)[0]], append=True); Bc = B.submesh([np.nonzero(mb)[0]], append=True)
    n = int(min(150000, max(5000, Ac.area * 4)))
    np.random.seed(11)
    pts, fi = trimesh.sample.sample_surface(Ac, n)
    area_per_pt = Ac.area / n
    nA = Ac.face_normals[fi]
    # prefilter on B's vertices AND a dense surface sample of B (large flat triangles have vertices far from their middle)
    nb = int(min(800000, max(20000, Bc.area * 4)))
    sb, _ = trimesh.sample.sample_surface(Bc, nb)
    dv, _ = cKDTree(np.vstack([Bc.vertices, sb])).query(pts, distance_upper_bound=limit + 1.0)
    keep = dv < limit + 1.0
    pts = pts[keep]; nA = nA[keep]
    if len(pts) == 0:
        rec['result'] = 'no point within %.1f mm' % (limit + 1.0); return rec
    cp = np.empty_like(pts); dist = np.empty(len(pts)); nB = np.empty_like(pts)
    for s in range(0, len(pts), 5000):
        c_, d_, t_ = trimesh.proximity.closest_point(Bc, pts[s:s + 5000])
        cp[s:s + 5000] = c_; dist[s:s + 5000] = d_; nB[s:s + 5000] = Bc.face_normals[t_]
    sgn = np.einsum('ij,ij->i', pts - cp, nB)
    neg = (sgn < 0) & (dist > 0.02)
    inside = np.zeros(len(pts), bool)
    if neg.any():
        idx = np.nonzero(neg)[0]
        if B.is_watertight:
            inside[idx] = B.contains(pts[idx])
        else:
            if len(idx) > 400:
                idx = idx[np.argsort(-dist[idx])[:400]]          # the deepest 400 (the rest assumed like them: reported)
                rec['winding_capped'] = True
            inside[idx] = winding(B, pts[idx]) > 0.5
    rec['n_face_sign_inside'] = int(neg.sum()); rec['n_confirmed_inside'] = int(inside.sum())
    if inside.any():
        rec['max_overlap'] = round(float(dist[inside].max()), 3)
        P = pts[inside]
        rec['overlap_box'] = [round(float(v), 1) for v in np.r_[P.min(0), P.max(0)]]
    gap = np.where(inside, -dist, dist)
    opp = np.einsum('ij,ij->i', nA, nB) < -0.8
    sel = opp & (gap < limit)
    rec['n_samples'] = int(len(pts)); rec['area_per_pt'] = round(float(area_per_pt), 4)
    rec['n_face_pairs'] = int(sel.sum())
    if not sel.any():
        rec['result'] = 'no facing faces closer than %.1f' % limit
        rec['min_gap_any'] = round(float(gap.min()), 3)
        return rec
    P = pts[sel]; G = gap[sel]; D = nA[sel]
    np.savez_compressed('/home/claude/pa/work/F2_%s_%s.npz' % (a, b), P=P, G=G, D=D, area_per_pt=area_per_pt)
    edges = [0.0, 0.05, 0.15, 0.25, 0.35, 0.45, 0.5, limit]
    rec['bands_mm2'] = {'%.2f-%.2f' % (edges[i], edges[i + 1]): round(float(((G >= edges[i]) & (G < edges[i + 1])).sum() * area_per_pt), 1)
                        for i in range(len(edges) - 1)}

    def regions(mask):
        if not mask.any():
            return []
        Pm = P[mask]; Gm = G[mask]; Dm = D[mask]
        org = Pm.min(0) - 2.0
        ijk = np.floor((Pm - org) / 2.0).astype(int)
        grid = np.zeros(ijk.max(0) + 2, bool); grid[tuple(ijk.T)] = True
        lab, nl = ndi.label(grid, structure=np.ones((3, 3, 3)))
        rl = lab[tuple(ijk.T)]
        out = []
        for r in range(1, nl + 1):
            m = rl == r
            if m.sum() < 3:
                continue
            g = Gm[m]; q = Pm[m]; dn = Dm[m].mean(0); dn = dn / (np.linalg.norm(dn) or 1)
            out.append({'n': int(m.sum()), 'area_mm2': round(float(m.sum() * area_per_pt), 1),
                        'gap_min': round(float(g.min()), 3), 'gap_med': round(float(np.median(g)), 3),
                        'gap_max': round(float(g.max()), 3),
                        'box': [round(float(v), 1) for v in np.r_[q.min(0), q.max(0)]],
                        'dir_A_out': [round(float(v), 2) for v in dn]})
        out.sort(key=lambda r: (r['gap_med'], -r['n']))
        return out
    rec['contact_regions'] = regions(G < 0.05)
    regs = regions(G >= 0.05)
    rec['regions'] = regs
    rec['result'] = '%d regions' % len(regs)
    return rec


if __name__ == '__main__':
    r = run(sys.argv[1], sys.argv[2])
    with open('/home/claude/pa/data/fits2.jsonl', 'a') as f:
        f.write(json.dumps(r) + '\n')
    s = {k: v for k, v in r.items() if k not in ('regions', 'contact_regions')}
    print(json.dumps(s), flush=True)
    for g in r.get('regions', [])[:40]:
        print('   gap', g, flush=True)
    for g in r.get('contact_regions', [])[:20]:
        print('   contact', g, flush=True)
