"""recheck3: the audit slices of version 67 read back against the model, in the bed frame of each print.
  G(job)                 the parsed G-code (r3_gparse.py's seg.npz): S [x0, y0, x1, y1, z top, e, w, layer, tool, object], F feature index, names
  BedPart(tag, pos)      the model's mesh in the same bed frame (print files' matrix + the job's offset): layer polygons, world <-> bed
  props(...)             area and second moments of the extruded lines of one layer in a window (lines counted as length x width), by line type
  solid(...)             the same of the model's section; picture(...) panels of layers with the model's outline
World: x + = viewer's left, y + toward the viewer, z up. Bed frame of a job = print files' matrix M (world -> bed) + pos."""
import os, sys, json, math, numpy as np
sys.path.insert(0, '/home/claude/r3/scan/scripts')
import fdm_lib
from fdm_lib import to_world, MESH, polys_of
import trimesh, shapely
from shapely.geometry import box, MultiPolygon
from shapely.ops import unary_union
GDIR = '/mnt/user-data/uploads/HA_panel_renders/print_audit_recheck3/slicer/out'
ORI = json.load(open('/mnt/user-data/uploads/HA_panel_renders/print_files/_work/data/pf_2_orient.json'))
TAGS = {'screen': 'HOUSING_F_plate', 'shell': 'HOUSING_F_front', 'spkbox_L': 'SPKBOX_L', 'spkbox_R': 'SPKBOX_R', 'base': 'FLOOR_PLATE', 'carrier': 'RESP_CARRIER',
        'cradle': 'CRADLE_5807', 'clip_L': 'TOUCH_CLIP_L', 'clip_R': 'TOUCH_CLIP_R', 'bme_hood': 'BME_HOOD', 'cap': 'HOUSING_F_cap', 'grommet': 'GROMMET_usbc_F',
        'slab': 'SLAB_frame', 'door': 'HOUSING_F_door'}
COL = {'Outer wall': '#d95f02', 'Inner wall': '#e6ab02', 'Overhang wall': '#a6761d', 'Sparse infill': '#9a9a9a', 'Internal solid infill': '#1b9e77', 'Top surface': '#7570b3',
       'Bottom surface': '#7570b3', 'Bridge': '#66a61e', 'Gap infill': '#e7298a', 'Floating vertical shell': '#1f78b4', 'Support': '#bcd5ee', 'Support interface': '#4f8fd6',
       'Support transition': '#bcd5ee', 'Brim': '#dddddd'}
PART_EXCL = ('Support', 'Support interface', 'Support transition', 'Brim', 'Skirt', 'Custom')

class G:
    def __init__(self, job):
        z = np.load(os.path.join(GDIR, job, 'seg.npz'), allow_pickle=True)
        self.job = job; self.S = z['seg']; self.F = z['feat']; self.names = [str(n) for n in z['names']]; self.L = z['layers']; self.objs = [str(o) for o in z['objs']]
        self.lh = float(np.median(np.diff(self.L))) if len(self.L) > 1 else 0.2
        self.part = ~np.isin(self.F, [i for i, n in enumerate(self.names) if n in PART_EXCL])
        # layers that carry part lines (tree supports add layers of their own at other heights)
        self.PL = np.unique(self.S[self.part, 7]).astype(int)
    def layer_at(self, zbed):                       # index of the part layer that holds bed height zbed
        k = int(np.searchsorted(self.L[self.PL], zbed - 1e-6)); return int(self.PL[min(k, len(self.PL) - 1)])
    def lh_of(self, li):                            # height of part layer li
        k = int(np.searchsorted(self.PL, li)); return float(self.L[li] - (self.L[self.PL[k - 1]] if k > 0 else 0.0))
    def sel(self, li, win=None, part=True, obj=None):
        m = self.S[:, 7] == li
        if part: m &= self.part
        if obj is not None: m &= self.S[:, 9] == obj
        if win is not None:
            x0, x1, y0, y1 = win; s = self.S
            m &= (np.minimum(s[:, 0], s[:, 2]) < x1) & (np.maximum(s[:, 0], s[:, 2]) > x0) & (np.minimum(s[:, 1], s[:, 3]) < y1) & (np.maximum(s[:, 1], s[:, 3]) > y0)
        return m

