# HA panel print audit (2026-11-07): offline geometry library for the cloud workspace.
#   Meshes: print_audit/exports/<tag>.stl from pa1_export.py (world mm, x_rel, z up, floor z 0, +y toward the viewer).
#   Build frame: the mesh rotated so the print's build direction U (world vector) points to +z, then moved so z_min = 0.
#   Layers: first layer 0.20, then LAYER_H; each layer is sampled on its mid-plane + 2e-4 mm (PrusaSlicer 2.7.2 convention,
#   checked on test cubes: a top face exactly on a mid-plane is not printed in that layer).
#   Rasters: even-odd scanline fill of the plane-section segments at pixel size px (pixel centres), so no loop assembly.
import numpy as np, trimesh, json, math, os
from scipy import ndimage as ndi

UPL = '/mnt/user-data/uploads/print_audit/exports/'
C12, S12 = math.cos(math.radians(12.0)), math.sin(math.radians(12.0))
LAYER_H = 0.20
FIRST_H = 0.20
EPS = 2e-4

# Build directions (world vectors that point UP in the build frame) and the planned / alternative orientations.
ORIENT = {
    'front':        {'plan': (0, 0, 1)},
    'cap':          {'plan': (0, 0, -1)},                      # top face down (decided)
    'slab':         {'plan': (0, -C12, -S12), 'side+x': (1, 0, 0), 'side-x': (-1, 0, 0), 'back_down': (0, C12, S12)},   # glass side down / on its side
    'resp_carrier': {'plan': (0, -C12, -S12)},                 # plate down (B6o "slab front down")
    'door':         {'plan': (0, 0, 1)},                       # bottom edge down
    'grommet':      {'plan': (0, 1, 0), 'side+x': (1, 0, 0), 'side+z': (0, 0, 1), 'side-z': (0, 0, -1), 'flange_up': (0, -1, 0)},
    'cradle':       {'plan': (0, 1, 0)},                       # rear face down
    'bracket_L':    {'plan': (0, 0, 1), 'flat+y': (0, 1, 0), 'flat-y': (0, -1, 0)},
    'bracket_R':    {'plan': (0, 0, 1), 'flat+y': (0, 1, 0), 'flat-y': (0, -1, 0)},
    'bme_hood':     {'plan': (-0.751, -0.643, 0.150)},          # back plate down (its interior face on the bed; mesh normal cluster 460 mm2)
    'spkbox_L':     {'plan': (0, 1, 0)},                       # rear face down
    'spkbox_R':     {'plan': (0, 1, 0)},
    'clip_L':       {'plan': (0, 0, 1)},                       # as fitted
    'clip_R':       {'plan': (0, 0, 1)},
}


def load_world(tag):
    return trimesh.load(UPL + tag + '.stl', force='mesh', process=True)


def rot_to_z(U):
    U = np.asarray(U, float); U = U / np.linalg.norm(U)
    if np.allclose(U, (0, 0, 1)):
        return np.eye(4)
    if np.allclose(U, (0, 0, -1)):
        R = np.eye(4); R[1, 1] = -1; R[2, 2] = -1            # 180 deg about x: (x, y, z) -> (x, -y, -z)
        return R
    return trimesh.geometry.align_vectors(U, (0, 0, 1))


def to_build(mw, U, spin_deg=0.0):
    """Returns (mesh in the build frame, M world->build 4x4)."""
    R = rot_to_z(U)
    if spin_deg:
        R = trimesh.transformations.rotation_matrix(math.radians(spin_deg), (0, 0, 1)) @ R
    mb = mw.copy(); mb.apply_transform(R)
    t = np.eye(4); t[:3, 3] = (0.0, 0.0, -mb.bounds[0][2])
    mb.apply_transform(t)
    return mb, t @ R


def b2w(M, pts):
    """build-frame points (n,3) -> world (x_rel, y, z)."""
    Mi = np.linalg.inv(M); p = np.c_[np.asarray(pts, float), np.ones(len(pts))]
    return (p @ Mi.T)[:, :3]


def layer_mids(height):
    zs = [FIRST_H / 2]
    while True:
        z = FIRST_H + LAYER_H * (len(zs) - 1) + LAYER_H / 2
        if z >= height:
            break
        zs.append(z)
    return np.array(zs)


def layer_top(k):
    return FIRST_H + LAYER_H * k


