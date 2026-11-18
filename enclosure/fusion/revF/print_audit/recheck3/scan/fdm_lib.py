"""Print re-check of version 67 (recheck3): the design-for-FDM audit's analysis library, guard volumes of version 67.

Runs offline on the audit's own meshes (written read-only from Fusion by
fusion/f0_export_mesh.py). Nothing here touches the model.

Frames
  model : Fusion coordinates in mm (y = -depth behind the glass, z = up along the screen)
  world : x_w = x_m + 2.55 ; y_w = c*y_m - s*z_m ; z_w = s*y_m + c*z_m + 143.3   (12 degree lean)
  print : (u, v, h) per part; h = height above the bed along the part's build direction
"""
import json, math, os, pickle
import numpy as np
import trimesh
import shapely
from shapely.geometry import Polygon, MultiPolygon, box, Point
from shapely.ops import unary_union
from shapely.strtree import STRtree

C = math.cos(math.radians(12.0))
S = math.sin(math.radians(12.0))
XW = np.array([1.0, 0.0, 0.0])
YW = np.array([0.0, C, -S])
ZW = np.array([0.0, S, C])
YM = np.array([0.0, 1.0, 0.0])
ZM = np.array([0.0, 0.0, 1.0])

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MESH = os.path.join(ROOT, 'mesh')
DATA = os.path.join(ROOT, 'data')
IMG = os.path.join(ROOT, 'img')

# guard volumes of version 67 (brief of the print re-check, D228), mm3
GUARD = {
    'HOUSING_F_plate': 66463.676, 'HOUSING_F_front': 111611.475, 'SPKBOX_L': 26342.557,
    'SPKBOX_R': 27112.045, 'FLOOR_PLATE': 32643.331, 'RESP_CARRIER': 13651.988,
    'CRADLE_5807': 1771.219, 'HOUSING_F_door': 50476.660, 'HOUSING_F_cap': 9986.525,
    'TOUCH_CLIP_L': 580.762, 'TOUCH_CLIP_R': 580.762, 'SLAB_frame': 62932.407,
    'GROMMET_usbc_F': 506.176, 'BME_HOOD': 802.884,
}

# build-up direction of each print in model coordinates, and its layer height
PARTS = {
    'HOUSING_F_front': dict(up=-YW, lh=0.20, label='Shell, chin face down'),
    'HOUSING_F_plate': dict(up=YM, lh=0.20, label='Screen plate, back down'),
    'SPKBOX_L': dict(up=YW, lh=0.20, label='Left box, rear face down'),
    'SPKBOX_R': dict(up=YW, lh=0.20, label='Right box, rear face down'),
    'FLOOR_PLATE': dict(up=ZW, lh=0.20, label='Base plate, underside down'),
    'RESP_CARRIER': dict(up=-YM, lh=0.20, label="Carrier, slab's front down"),
    'CRADLE_5807': dict(up=YW, lh=0.20, label='Cradle, rear face down'),
    'TOUCH_CLIP_L': dict(up=ZW, lh=0.20, label='Touch clip L, as fitted'),
    'TOUCH_CLIP_R': dict(up=ZW, lh=0.20, label='Touch clip R, as fitted'),
    'BME_HOOD': dict(up=None, lh=0.20, label='BME680 hood, back plate down'),
    'HOUSING_F_cap': dict(up=-ZW, lh=0.12, label='Cap, top face down'),
    'GROMMET_usbc_F': dict(up=ZW, lh=0.12, label='Grommet, on its side, world z up'),
    'SLAB_frame': dict(up=-YM, lh=0.10, label='Bezel, glass side down'),
    'HOUSING_F_door': dict(up=ZW, lh=0.20, label='Door, standing on its bottom edge'),
}

# in-plane thickness classes in lines of the 0.4 nozzle (0.42 outer + 0.45 inner lines)
T_PLANE = [0.45, 0.85, 1.30, 1.70, 2.00, 2.60]


def to_world(p):
    p = np.atleast_2d(np.asarray(p, float))
    return np.c_[p[:, 0] + 2.55, p @ YW, p @ ZW + 143.3]


