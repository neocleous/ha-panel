"""Block 1: narrow air gaps inside one printed body (slits between features that should be one piece,
slots narrower than a line). Rays go OUT of the surface; a hit on the same body within GMAX is a gap."""
import sys, json, numpy as np
from scipy import ndimage
from fdm_lib import *
GMAX = 0.45; G = 0.7

def run(name, dens=10.0):
    p = Part(name); m = p.m
    n = int(m.area * dens)
    pts, fi = trimesh.sample.sample_surface(m, n, seed=2)
    nrm = m.face_normals[fi]
    eps = 0.002
    org = pts + eps * nrm
    loc, ir, it = m.ray.intersects_location(org, nrm, multiple_hits=False)
    g = np.full(n, np.inf); g[ir] = np.linalg.norm(loc - org[ir], axis=1) + eps
    sel = np.where(g < GMAX)[0]
    rows = []
    if len(sel):
        lo = pts.min(0) - G; ijk = np.floor((pts[sel] - lo) / G).astype(int)
        grid = np.zeros(ijk.max(0) + 2, bool); grid[ijk[:, 0], ijk[:, 1], ijk[:, 2]] = True
        lab, nl = ndimage.label(grid, structure=np.ones((3, 3, 3), bool))
        l = lab[ijk[:, 0], ijk[:, 1], ijk[:, 2]]
        a_s = m.area / n
        for k in range(1, nl + 1):
            s = sel[l == k]
            area = len(s) * a_s / 2
            if area < 0.5: continue
            w = to_world(pts[s]); uvh = np.c_[pts[s] @ p.u, pts[s] @ p.v, pts[s] @ p.up - p.h0]
            rows.append(dict(area=round(float(area), 1), gmin=round(float(np.percentile(g[s], 10)), 3), gmed=round(float(np.median(g[s])), 3), g90=round(float(np.percentile(g[s], 90)), 3),
                             upc=round(float(np.abs(nrm[s] @ p.up).mean()), 2), h=[round(float(uvh[:, 2].min()), 1), round(float(uvh[:, 2].max()), 1)],
                             wmin=[round(float(x), 1) for x in w.min(0)], wmax=[round(float(x), 1) for x in w.max(0)]))
    rows.sort(key=lambda r: -r['area'])
    json.dump(rows, open(os.path.join(DATA, 'gaps_%s.json' % name), 'w'))
    print('%-16s gaps under %.2f: %d' % (name, GMAX, len(rows)))
    rows = [r for r in rows if r['g90'] - r['gmin'] < 0.12 or r['g90'] < 0.2]
    json.dump(rows, open(os.path.join(DATA, 'slits_%s.json' % name), 'w'))
    print('   of these, slits of even width:', len(rows))
    for r in rows[:20]:
        print('   area %6.1f gap p10 %.3f med %.3f p90 %.3f %s h %.1f-%.1f | x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f' % (
            r['area'], r['gmin'], r['gmed'], r['g90'], 'flat' if r['upc'] > 0.87 else ('upright' if r['upc'] < 0.35 else 'slope'), r['h'][0], r['h'][1],
            r['wmin'][0], r['wmax'][0], r['wmin'][1], r['wmax'][1], r['wmin'][2], r['wmax'][2]))

if __name__ == '__main__':
    for nme in sys.argv[1:] or list(GUARD):
        run(nme)