class BedPart:
    def __init__(self, tag, pos=(0, 0, 0)):
        self.tag = tag; body = TAGS[tag]
        v = np.fromfile(os.path.join(MESH, body + '.v.f32'), dtype=np.float32).reshape(-1, 3).astype(float)
        t = np.fromfile(os.path.join(MESH, body + '.t.i32'), dtype=np.int32).reshape(-1, 3)
        self.M = np.array(ORI[tag]['M']); self.pos = np.array(pos, float)
        B = to_world(v) @ self.M[:3, :3].T + self.M[:3, 3] + self.pos
        self.m = trimesh.Trimesh(vertices=B, faces=t, process=True); self._lay = {}
    def to_bed(self, W):
        W = np.atleast_2d(np.asarray(W, float)); return W @ self.M[:3, :3].T + self.M[:3, 3] + self.pos
    def to_world(self, Bd):
        Bd = np.atleast_2d(np.asarray(Bd, float)); return (Bd - self.pos - self.M[:3, 3]) @ np.linalg.inv(self.M[:3, :3]).T
    def layer(self, zmid):
        k = round(zmid, 4)
        if k not in self._lay:
            sec = self.m.section(plane_origin=[0, 0, zmid], plane_normal=[0, 0, 1])
            if sec is None: self._lay[k] = MultiPolygon()
            else:
                p2, T = sec.to_2D()
                polys = [shapely.affinity.affine_transform(p, [T[0, 0], T[0, 1], T[1, 0], T[1, 1], T[0, 3], T[1, 3]]) for p in p2.polygons_full if p is not None and p.area > 1e-6]
                self._lay[k] = unary_union(polys) if polys else MultiPolygon()
        return self._lay[k]

def props(g, li, win, obj=None):
    """Extruded area in a window of one layer (line length x width), centroid, principal second moments, Ixx (about the x axis through the centroid), Iyy, by type."""
    b = g.S[g.sel(li, win, obj=obj)]; ft = g.F[g.sel(li, win, obj=obj)]
    x0, x1, y0, y1 = win
    if not len(b): return dict(A=0.0, mix={})
    P0 = b[:, 0:2].astype(float); P1 = b[:, 2:4].astype(float); L = np.hypot(*(P1 - P0).T); n = np.maximum(1, np.ceil(L / 0.05).astype(int))
    idx = np.repeat(np.arange(len(b)), n); k = np.concatenate([np.arange(m) for m in n]); f = (k + 0.5) / n[idx]
    C = P0[idx] + (P1[idx] - P0[idx]) * f[:, None]; dA = (L[idx] / n[idx]) * b[idx, 6]; typ = ft[idx]
    m = (C[:, 0] >= x0) & (C[:, 0] <= x1) & (C[:, 1] >= y0) & (C[:, 1] <= y1); C, dA, typ = C[m], dA[m], typ[m]
    A = dA.sum()
    if A <= 0: return dict(A=0.0, mix={})
    c = (C * dA[:, None]).sum(0) / A; d = C - c
    Ixx = (dA * d[:, 1] ** 2).sum(); Iyy = (dA * d[:, 0] ** 2).sum(); Ixy = (dA * d[:, 0] * d[:, 1]).sum(); ev = np.linalg.eigvalsh(np.array([[Ixx, -Ixy], [-Ixy, Iyy]]))
    return dict(A=float(A), c=c, Ixx=float(Ixx), Iyy=float(Iyy), I1=float(ev[0]), I2=float(ev[1]), J=float(Ixx + Iyy), ymax=float(np.abs(d[:, 1]).max()), xmax=float(np.abs(d[:, 0]).max()),
                rmax=float(np.hypot(d[:, 0], d[:, 1]).max()), mix={g.names[t]: float(dA[typ == t].sum()) for t in np.unique(typ)})

def solid(bp, zmid, win, step=0.04):
    gm = bp.layer(zmid).intersection(box(win[0], win[2], win[1], win[3]))
    if gm.is_empty: return dict(A=0.0)
    xs = np.arange(win[0], win[1], step) + step / 2; ys = np.arange(win[2], win[3], step) + step / 2
    X, Y = np.meshgrid(xs, ys); ins = shapely.contains(gm, shapely.points(X.ravel(), Y.ravel())); C = np.c_[X.ravel()[ins], Y.ravel()[ins]]; dA = step * step
    A = len(C) * dA; c = C.mean(0); d = C - c
    Ixx = (d[:, 1] ** 2).sum() * dA; Iyy = (d[:, 0] ** 2).sum() * dA; Ixy = (d[:, 0] * d[:, 1]).sum() * dA; ev = np.linalg.eigvalsh(np.array([[Ixx, -Ixy], [-Ixy, Iyy]]))
    return dict(A=float(A), c=c, Ixx=float(Ixx), Iyy=float(Iyy), I1=float(ev[0]), I2=float(ev[1]), J=float(Ixx + Iyy), ymax=float(np.abs(d[:, 1]).max()), xmax=float(np.abs(d[:, 0]).max()),
                rmax=float(np.hypot(d[:, 0], d[:, 1]).max()), geom=gm)

