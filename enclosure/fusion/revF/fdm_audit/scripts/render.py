"""Small orthographic renderer for the audit's meshes (numpy only): shaded pictures with faces coloured
by part or by thickness class, optional cut-away. World coordinates throughout."""
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import ndimage
from fdm_lib import *

_wm = {}
def world_mesh(name):
    if name not in _wm:
        m = load_model_mesh(name)
        _wm[name] = trimesh.Trimesh(vertices=to_world(m.vertices), faces=m.faces, process=False)
    return _wm[name]

def hexrgb(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float) / 255.0

def view_axes(d, up=(0, 0, 1)):
    """camera looks along -d (d points from the scene to the eye)."""
    d = np.asarray(d, float); d /= np.linalg.norm(d)
    up = np.asarray(up, float)
    r = np.cross(up, d); r /= np.linalg.norm(r)
    u = np.cross(d, r)
    return r, u, d

def render(items, d, centre, width, height, ppm=8.0, up=(0, 0, 1), clip=None, bg=1.0):
    """items: list of (mesh, face_rgb (n,3) or rgb). clip: list of (point, normal) -> keep where (c-p).n <= 0.
    Returns rgb image (H, W, 3) and the camera axes."""
    r, u, dd = view_axes(d, up)
    W = int(round(width * ppm)); H = int(round(height * ppm))
    zbuf = np.full(H * W, -np.inf); img = np.full((H * W, 3), bg); nbuf = np.zeros(H * W)
    c0 = np.asarray(centre, float)
    for mesh, col in items:
        tri = mesh.triangles; fn = mesh.face_normals; nf = len(tri)
        cols = np.tile(np.asarray(col, float), (nf, 1)) if np.ndim(col) == 1 else np.asarray(col, float)
        keep = np.ones(nf, bool)
        if clip:
            cen = tri.mean(1)
            for p, n in clip:
                keep &= ((cen - np.asarray(p, float)) @ np.asarray(n, float)) <= 0
        idx = np.where(keep)[0]
        if len(idx) == 0:
            continue
        area = mesh.area_faces[idx]
        dens = 3.0 * ppm * ppm
        cnt = np.maximum(1, np.random.poisson(area * dens)) if False else np.maximum(1, np.ceil(area * dens).astype(int))
        fi = np.repeat(idx, cnt)
        rng = np.random.default_rng(0)
        a = rng.random(len(fi)); b = rng.random(len(fi))
        sw = a + b > 1; a[sw] = 1 - a[sw]; b[sw] = 1 - b[sw]
        T = tri[fi]
        P = T[:, 0] + a[:, None] * (T[:, 1] - T[:, 0]) + b[:, None] * (T[:, 2] - T[:, 0])
        q = P - c0
        x = q @ r; y = q @ u; z = q @ dd
        px = np.floor((x + width / 2) * ppm).astype(int); py = np.floor((height / 2 - y) * ppm).astype(int)
        ok = (px >= 0) & (px < W) & (py >= 0) & (py < H)
        px, py, z, fi = px[ok], py[ok], z[ok], fi[ok]
        pid = py * W + px
        o = np.lexsort((z, pid))
        pid, z, fi = pid[o], z[o], fi[o]
        last = np.r_[pid[1:] != pid[:-1], True]
        pid, z, fi = pid[last], z[last], fi[last]
        better = z > zbuf[pid]
        pid, z, fi = pid[better], z[better], fi[better]
        nd = fn[fi] @ dd
        back = nd < 0
        shade = 0.35 + 0.65 * np.abs(nd)
        side = 0.5 + 0.5 * (fn[fi] @ r) * 0.25
        c = cols[fi] * (shade * (0.9 + 0.1 * side))[:, None]
        c[back] = np.array([0.25, 0.25, 0.28])          # cut faces seen from inside
        zbuf[pid] = z; img[pid] = c; nbuf[pid] = nd
    img = img.reshape(H, W, 3); zb = zbuf.reshape(H, W)
    # fill pinholes
    hole = ~np.isfinite(zb)
    filled = ndimage.maximum_filter(np.where(hole, -1e9, zb), size=3)
    fix = hole & (filled > -1e8)
    if fix.any():
        for k in range(3):
            ch = img[:, :, k]; ch2 = ndimage.minimum_filter(ch, size=3); ch[fix] = ch2[fix]
        zb = np.where(fix, filled, zb)
    # outlines from depth steps
    zz = np.where(np.isfinite(zb), zb, zb[np.isfinite(zb)].min() - 50 if np.isfinite(zb).any() else 0)
    gx = np.abs(ndimage.sobel(zz, axis=1)); gy = np.abs(ndimage.sobel(zz, axis=0))
    edge = (gx + gy) > (6.0 / ppm * 8)
    img[edge] *= 0.55
    return np.clip(img, 0, 1), (r, u, dd)

