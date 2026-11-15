# recheck2 block 2: the shell's surfaces in a world box that face the viewer (normal . SN > cmin), as sliced (A_shell_v2):
#   share printed over support, the printed position along each sample's normal against the model, the first layer's features.
import sys, json, math, numpy as np, trimesh
from scipy.spatial import cKDTree
sys.path.insert(0, '/home/claude/r2/offline')
from r2_gq import G
C12, S12 = math.cos(math.radians(12)), math.sin(math.radians(12)); SN = np.array([0, C12, S12])
def pts_of(s, step=0.2):
    L = np.hypot(s[:, 2] - s[:, 0], s[:, 3] - s[:, 1]); nn = np.maximum(1, (L / step).astype(int))
    return np.concatenate([np.linspace(a[0:2], a[2:4], k) for a, k in zip(s, nn)]), nn
def region(g, mesh, box, cmin=0.3, dens=4.0, px=0.05, seed=2):
    TN = mesh.face_normals; TC = mesh.triangles_center
    x0, x1, y0, y1, z0, z1 = box
    sel = (TN @ SN > cmin) & (TC[:, 0] > x0) & (TC[:, 0] < x1) & (TC[:, 1] > y0) & (TC[:, 1] < y1) & (TC[:, 2] > z0) & (TC[:, 2] < z1)
    tri = mesh.triangles[sel]; nrm = TN[sel]
    ar = trimesh.triangles.area(tri); A = float(ar.sum())
    if A < 1e-6: return None
    rng = np.random.default_rng(seed); k = int(min(6000, max(100, A * dens)))
    idx = rng.choice(len(tri), size=k, p=ar / A); r1 = np.sqrt(rng.random(k)); r2 = rng.random(k); T = tri[idx]
    W = (1 - r1)[:, None] * T[:, 0] + (r1 * (1 - r2))[:, None] * T[:, 1] + (r1 * r2)[:, None] * T[:, 2]
    N = nrm[idx]; B = g.to_bed(W); Ub = g.M[2, :3]                  # bed z axis in world
    nz = N @ Ub                                                        # < 0: faces down in the print
    down = nz < -0.2
    part = g.fmask(exclude=('Support', 'Brim', 'Skirt', 'tower')); supm = g.fmask('Support')
    Z = np.array(sorted(set(np.round(g.S[:, 4], 3))))
    bx0, bx1 = B[:, 0].min() - 1, B[:, 0].max() + 1; by0, by1 = B[:, 1].min() - 1, B[:, 1].max() + 1
    Wd = int((bx1 - bx0) / px) + 1; Hd = int((by1 - by0) / px) + 1
    ii = np.clip(((B[:, 0] - bx0) / px).astype(int), 0, Wd - 1); jj = np.clip(((B[:, 1] - by0) / px).astype(int), 0, Hd - 1)
    first = np.full(len(B), np.nan)
    for z in Z[(Z > B[:, 2].min() - 0.8) & (Z < B[:, 2].max() + 1.2)]:
        R = g.raster(part, z, bx0, by0, Wd, Hd, px); c = R[jj, ii] & np.isnan(first) & down & (z > B[:, 2] - 0.6)
        first[c] = z
    got = ~np.isnan(first)
    prot = (B[:, 2] - (first - 0.2)) * np.abs(nz)
    supd = np.zeros(len(B), bool); feats = {}
    for z in sorted(set(first[got])):
        selz = got & (np.abs(first - z) < 1e-3)
        for dzl in (0.2, 0.4, 0.6):
            m = supm & (np.abs(g.S[:, 4] - round(z - dzl, 3)) < 1e-3); s = g.S[m]
            s = s[(np.maximum(s[:, 0], s[:, 2]) > bx0) & (np.minimum(s[:, 0], s[:, 2]) < bx1) & (np.maximum(s[:, 1], s[:, 3]) > by0) & (np.minimum(s[:, 1], s[:, 3]) < by1)]
            if not len(s): continue
            p, _ = pts_of(s); d_, _ = cKDTree(p).query(B[selz, :2], distance_upper_bound=0.5)
            supd[np.nonzero(selz)[0][np.isfinite(d_)]] = True
        m = part & (np.abs(g.S[:, 4] - z) < 1e-3); s = g.S[m]; fi = g.F[m]
        inb = (np.maximum(s[:, 0], s[:, 2]) > bx0) & (np.minimum(s[:, 0], s[:, 2]) < bx1) & (np.maximum(s[:, 1], s[:, 3]) > by0) & (np.minimum(s[:, 1], s[:, 3]) < by1)
        s = s[inb]; fi = fi[inb]
        if len(s):
            p, nn = pts_of(s); lab = np.repeat(fi, nn); _, q = cKDTree(p).query(B[selz, :2])
            for l in lab[q]: feats[g.names[l]] = feats.get(g.names[l], 0) + 1
    tot = sum(feats.values()) or 1
    pr = prot[got]
    return dict(area_view=round(A, 1), share_down=round(float(down.mean()), 2), area_down=round(A * float(down.mean()), 1), covered=round(float(got[down].mean()), 2) if down.any() else None,
                on_support=round(float(supd[got].mean()), 2) if got.any() else None,
                prot_pct=[round(float(np.percentile(pr, q)), 3) for q in (2, 25, 50, 75, 98)] if len(pr) else None,
                bedz=[round(float(B[down, 2].min()), 1), round(float(B[down, 2].max()), 1)] if down.any() else None,
                feat={k: round(v / tot, 2) for k, v in sorted(feats.items(), key=lambda kv: -kv[1])[:4]})
if __name__ == '__main__':
    job, tag = sys.argv[1], sys.argv[2]; boxes = json.loads(sys.argv[3])
    g = G(job, tag); mesh = trimesh.load('/mnt/user-data/uploads/print_audit_recheck2/exports/%s.stl' % tag, force='mesh')
    for name, box in boxes.items():
        print(name, json.dumps(region(g, mesh, box)))