def mixstr(s, n=4):
    return ', '.join('%s %.0f%%' % (k.replace(' infill', '').replace('Internal ', ''), 100 * v / s['A']) for k, v in sorted(s['mix'].items(), key=lambda kv: -kv[1])[:n]) if s.get('A') else ''

def volbox(g, win, z0, z1, obj=None, part=True):
    """Extruded volume (length x width x layer height) by type for lines whose midpoint is in the window and whose layer top is in (z0, z1]."""
    s = g.S; m = (s[:, 4] > z0 + 1e-3) & (s[:, 4] <= z1 + 1e-3)
    if part: m &= g.part
    if obj is not None: m &= s[:, 9] == obj
    mx = (s[:, 0] + s[:, 2]) / 2; my = (s[:, 1] + s[:, 3]) / 2
    m &= (mx >= win[0]) & (mx <= win[1]) & (my >= win[2]) & (my <= win[3])
    b = s[m]; ln = np.hypot(b[:, 2] - b[:, 0], b[:, 3] - b[:, 1]); vol = ln * b[:, 6] * g.lh; out = {}
    for i, n in enumerate(g.names):
        mm = g.F[m] == i
        if mm.any(): out[n] = float(vol[mm].sum())
    return out

def panel(ax, g, li, win, bp=None, title='', support=True, legend=True):
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path
    x0, x1, y0, y1 = win
    if bp is not None:
        gm = bp.layer(float(g.L[li]) - g.lh / 2).intersection(box(x0 - 1, y0 - 1, x1 + 1, y1 + 1))
        for p in polys_of(gm):
            verts = []; codes = []
            for ring in [p.exterior] + list(p.interiors):
                c = np.asarray(ring.coords); verts += list(c); codes += [Path.MOVETO] + [Path.LINETO] * (len(c) - 2) + [Path.CLOSEPOLY]
            ax.add_patch(PathPatch(Path(verts, codes), facecolor='#f3f0e6', edgecolor='k', linewidth=0.6, zorder=0))
    m = g.sel(li, win, part=not support); b = g.S[m]; ft = g.F[m]
    fig = ax.figure; bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted()); ppm = bbox.width * 72 / (x1 - x0)
    for t in np.unique(ft):
        s = b[ft == t]; nm = g.names[t]
        if nm == 'Custom': continue
        segs = np.stack([s[:, 0:2], s[:, 2:4]], axis=1)
        ax.add_collection(LineCollection(segs, colors=COL.get(nm, '#000000'), linewidths=float(np.median(s[:, 6])) * ppm * 0.9, capstyle='round', label=nm, alpha=0.85, zorder=2))
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect('equal'); ax.tick_params(labelsize=6); ax.grid(True, linewidth=0.3, alpha=0.5)
    ax.set_title('%s  layer %d (top %.1f)' % (title, li + 1, g.L[li]), fontsize=8)
    if legend: ax.legend(fontsize=5, loc='lower left')

def sheet(out, specs, ncol=4, size=3.6):
    """specs: (G, layer index, window, BedPart or None, title)"""
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    n = len(specs); nrow = (n + ncol - 1) // ncol
    fig, axs = plt.subplots(nrow, ncol, figsize=(size * ncol, size * nrow), dpi=110, squeeze=False); fig.tight_layout(pad=1.6)
    for ax in axs.ravel()[n:]: ax.axis('off')
    for ax, s in zip(axs.ravel(), specs): panel(ax, s[0], s[1], s[2], s[3], s[4])
    fig.savefig(out); plt.close(fig)

# ---- the printed footprint of a layer as geometry (lines drawn with their width, overlaps counted once) ----
from shapely.geometry import LineString
def foot(g, li, win, obj=None, pad=1.0, exclude=()):
    x0, x1, y0, y1 = win; m = g.sel(li, (x0 - pad, x1 + pad, y0 - pad, y1 + pad), obj=obj)
    if exclude: m &= ~np.isin(g.F, [i for i, n in enumerate(g.names) if n in exclude])
    b = g.S[m]
    if not len(b): return MultiPolygon()
    co = np.stack([b[:, 0:2], b[:, 2:4]], axis=1).astype(float)
    bufs = shapely.buffer(shapely.linestrings(co), b[:, 6].astype(float) / 2.0, quad_segs=4)
    return shapely.union_all(bufs).intersection(box(x0, y0, x1, y1))

