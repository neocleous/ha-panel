# recheck: quick shaded views of a world mesh by splatting dense surface samples into a z-buffer (no GPU, no ray library).
# view = (azimuth_deg, elevation_deg); crop = world box (x0,x1,y0,y1,z0,z1) or None; marks = list of (x,y,z,label) world points.
import sys, json, math, numpy as np, trimesh
sys.path.insert(0, '/home/claude/pa')
from pa_geom import load_world
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

def view_basis(az, el):
    a, e = math.radians(az), math.radians(el)
    d = np.array([math.cos(e) * math.sin(a), -math.cos(e) * math.cos(a), math.sin(e)])   # from target toward the eye
    up = np.array([0, 0, 1.0]); r = np.cross(up, d); r /= np.linalg.norm(r); u = np.cross(d, r)
    return r, u, d

def render(meshes, az, el, out, px=0.15, crop=None, marks=(), title='', size=7, colors=None, sample=6.0):
    r, u, d = view_basis(az, el)
    pts_all, val_all, col_all = [], [], []
    for mi, m in enumerate(meshes):
        if crop is not None:
            c = m.triangles_center
            k = (c[:, 0] >= crop[0]) & (c[:, 0] <= crop[1]) & (c[:, 1] >= crop[2]) & (c[:, 1] <= crop[3]) & (c[:, 2] >= crop[4]) & (c[:, 2] <= crop[5])
            m = m.submesh([np.nonzero(k)[0]], append=True) if k.any() else None
            if m is None: continue
        n = min(max(int(m.area * 2.5 / (px * px)), 20000), 6000000)
        p, fi = trimesh.sample.sample_surface(m, n)
        nn = m.face_normals[fi]
        lam = np.clip(nn @ (0.35 * r + 0.55 * u + 0.75 * d) / np.linalg.norm(0.35 * r + 0.55 * u + 0.75 * d), 0, 1)
        pts_all.append(p); val_all.append(0.25 + 0.75 * lam); col_all.append(np.full(len(p), mi))
    P = np.vstack(pts_all); V = np.concatenate(val_all); Ci = np.concatenate(col_all)
    X = P @ r; Y = P @ u; Z = P @ d
    x0, y0 = X.min(), Y.min(); W = int((X.max() - x0) / px) + 2; Hh = int((Y.max() - y0) / px) + 2
    i = ((X - x0) / px).astype(int); j = ((Y - y0) / px).astype(int)
    order = np.argsort(Z)                      # far first, near last wins
    img = np.ones((Hh, W)); idx = np.full((Hh, W), -1)
    img[j[order], i[order]] = V[order]; idx[j[order], i[order]] = Ci[order]
    cols = colors or [(0.85, 0.85, 0.85), (0.95, 0.75, 0.3), (0.4, 0.7, 1.0), (0.6, 0.9, 0.5), (1.0, 0.5, 0.5)]
    from scipy import ndimage as ndi
    hole = idx < 0
    if hole.any():                                      # fill single-pixel gaps from the nearest sample
        dd, (jj, ii) = ndi.distance_transform_edt(hole, return_indices=True)
        fillk = hole & (dd <= 1.5)
        img[fillk] = img[jj[fillk], ii[fillk]]; idx[fillk] = idx[jj[fillk], ii[fillk]]
    rgb = np.ones((Hh, W, 3))
    for mi in range(len(meshes)):
        k = idx == mi
        rgb[k] = np.array(cols[mi % len(cols)])[None, :] * img[k][:, None]
    fig, ax = plt.subplots(figsize=(size, size * Hh / W + 0.3), dpi=110)
    ax.imshow(rgb, origin='lower', extent=(x0, x0 + W * px, y0, y0 + Hh * px), interpolation='nearest')
    for (x, y, z, lab) in marks:
        q = np.array([x, y, z]); ax.plot(q @ r, q @ u, 'r+', ms=8); ax.text(q @ r, q @ u, ' ' + lab, color='r', fontsize=6)
    ax.set_title(title, fontsize=8); ax.set_xticks([]); ax.set_yticks([]); fig.tight_layout(); fig.savefig(out); plt.close(fig)

if __name__ == '__main__':
    tags = sys.argv[1].split(','); az, el = float(sys.argv[2]), float(sys.argv[3]); out = sys.argv[4]
    crop = [float(v) for v in sys.argv[5].split(',')] if len(sys.argv) > 5 and sys.argv[5] != '-' else None
    px = float(sys.argv[6]) if len(sys.argv) > 6 else 0.15
    render([load_world(t) for t in tags], az, el, out, px=px, crop=crop, title=' + '.join(tags) + ' az %g el %g' % (az, el))
    print(out)