def load_model_mesh(name):
    v = np.fromfile(os.path.join(MESH, name + '.v.f32'), dtype=np.float32).reshape(-1, 3).astype(float)
    t = np.fromfile(os.path.join(MESH, name + '.t.i32'), dtype=np.int32).reshape(-1, 3)
    m = trimesh.Trimesh(vertices=v, faces=t, process=True)
    return m


def largest_flat_normal(m):
    fn = m.face_normals
    keys = np.round(fn, 3)
    uniq, inv = np.unique(keys, axis=0, return_inverse=True)
    ar = np.bincount(inv.ravel(), weights=m.area_faces)
    i = int(np.argmax(ar))
    sel = inv.ravel() == i
    n = (fn[sel] * m.area_faces[sel][:, None]).sum(0)
    return n / np.linalg.norm(n)


def frame(name, up=None):
    """(u, v, up) unit vectors in model coordinates; u x v = up."""
    up = PARTS[name]['up'] if up is None else up
    up = np.asarray(up, float) / np.linalg.norm(up)
    u = XW if abs(up @ XW) < 0.9 else YW
    u = u - (u @ up) * up
    u /= np.linalg.norm(u)
    v = np.cross(up, u)
    return u, v, up


class Part:
    def __init__(self, name, up=None):
        self.name = name
        self.lh = PARTS[name]['lh']
        self.m = load_model_mesh(name)
        if up is None and PARTS[name]['up'] is None:
            up = largest_flat_normal(self.m) * -1.0   # the largest flat face lies on the bed
        self.u, self.v, self.up = frame(name, up)
        V = self.m.vertices
        self.h0 = float((V @ self.up).min())
        P = np.c_[V @ self.u, V @ self.v, V @ self.up - self.h0]
        self.pm = trimesh.Trimesh(vertices=P, faces=self.m.faces, process=False)
        self.height = float(P[:, 2].max())
        self.layers = None

    # print (u, v, h) -> model, world
    def to_model(self, uvh):
        uvh = np.atleast_2d(np.asarray(uvh, float))
        return np.outer(uvh[:, 0], self.u) + np.outer(uvh[:, 1], self.v) + np.outer(uvh[:, 2] + self.h0, self.up)

    def uvh_to_world(self, uvh):
        return to_world(self.to_model(uvh))

    def slice(self, lh=None, cache=True):
        """Cross-sections at mid-layer heights -> list of (h, MultiPolygon)."""
        lh = lh or self.lh
        fn = os.path.join(DATA, 'layers_%s_%03d.pkl' % (self.name, round(lh * 100)))
        if cache and os.path.exists(fn):
            self.layers = pickle.load(open(fn, 'rb'))
            return self.layers
        n = int(math.ceil(self.height / lh - 1e-6))
        hs = (np.arange(n) + 0.5) * lh
        hs = hs[hs < self.height - 1e-4]
        secs = self.pm.section_multiplane(plane_origin=[0, 0, 0], plane_normal=[0, 0, 1], heights=hs)
        out = []
        for h, sec in zip(hs, secs):
            if sec is None:
                out.append((float(h), MultiPolygon()))
                continue
            polys = [p for p in sec.polygons_full if p is not None and p.area > 1e-6]
            # section_multiplane keeps one 2D frame; with normal +z it is the identity up to translation
            T = sec.metadata.get('to_3D', np.eye(4))
            if not np.allclose(T[:3, :3], np.eye(3), atol=1e-9) or abs(T[0, 3]) > 1e-9 or abs(T[1, 3]) > 1e-9:
                polys = [shapely.affinity.affine_transform(p, [T[0, 0], T[0, 1], T[1, 0], T[1, 1], T[0, 3], T[1, 3]]) for p in polys]
            g = unary_union(polys) if polys else MultiPolygon()
            out.append((float(h), g))
        self.layers = out
        if cache:
            pickle.dump(out, open(fn, 'wb'))
        return out


def polys_of(g):
    if g is None or g.is_empty:
        return []
    if g.geom_type == 'Polygon':
        return [g]
    if g.geom_type in ('MultiPolygon', 'GeometryCollection'):
        return [p for p in g.geoms if p.geom_type == 'Polygon' and not p.is_empty]
    return []


def opening(g, r, qs=8):
    if g.is_empty:
        return g
    return g.buffer(-r, quad_segs=qs).buffer(r, quad_segs=qs)