def gprops(gm, win, step=0.04, about=None):
    """Area, centroid and second moments of a geometry by sampling; about = (x, y) gives the polar moment about that point as well."""
    if gm.is_empty: return dict(A=0.0)
    xs = np.arange(win[0], win[1], step) + step / 2; ys = np.arange(win[2], win[3], step) + step / 2
    X, Y = np.meshgrid(xs, ys); ins = shapely.contains(gm, shapely.points(X.ravel(), Y.ravel())); C = np.c_[X.ravel()[ins], Y.ravel()[ins]]; dA = step * step
    if not len(C): return dict(A=0.0)
    A = len(C) * dA; c = C.mean(0); d = C - c
    out = dict(A=float(A), c=c, Ixx=float((d[:, 1] ** 2).sum() * dA), Iyy=float((d[:, 0] ** 2).sum() * dA), ymax=float(np.abs(d[:, 1]).max()), xmax=float(np.abs(d[:, 0]).max()))
    out['J'] = out['Ixx'] + out['Iyy']
    if about is not None:
        r = np.hypot(C[:, 0] - about[0], C[:, 1] - about[1]); out['Jo'] = float((r ** 2).sum() * dA); out['ro'] = float(r.max())
    return out

def vcut(g, bp, axis, value, lo, hi, z0, z1, obj=None, dz=None):
    """A cut square to the bed along x = value (axis 'x', spanning y lo..hi) or y = value (axis 'y'): per layer the printed and the modelled length on the cut line.
    Returns dict with area and second moment about the horizontal axis through each centroid (bending depth along the print height), printed and modelled."""
    rows = []
    for li in range(g.layer_at(z0 + 1e-3), g.layer_at(z1 - 1e-3) + 1):
        zt = float(g.L[li]); zm = zt - g.lh / 2
        if axis == 'x': win = (value - 0.6, value + 0.6, lo, hi); ln = LineString([(value, lo), (value, hi)])
        else: win = (lo, hi, value - 0.6, value + 0.6); ln = LineString([(lo, value), (hi, value)])
        P = foot(g, li, win, obj=obj); Mo = bp.layer(zm)
        rows.append((zm, P.intersection(ln).length if not P.is_empty else 0.0, Mo.intersection(ln).length if not Mo.is_empty else 0.0))
    R = np.array(rows); out = {'rows': R}
    for k, col in (('sliced', 1), ('model', 2)):
        a = R[:, col] * g.lh; A = a.sum()
        if A <= 0: out[k] = dict(A=0.0); continue
        zc = (a * R[:, 0]).sum() / A; I = (a * (R[:, 0] - zc) ** 2).sum() + (a * g.lh ** 2 / 12).sum()
        cmax = max(R[R[:, col] > 0, 0].max() + g.lh / 2 - zc, zc - (R[R[:, col] > 0, 0].min() - g.lh / 2))
        out[k] = dict(A=float(A), zc=float(zc), I=float(I), c=float(cmax), Z=float(I / cmax))
    return out

def vcut2(g, bp, axis, value, lo, hi, z0, z1, obj=None, ds=0.02):
    """As vcut, but sampled along the cut line: occupancy arrays (layers x samples), printed and modelled, with both second moments:
    Iv about the axis that lies in the layers (bending depth along the print height) and Ih about the axis along the print height (bending depth in the layers)."""
    s = np.arange(lo, hi, ds) + ds / 2; rows = []; zs = []; lhs = []
    for li in g.PL:
        zt = float(g.L[li])
        if zt <= z0 + 1e-3 or zt > z1 + 1e-3: continue
        lh = g.lh_of(li); zm = zt - lh / 2
        if axis == 'x': win = (value - 0.6, value + 0.6, lo, hi); pts = shapely.points(np.full(len(s), value), s)
        else: win = (lo, hi, value - 0.6, value + 0.6); pts = shapely.points(s, np.full(len(s), value))
        P = foot(g, li, win, obj=obj); Mo = bp.layer(zm)
        rows.append((shapely.contains(P, pts) if not P.is_empty else np.zeros(len(s), bool), shapely.contains(Mo, pts) if not Mo.is_empty else np.zeros(len(s), bool))); zs.append(zm); lhs.append(lh)
    zs = np.array(zs); lhs = np.array(lhs); out = {'s': s, 'z': zs}
    for k, idx in (('sliced', 0), ('model', 1)):
        O = np.array([r[idx] for r in rows], float); dA = O * ds * lhs[:, None]; A = dA.sum()
        if A <= 0: out[k] = dict(A=0.0); continue
        zc = (dA.sum(1) * zs).sum() / A; sc = (dA.sum(0) * s).sum() / A
        Iv = (dA * (zs[:, None] - zc) ** 2).sum(); Ih = (dA * (s[None, :] - sc) ** 2).sum()
        zz = zs[O.any(1)]; ss = s[O.any(0)]
        cv = max(zz.max() + lhs.max() / 2 - zc, zc - (zz.min() - lhs.max() / 2)); ch = max(ss.max() - sc, sc - ss.min())
        out[k] = dict(A=float(A), Iv=float(Iv), Zv=float(Iv / cv), Ih=float(Ih), Zh=float(Ih / ch), occ=O)
    return out
