# recheck2 block 2: faces that look toward the viewer, as sliced. For each B-rep face (world plane, from the face dump), sample the
#   real face (triangles of the world STL lying in the face's plane and box), then in the G-code (part features only):
#   - 'prot': where the printed surface is, along the face's outward normal, against the model (+ = proud of the model, toward the viewer);
#   - 'sup': share of samples with support or support interface within 0.5 mm (bed xy) in the three layers under the first printed layer;
#   - 'feat': which extrusion features make the first printed layer there.
#   Usage: python3 r2_vis.py <job> <tag> <face ids comma-separated> [stl]
import sys, json, math, numpy as np, trimesh
from scipy.spatial import cKDTree
sys.path.insert(0, '/home/claude/r2/offline')
from r2_gq import G
from r2_faces import load

def run(job, tag, ids, stl, px=0.05, seed=1):
    g = G(job, tag); F = {f['i']: f for f in load(tag)}
    mesh = trimesh.load(stl, force='mesh')
    TN = mesh.face_normals; TC = mesh.triangles_center
    part = g.fmask(exclude=('Support', 'Brim', 'Skirt', 'tower'))
    supm = g.fmask('Support')
    Z = np.array(sorted(set(np.round(g.S[:, 4], 3))))
    U = (g.M[:3, :3].T @ np.array([0, 0, 1.0]))                    # bed 'up' in world
    out = {}
    rng = np.random.default_rng(seed)
    for i in ids:
        f = F[i]; n = np.array(f['n'], float); n /= np.linalg.norm(n); p = np.array(f['p'], float); bb = f['bb']
        sel = (TN @ n > 0.9995) & (np.abs((TC - p) @ n) < 0.02)
        sel &= (TC[:, 0] > bb[0] - 0.05) & (TC[:, 0] < bb[1] + 0.05) & (TC[:, 1] > bb[2] - 0.05) & (TC[:, 1] < bb[3] + 0.05) & (TC[:, 2] > bb[4] - 0.05) & (TC[:, 2] < bb[5] + 0.05)
        tri = mesh.triangles[sel]
        if not len(tri):
            out[i] = None; continue
        ar = trimesh.triangles.area(tri); A = float(ar.sum())
        k = int(min(4000, max(60, A / 0.25)))
        idx = rng.choice(len(tri), size=k, p=ar / A)
        r1 = np.sqrt(rng.random(k)); r2 = rng.random(k)
        T = tri[idx]
        W = (1 - r1)[:, None] * T[:, 0] + (r1 * (1 - r2))[:, None] * T[:, 1] + (r1 * r2)[:, None] * T[:, 2]
        B = g.to_bed(W)
        cosn = float(abs(n @ U))                                    # bed-z error -> error along the face normal
        facing_down = (n @ U) < 0
        x0, x1 = B[:, 0].min() - 1.0, B[:, 0].max() + 1.0; y0, y1 = B[:, 1].min() - 1.0, B[:, 1].max() + 1.0
        Wd = int((x1 - x0) / px) + 1; Hd = int((y1 - y0) / px) + 1
        ii = np.clip(((B[:, 0] - x0) / px).astype(int), 0, Wd - 1); jj = np.clip(((B[:, 1] - y0) / px).astype(int), 0, Hd - 1)
        zr = Z[(Z > B[:, 2].min() - 1.0) & (Z < B[:, 2].max() + 1.2)]
        first = np.full(len(B), np.nan)
        order = zr if facing_down else zr[::-1]
        for z in order:
            R = g.raster(part, z, x0, y0, Wd, Hd, px); c = R[jj, ii] & np.isnan(first)
            # only accept layers on the solid side of the face
            ok = (z > B[:, 2] - 0.6) if facing_down else (z - 0.2 < B[:, 2] + 0.6)
            first[c & ok] = z
        got = ~np.isnan(first)
        if facing_down:
            dz = B[:, 2] - (first - 0.2)            # + : printed below the model face (toward the bed = toward the face's outside)
        else:
            dz = first - B[:, 2]
        prot = dz * cosn
        # support under the first printed layer
        supfrac = np.nan; feats = {}
        if facing_down and got.any():
            supd = np.zeros(len(B), bool)
            for z in sorted(set(first[got])):
                for dzl in (0.2, 0.4, 0.6):
                    zl = round(z - dzl, 3)
                    m = supm & (np.abs(g.S[:, 4] - zl) < 1e-3)
                    s = g.S[m]
                    if not len(s): continue
                    s = s[(np.maximum(s[:, 0], s[:, 2]) > x0) & (np.minimum(s[:, 0], s[:, 2]) < x1) & (np.maximum(s[:, 1], s[:, 3]) > y0) & (np.minimum(s[:, 1], s[:, 3]) < y1)]
                    if not len(s): continue
                    L = np.hypot(s[:, 2] - s[:, 0], s[:, 3] - s[:, 1]); nn = np.maximum(1, (L / 0.2).astype(int))
                    pts = np.concatenate([np.linspace(a[0:2], a[2:4], k_) for a, k_ in zip(s, nn)])
                    t = cKDTree(pts); sel_ = got & (np.abs(first - z) < 1e-3)
                    d_, _ = t.query(B[sel_, :2], distance_upper_bound=0.5)
                    supd[np.nonzero(sel_)[0][np.isfinite(d_)]] = True
            supfrac = float(supd[got].mean())
            # features of the first printed layer at the samples
            for z in sorted(set(first[got])):
                m = part & (np.abs(g.S[:, 4] - z) < 1e-3)
                s = g.S[m]; fi = g.F[m]
                s_in = (np.maximum(s[:, 0], s[:, 2]) > x0) & (np.minimum(s[:, 0], s[:, 2]) < x1) & (np.maximum(s[:, 1], s[:, 3]) > y0) & (np.minimum(s[:, 1], s[:, 3]) < y1)
                s = s[s_in]; fi = fi[s_in]
                if not len(s): continue
                L = np.hypot(s[:, 2] - s[:, 0], s[:, 3] - s[:, 1]); nn = np.maximum(1, (L / 0.2).astype(int))
                pts = np.concatenate([np.linspace(a[0:2], a[2:4], k_) for a, k_ in zip(s, nn)]); lab = np.repeat(fi, nn)
                t = cKDTree(pts); sel_ = got & (np.abs(first - z) < 1e-3)
                _, q = t.query(B[sel_, :2])
                for l in lab[q]: feats[g.names[l]] = feats.get(g.names[l], 0) + 1
        tot = sum(feats.values()) or 1
        out[i] = dict(area=round(A, 1), n=int(len(B)), covered=round(float(got.mean()), 2),
                      prot_mean=round(float(np.nanmean(prot)), 3) if got.any() else None, prot_min=round(float(np.nanmin(prot)), 3) if got.any() else None,
                      prot_max=round(float(np.nanmax(prot)), 3) if got.any() else None, bedz=[round(float(B[:, 2].min()), 2), round(float(B[:, 2].max()), 2)],
                      down=bool(facing_down), sup=None if np.isnan(supfrac) else round(supfrac, 2), feat={k: round(v / tot, 2) for k, v in sorted(feats.items(), key=lambda kv: -kv[1])[:4]})
    return out

if __name__ == '__main__':
    job, tag, ids = sys.argv[1], sys.argv[2], [int(v) for v in sys.argv[3].split(',')]
    stl = sys.argv[4] if len(sys.argv) > 4 else '/mnt/user-data/uploads/print_audit_recheck2/exports/%s.stl' % tag
    res = run(job, tag, ids, stl)
    for k, v in res.items(): print(k, json.dumps(v))
