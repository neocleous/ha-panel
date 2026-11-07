# HA panel print audit (P4/P11): where the slicer's support touches the part. On a 0.25 mm grid, a support cell is a top
#   cell when no support prints there (+-0.5 mm) in the next layer; it is a contact when the part prints within 0.25 mm
#   of it in either of the next two layers (contact distance 0.2 + one layer); contact cells are clustered (8-connected, per 1 mm z band) and reported in build
#   and world coordinates (world via the inverse of the build transform). Usage: pa_contacts.py <gcode tag> <orient tag> <okey>
import sys, json, numpy as np
sys.path.insert(0, '/home/claude/pa')
from pa_gview import parse
from pa_geom import ORIENT, load_world, to_build, b2w
from scipy import ndimage as ndi
gtag, otag, okey = sys.argv[1], sys.argv[2], sys.argv[3]
S = parse('/home/claude/pa/slice/gc_%s.gcode' % gtag)
mw = load_world(otag); mb, M = to_build(mw, ORIENT[otag][okey])
# arrange offset: centre of the non-support extrusion bbox vs mesh bbox centre (perimeters inset symmetrically)
ns = S[S[:, 5] > 1]
gx = (min(ns[:, 1].min(), ns[:, 3].min()), max(ns[:, 1].max(), ns[:, 3].max()))
gy = (min(ns[:, 2].min(), ns[:, 4].min()), max(ns[:, 2].max(), ns[:, 4].max()))
b = mb.bounds
off = ((gx[0] + gx[1]) / 2 - (b[0][0] + b[1][0]) / 2, (gy[0] + gy[1]) / 2 - (b[0][1] + b[1][1]) / 2)
G = 0.25
x0, y0 = b[0][0] - 20, b[0][1] - 20
nx, ny = int((b[1][0] - b[0][0] + 40) / G) + 1, int((b[1][1] - b[0][1] + 40) / G) + 1


def rast(rows):
    m = np.zeros((nx, ny), bool)
    for r in rows:
        L = max(abs(r[3] - r[1]), abs(r[4] - r[2])); n = int(L / (G / 2)) + 2
        xs = np.linspace(r[1], r[3], n) - off[0]; ys = np.linspace(r[2], r[4], n) - off[1]
        i = ((xs - x0) / G).astype(int); j = ((ys - y0) / G).astype(int)
        ok = (i >= 0) & (i < nx) & (j >= 0) & (j < ny)
        m[i[ok], j[ok]] = True
    return m


zs = np.unique(S[:, 0])
byz = {round(float(z), 3): S[S[:, 0] == z] for z in zs}
cells = []
zl = [round(float(z), 3) for z in zs]
supm = {}
def supmask(k):
    if k not in supm:
        Lk = byz.get(k)
        supm[k] = rast(Lk[Lk[:, 5] <= 1]) if Lk is not None and (Lk[:, 5] <= 1).any() else np.zeros((nx, ny), bool)
    return supm[k]
partm = {}
def partmask(k):
    if k not in partm:
        Lk = byz.get(k)
        partm[k] = rast(Lk[Lk[:, 5] > 1]) if Lk is not None and (Lk[:, 5] > 1).any() else np.zeros((nx, ny), bool)
    return partm[k]
for z in zl:
    ms = supmask(z)
    if not ms.any():
        continue
    top = ms & ~ndi.binary_dilation(supmask(round(z + 0.2, 3)), iterations=2)   # support ends at this layer
    if not top.any():
        continue
    above = ndi.binary_dilation(partmask(round(z + 0.2, 3)) | partmask(round(z + 0.4, 3)), iterations=1)
    c = top & above
    for k in [k for k in list(supm) if k < z - 1e-6]:
        del supm[k]
    for k in [k for k in list(partm) if k < z - 1e-6]:
        del partm[k]
    if c.any():
        ii, jj = np.nonzero(c)
        for a, bb in zip(ii, jj):
            cells.append((z + 0.2, x0 + (a + 0.5) * G, y0 + (bb + 0.5) * G))
cells = np.array(cells) if cells else np.zeros((0, 3))
out = {'gcode': gtag, 'offset': off, 'n_cells': int(len(cells)), 'area_mm2_est': round(len(cells) * G * G, 1), 'clusters': []}
if len(cells):
    # cluster: 1 mm z bands x 8-connected grid
    zb = np.floor(cells[:, 0]).astype(int)
    for band in np.unique(zb):
        cb = cells[zb == band]
        m = np.zeros((nx, ny), bool)
        ii = ((cb[:, 1] - x0) / G).astype(int); jj = ((cb[:, 2] - y0) / G).astype(int); m[ii, jj] = True
        lab, n = ndi.label(ndi.binary_dilation(m, iterations=2), structure=np.ones((3, 3)))
        for k in range(1, n + 1):
            sel = lab[ii, jj] == k
            if sel.sum() < 2:
                continue
            p = cb[sel]
            w = b2w(M, np.c_[p[:, 1], p[:, 2], p[:, 0] - 0.1])
            out['clusters'].append({'z_build': [round(float(p[:, 0].min()), 2), round(float(p[:, 0].max()), 2)],
                                    'area_mm2': round(float(sel.sum() * G * G), 1),
                                    'bbox_build': [round(float(v), 1) for v in (p[:, 1].min(), p[:, 1].max(), p[:, 2].min(), p[:, 2].max())],
                                    'world_min': [round(float(v), 1) for v in w.min(0)], 'world_max': [round(float(v), 1) for v in w.max(0)]})
out['clusters'].sort(key=lambda c: -c['area_mm2'])
json.dump(out, open('/home/claude/pa/data/C_%s.json' % gtag, 'w'), indent=1)
print(gtag, 'contact cells', out['n_cells'], 'area est', out['area_mm2_est'], 'clusters', len(out['clusters']))
for c in out['clusters'][:15]:
    print('  zb %s a %6.1f  world x %6.1f..%6.1f y %6.1f..%6.1f z %6.1f..%6.1f' % (c['z_build'], c['area_mm2'], c['world_min'][0], c['world_max'][0], c['world_min'][1], c['world_max'][1], c['world_min'][2], c['world_max'][2]))
