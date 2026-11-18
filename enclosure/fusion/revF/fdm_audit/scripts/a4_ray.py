"""Block 1: true (orientation-free) thickness of every printed part by ray casting.
From sample points all over the surface a ray goes into the material along the inward normal;
its length to the opposite face is the local thickness. Thin samples of one class that lie
together are joined into features. Each feature is tagged by how it stands in the print:
wall (thickness lies in the layers -> counted in lines), skin (thickness lies along the build
height -> counted in layers) or sloped."""
import sys, time, json, numpy as np
from scipy import ndimage
from fdm_lib import *

TT = [t - 0.02 for t in T_PLANE]      # a feature of exactly 0.85 counts as 2 lines
G = 0.7                               # grid for joining samples, mm

def run(name, dens=10.0):
    t0 = time.time()
    p = Part(name)
    m = p.m
    n = int(m.area * dens)
    pts, fi = trimesh.sample.sample_surface(m, n, seed=1)
    nrm = m.face_normals[fi]
    eps = 0.01
    org = pts - eps * nrm
    loc, ir, it = m.ray.intersects_location(org, -nrm, multiple_hits=False)
    t = np.full(n, np.nan)
    t[ir] = np.linalg.norm(loc - org[ir], axis=1) + eps
    ok = ~np.isnan(t)
    cls = np.digitize(t, TT)          # 0..6 ; 6 = 2.6 or more
    cls[~ok] = 9
    a_s = m.area / n                  # area per sample
    upc = np.abs(nrm @ p.up)
    uvh = np.c_[pts @ p.u, pts @ p.v, pts @ p.up - p.h0]
    lo = pts.min(0) - G
    ijk = np.floor((pts - lo) / G).astype(int)
    shape = ijk.max(0) + 2
    rows = []
    st = np.ones((3, 3, 3), bool)
    for k in range(len(TT)):
        sel = np.where(cls == k)[0]
        if len(sel) == 0:
            continue
        grid = np.zeros(shape, bool)
        grid[ijk[sel, 0], ijk[sel, 1], ijk[sel, 2]] = True
        lab, nl = ndimage.label(grid, structure=st)
        l = lab[ijk[sel, 0], ijk[sel, 1], ijk[sel, 2]]
        order = np.argsort(l)
        l_sorted = l[order]
        cuts = np.flatnonzero(np.diff(l_sorted)) + 1
        for grp in np.split(order, cuts):
            s = sel[grp]
            area = len(s) * a_s / 2.0     # both faces of a wall are sampled
            if area < 1.0:
                continue
            w = to_world(pts[s])
            rows.append(dict(cls=k, n=int(len(s)), area=round(float(area), 1),
                             tmin=round(float(np.percentile(t[s], 2)), 2), tmed=round(float(np.median(t[s])), 2),
                             upc=round(float(upc[s].mean()), 2),
                             h=[round(float(uvh[s, 2].min()), 2), round(float(uvh[s, 2].max()), 2)],
                             ubox=[round(float(uvh[s, 0].min()), 2), round(float(uvh[s, 0].max()), 2)],
                             vbox=[round(float(uvh[s, 1].min()), 2), round(float(uvh[s, 1].max()), 2)],
                             wmin=[round(float(x), 1) for x in w.min(0)], wmax=[round(float(x), 1) for x in w.max(0)]))
    rows.sort(key=lambda r: (r['cls'], -r['area']))
    json.dump(rows, open(os.path.join(DATA, 'ray_%s.json' % name), 'w'))
    np.savez_compressed(os.path.join(DATA, 'ray_%s.npz' % name), pts=pts.astype(np.float32), t=t.astype(np.float32), fi=fi.astype(np.int32))
    frac = [(cls == k).sum() * a_s / 2 for k in range(7)]
    print('%-16s area %.0f rays %d miss %d | area by class (mm2, one face): %s | features %d | dt %.0fs' % (
        name, m.area, n, int((~ok).sum()), ' '.join('%.0f' % f for f in frac), len(rows), time.time() - t0), flush=True)

if __name__ == '__main__':
    for nme in sys.argv[1:]:
        run(nme)
