# recheck2: the lug pocket's floor as printed (box print, rear face down) against the model's floor plane, and the box's front
#   face and the lug's front face as sliced. World y = bed z - 52.0 in these prints.
import sys, json, math, numpy as np
sys.path.insert(0, '/home/claude/r2/offline')
from r2_gq import G
from r2_faces import load
out = {}
for tag, job in (('spkbox_L', 'A_spkbox_L'), ('spkbox_R', 'A_spkbox_R')):
    g = G(job, tag); F = load(tag)
    fl = [f for f in F if f['k'] == 'plane' and f['n'] and abs(f['n'][1] - 0.9848) < 1e-3 and abs(abs(f['n'][0]) - 0.1736) < 1e-3 and f['a'] > 5][0]
    pc = [f for f in F if f['k'] == 'cylinder' and abs(f['r'] - 2.6) < 1e-3 and f['a'] > 3][0]
    u = np.array(pc['ax']); u = u if u[1] > 0 else -u; o = np.array(pc['o'])
    n = np.array(fl['n']); p = np.array(fl['p'])
    # axis point on the floor plane
    t = n @ (p - o) / (n @ u); a0 = o + t * u
    # ring r 1.8 .. 2.3 in the floor plane: sample points
    e1 = np.array([0.0, 0.0, 1.0]); e2 = np.cross(u, e1); e2 /= np.linalg.norm(e2)
    pts = []
    for r in np.linspace(1.80, 2.30, 11):
        for th in np.linspace(0, 2 * math.pi, 361)[:-1]:
            pts.append(a0 + r * (math.cos(th) * e1 + math.sin(th) * e2))
    pts = np.array(pts)
    B = g.to_bed(pts)
    # layers near the floor
    mask = g.fmask()
    zs = sorted(set(round(float(z), 3) for z in g.S[:, 4] if 49.2 < z < 51.6))
    px = 0.01
    x0, x1 = B[:, 0].min() - 0.5, B[:, 0].max() + 0.5; y0, y1 = B[:, 1].min() - 0.5, B[:, 1].max() + 0.5
    W = int((x1 - x0) / px) + 1; H = int((y1 - y0) / px) + 1
    top = np.full(len(B), -1.0)
    for z in zs:
        R = g.raster(mask, z, x0, y0, W, H, px)
        ii = ((B[:, 0] - x0) / px).astype(int); jj = ((B[:, 1] - y0) / px).astype(int)
        cov = R[jj, ii]
        top[cov] = np.maximum(top[cov], z)
    true_y = pts[:, 1]
    printed_y = top - 52.0
    proud = printed_y - true_y            # + = toward the plate
    out[tag] = {'axis_on_floor': np.round(a0, 3).tolist(), 'u': np.round(u, 5).tolist(), 'floor_true_y_range': [round(float(true_y.min()), 3), round(float(true_y.max()), 3)],
                'layers': zs, 'covered_share': round(float((top > 0).mean()), 3),
                'proud_max_y': round(float(proud[top > 0].max()), 3), 'proud_mean_y': round(float(proud[top > 0].mean()), 3),
                'proud_min_y': round(float(proud[top > 0].min()), 3),
                'proud_max_along_u': round(float(proud[top > 0].max() * u[1]), 3)}
    # the box's front face (driver face, model y -3.70) and the lug's front face (model y -0.78): highest layer top in a patch
    def top_at(world_xz_box):
        xa, xb, za, zb = world_xz_box
        Wp = np.array([[x, -3.0, z] for x in np.linspace(xa, xb, 9) for z in np.linspace(za, zb, 9)])
        Bp = g.to_bed(Wp)
        best = []
        for z in sorted(set(round(float(v), 3) for v in g.S[:, 4] if 46.0 < v < 51.6)):
            m = mask & (np.abs(g.S[:, 4] - z) < 1e-3)
            s = g.S[m]
            if not len(s):
                continue
            # any segment midpoint inside the patch's bed box
            mx = (s[:, 0] + s[:, 2]) / 2; my = (s[:, 1] + s[:, 3]) / 2
            inb = (mx > Bp[:, 0].min()) & (mx < Bp[:, 0].max()) & (my > Bp[:, 1].min()) & (my < Bp[:, 1].max())
            if inb.any():
                best.append(z)
        return max(best) if best else None
    sx = 1 if tag == 'spkbox_L' else -1
    fz = top_at((sx * 70, sx * 85, 20, 35) if sx > 0 else (sx * 85, sx * 70, 20, 35))
    out[tag]['front_face_top_z'] = fz; out[tag]['front_face_y_as_sliced'] = None if fz is None else round(fz - 52.0, 3)
    lz = top_at((sx * 60.5, sx * 62.5, 82.8, 83.8) if sx > 0 else (sx * 62.5, sx * 60.5, 82.8, 83.8))
    out[tag]['lug_face_top_z'] = lz; out[tag]['lug_face_y_as_sliced'] = None if lz is None else round(lz - 52.0, 3)
print(json.dumps(out, indent=1))
json.dump(out, open('/home/claude/r2/data/lug_floor.json', 'w'), indent=1)