class Slicer:
    def __init__(self, mb):
        self.V = np.asarray(mb.vertices, float)
        self.E = np.asarray(mb.edges_unique)
        self.FE = np.asarray(mb.faces_unique_edges)
        vz = self.V[:, 2]
        e0 = vz[self.E[:, 0]]; e1 = vz[self.E[:, 1]]
        self.emin = np.minimum(e0, e1); self.emax = np.maximum(e0, e1)
        fz = vz[np.asarray(mb.faces)]
        self.fmin = fz.min(1); self.fmax = fz.max(1)
        self.order = np.argsort(self.fmin); self.fmin_s = self.fmin[self.order]

    def segments(self, z):
        """(n,2,2) XY segments of the plane z (strict crossings; z must avoid vertex heights)."""
        hi = np.searchsorted(self.fmin_s, z)
        cand = self.order[:hi]
        cand = cand[self.fmax[cand] > z]
        if len(cand) == 0:
            return np.zeros((0, 2, 2))
        fe = self.FE[cand]                                   # (n,3) edge ids
        cr = (self.emin[fe] < z) & (self.emax[fe] > z)       # crossing flags
        ok = cr.sum(1) == 2
        fe = fe[ok]; cr = cr[ok]
        idx = np.argsort(~cr, axis=1, kind='stable')[:, :2]  # the two crossing edges per face
        ee = np.take_along_axis(fe, idx, 1)                  # (n,2)
        a = self.V[self.E[ee, 0]]; b = self.V[self.E[ee, 1]]  # (n,2,3)
        t = (z - a[..., 2]) / (b[..., 2] - a[..., 2])
        p = a[..., :2] + t[..., None] * (b[..., :2] - a[..., :2])
        return p                                              # (n,2,2)


def raster(seg, x0, y0, px, W, Hh):
    """Even-odd scanline raster of closed section segments. Pixel (j,i) centre = (x0+(i+.5)px, y0+(j+.5)px)."""
    if len(seg) == 0:
        return np.zeros((Hh, W), bool)
    X = (seg[..., 0] - x0) / px; Y = (seg[..., 1] - y0) / px
    ya, yb = Y[:, 0], Y[:, 1]; xa, xb = X[:, 0], X[:, 1]
    ymin = np.minimum(ya, yb); ymax = np.maximum(ya, yb)
    j0 = np.ceil(ymin - 0.5).astype(np.int64); j1 = np.ceil(ymax - 0.5).astype(np.int64) - 1
    n = np.maximum(j1 - j0 + 1, 0)
    keep = n > 0
    if not keep.any():
        return np.zeros((Hh, W), bool)
    j0, n, xa, xb, ya, yb = j0[keep], n[keep], xa[keep], xb[keep], ya[keep], yb[keep]
    rep = np.repeat(np.arange(len(n)), n)
    jj = j0[rep] + (np.arange(n.sum()) - np.repeat(np.cumsum(n) - n, n))
    yc = jj + 0.5
    xc = xa[rep] + (yc - ya[rep]) * (xb[rep] - xa[rep]) / (yb[rep] - ya[rep])
    ii = np.ceil(xc - 0.5).astype(np.int64)
    ok = (jj >= 0) & (jj < Hh)
    jj, ii = jj[ok], np.clip(ii[ok], 0, W)
    cnt = np.bincount(jj * (W + 1) + ii, minlength=Hh * (W + 1)).reshape(Hh, W + 1)
    return (np.cumsum(cnt[:, :W], axis=1) & 1).astype(bool)


def grid_for(mb, px, margin=2.0):
    lo = mb.bounds[0][:2] - margin; hi = mb.bounds[1][:2] + margin
    W = int(math.ceil((hi[0] - lo[0]) / px)); Hh = int(math.ceil((hi[1] - lo[1]) / px))
    return lo[0], lo[1], W, Hh


def px2b(j, i, x0, y0, px):
    return x0 + (np.asarray(i) + 0.5) * px, y0 + (np.asarray(j) + 0.5) * px


def overhang_stats(mb, bed_tol=0.3):
    """Downward-facing area by overhang angle from vertical (bed faces excluded) + flat-ceiling area."""
    n = mb.face_normals; a = mb.area_faces
    fz = mb.vertices[mb.faces][:, :, 2]
    bed = (fz < bed_tol).all(1)
    nz = n[:, 2]
    ang = np.degrees(np.arcsin(np.clip(-nz, -1, 1)))         # 90 = ceiling facing straight down; 0 = vertical
    down = (nz < 0) & ~bed
    bins = [(45, 60), (60, 70), (70, 80), (80, 90.01)]
    r = {'%d-%d' % (lo, min(hi, 90)): round(float(a[down & (ang >= lo) & (ang < hi)].sum()), 1) for lo, hi in bins}
    r['>=60'] = round(float(a[down & (ang >= 60)].sum()), 1)
    r['>=45'] = round(float(a[down & (ang >= 45)].sum()), 1)
    r['bed'] = round(float(a[bed & (nz < -0.99)].sum()), 1)
    return r


def footprint(mb):
    """Convex hull of all vertices in XY -> min-area rectangle (short, long), angle; and of the first layer."""
    from shapely.geometry import MultiPoint
    hull = MultiPoint(mb.vertices[:, :2]).convex_hull
    rect = hull.minimum_rotated_rectangle
    xs, ys = rect.exterior.coords.xy
    e = [math.hypot(xs[i + 1] - xs[i], ys[i + 1] - ys[i]) for i in range(2)]
    return {'hull_area': round(hull.area, 1), 'rect': sorted([round(e[0], 2), round(e[1], 2)]),
            'aabb': [round(float(v), 2) for v in (mb.extents[0], mb.extents[1])], 'height': round(float(mb.extents[2]), 2)}