CLASS_COL = ['#d7191c', '#f17c33', '#fdc543', '#8cc269', '#3b9ab2', '#a8c6e0']   # <0.45 .. 2.0-2.6
_tm = {}
def thickness_mesh(name, edge=0.9):
    """World mesh cut into small faces, each with its ray thickness (centroid ray along the inward normal)."""
    if name in _tm:
        return _tm[name]
    fn = os.path.join(DATA, 'tmesh_%s.npz' % name)
    if os.path.exists(fn):
        z = np.load(fn)
        m = trimesh.Trimesh(vertices=z['v'], faces=z['f'], process=False); t = z['t']
    else:
        m0 = world_mesh(name)
        v, f = trimesh.remesh.subdivide_to_size(m0.vertices, m0.faces, max_edge=edge)
        m = trimesh.Trimesh(vertices=v, faces=f, process=False)
        cen = m.triangles_center; nrm = m.face_normals
        org = cen - 0.01 * nrm
        loc, ir, it = m0.ray.intersects_location(org, -nrm, multiple_hits=False)
        t = np.full(len(f), 99.0); t[ir] = np.linalg.norm(loc - org[ir], axis=1) + 0.01
        np.savez_compressed(fn, v=v.astype(np.float32), f=f.astype(np.int32), t=t.astype(np.float32))
    _tm[name] = (m, t)
    return _tm[name]

def thickness_colours(name, base='#c8ccd0', maxcls=4):
    m, t = thickness_mesh(name)
    TT = [x - 0.02 for x in T_PLANE]
    cls = np.digitize(t, TT)
    cols = np.tile(hexrgb(base), (len(m.faces), 1))
    for k in range(maxcls + 1):
        cols[cls == k] = hexrgb(CLASS_COL[k])
    return m, cols

def save(img, out, title='', notes=(), cam=None, centre=None, width=None, height=None, legend=True, maxcls=4):
    H, W = img.shape[:2]
    fig = plt.figure(figsize=(W / 100.0, H / 100.0 + 0.5), dpi=100)
    ax = fig.add_axes([0, 0, 1, H / (H + 50.0)])
    ax.imshow(img, extent=[-width / 2, width / 2, -height / 2, height / 2] if width else None)
    ax.axis('off')
    if cam is not None:
        r, u, dd = cam
        for (p, s) in notes:
            q = np.asarray(p, float) - np.asarray(centre, float)
            ax.annotate(s, (q @ r, q @ u), fontsize=9, color='#111', ha='center', va='center',
                        bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#555', lw=0.6, alpha=0.9))
    if legend:
        names = ['under 0.45', '0.45 to 0.85', '0.85 to 1.3', '1.3 to 1.7', '1.7 to 2.0', '2.0 to 2.6']
        for k in range(maxcls + 1):
            fig.text(0.01 + 0.16 * k, 0.975, '■ ' + names[k], color=CLASS_COL[k], fontsize=9, va='top')
    fig.text(0.01, 0.94 if legend else 0.975, title, fontsize=10, va='top')
    fig.savefig(out); plt.close(fig)