def inradius(p):
    try:
        line = shapely.maximum_inscribed_circle(p, tolerance=0.01)
        return float(line.length)
    except Exception:
        return 0.0


def rect_width(p):
    """Width of the rectangle that has this polygon's area and perimeter."""
    A, Pm = p.area, p.length
    d = Pm * Pm - 16.0 * A
    if d <= 0:
        return math.sqrt(A)
    return (Pm - math.sqrt(d)) / 4.0


def plane_bands(g, T=T_PLANE):
    """Split a layer's material by local in-plane thickness.
    Returns {k: [(piece, rect_width)]}; band k holds material thinner than T[k] and not thinner than T[k-1].
    Crescents left at corners by the two round offsets are dropped: a real feature of band k is at least
    T[k-1] wide, a crescent is far narrower."""
    out = {}
    prev = g
    lo = 0.0
    for k, t in enumerate(T):
        op = opening(g, t / 2.0)
        band = prev.difference(op) if not op.is_empty else prev
        prev = op if not op.is_empty else MultiPolygon()
        ps = [p for p in polys_of(band) if p.area >= 0.02]
        keep = []
        if ps:
            need = max(0.10, 0.40 * lo) if k > 0 else 0.05
            arr = np.array(ps, dtype=object)
            er = shapely.buffer(arr, -need, quad_segs=4)
            ok = ~shapely.is_empty(er)
            keep = [(p, rect_width(p)) for p, o in zip(ps, ok) if o]
        out[k] = keep
        lo = t
    return out


def cluster_band(layer_bands, k, hs, lh):
    """Join the thin pieces of band k that overlap in consecutive layers."""
    uf = UF()
    items = {}
    prev = []
    for li, bands in enumerate(layer_bands):
        cur = []
        for pi, (p, w) in enumerate(bands.get(k, [])):
            key = (li, pi)
            items[key] = (p, w)
            uf.find(key)
            cur.append((key, p))
        if prev and cur:
            tree = STRtree([p for _, p in prev])
            for key, p in cur:
                for j in tree.query(p):
                    q = prev[j][1]
                    if p.intersects(q) and p.intersection(q).area > 0.005:
                        uf.union(key, prev[j][0])
        prev = cur
    groups = {}
    for key in items:
        groups.setdefault(uf.find(key), []).append(key)
    clusters = []
    for root, keys in groups.items():
        lis = sorted(set(q[0] for q in keys))
        geoms = [items[q][0] for q in keys]
        b = shapely.total_bounds(np.array(geoms, dtype=object))
        per = {}
        for q in keys:
            per[q[0]] = per.get(q[0], 0.0) + items[q][0].area
        clusters.append(dict(band=k, keys=keys, layers=(lis[0], lis[-1]), nlayers=len(lis),
                             h=(round(hs[lis[0]] - lh / 2, 3), round(hs[lis[-1]] + lh / 2, 3)),
                             vol=sum(per.values()) * lh,
                             ubox=(float(b[0]), float(b[2])), vbox=(float(b[1]), float(b[3])),
                             area_max=max(per.values()),
                             wtyp=float(np.median([items[q][1] for q in keys]))))
    clusters.sort(key=lambda c: -c['vol'])
    return clusters, items


class UF:
    def __init__(self):
        self.p = {}

    def find(self, a):
        self.p.setdefault(a, a)
        while self.p[a] != a:
            self.p[a] = self.p[self.p[a]]
            a = self.p[a]
        return a

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb


def local_min_width(g, region, lo=0.05, hi=2.6, tol=0.02, margin=3.0):
    """Smallest local in-plane thickness of layer material g inside 'region' (a polygon), by bisection."""
    b = region.bounds
    clip = box(b[0] - margin, b[1] - margin, b[2] + margin, b[3] + margin)
    gg = g.intersection(clip)
    core = region.buffer(-0.02) if region.buffer(-0.02).area > 0 else region
    def lost(t):
        op = opening(gg, t / 2.0, qs=16)
        d = core.difference(op)
        return any(p.area > 0.003 and inradius(p) > 0.03 for p in polys_of(d))
    if lost(lo):
        return lo
    a, bb = lo, hi
    if not lost(hi):
        return hi
    while bb - a > tol:
        mid = 0.5 * (a + bb)
        if lost(mid):
            bb = mid
        else:
            a = mid
    return 0.5 * (a + bb)
