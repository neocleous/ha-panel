# P8: bracket halves upright - per-layer section properties (area, second moments about the section centroid) from the layer
# stacks; bending stress at each layer interface for a horizontal force F at the upper board screws (z 80.5) acting along
# world y (push on the board face) and along x. Interlayer bending strength: Bambu ASA TDS V3.0 bending strength (Z) 40 MPa.
import sys, json, numpy as np
sys.path.insert(0, '/home/claude/pa')
from pa_geom import *
res = {}
for tag in ('bracket_L', 'bracket_R'):
    z = np.load('/home/claude/pa/work/M_%s_plan.npz' % tag)
    Hh, W = [int(v) for v in z['shape']]; x0, y0, px = [float(v) for v in z['grid']]; zs = z['zs']
    jj, ii = np.mgrid[0:Hh, 0:W]; X = x0 + (ii + 0.5) * px; Y = y0 + (jj + 0.5) * px
    rows = []
    for k in range(len(zs)):
        m = np.unpackbits(z['packed'][k])[:Hh * W].reshape(Hh, W).astype(bool)
        A = m.sum() * px * px
        if A == 0: continue
        cx = X[m].mean(); cy = Y[m].mean()
        Ix = ((Y[m] - cy) ** 2).sum() * px * px   # about x-axis: bending from a force along y
        Iy = ((X[m] - cx) ** 2).sum() * px * px
        cyy = np.abs(Y[m] - cy).max(); cxx = np.abs(X[m] - cx).max()
        rows.append((float(zs[k]), A, Ix / cyy, Iy / cxx, cx, cy))
    rows = np.array(rows)
    zt = 80.5 - 2.5          # build z of the upper board screw (world 80.5, bracket bottom at world 2.5)
    sel = rows[:, 0] < zt
    lev = zt - rows[sel, 0]
    sy = lev / rows[sel, 2]   # stress per N for force along y  (MPa/N)
    sx = lev / rows[sel, 3]
    iy = int(np.argmax(sy)); ix = int(np.argmax(sx))
    out = {'max_stress_per_N_y': round(float(sy[iy]), 3), 'at_build_z': round(float(rows[sel][iy, 0]), 2), 'W_y_mm3': round(float(rows[sel][iy, 2]), 1),
           'area_mm2': round(float(rows[sel][iy, 1]), 1), 'F_crit_y_N_at_40MPa': round(40 / float(sy[iy]), 1),
           'max_stress_per_N_x': round(float(sx[ix]), 3), 'at_build_z_x': round(float(rows[sel][ix, 0]), 2), 'W_x_mm3': round(float(rows[sel][ix, 3]), 1),
           'F_crit_x_N_at_40MPa': round(40 / float(sx[ix]), 1)}
    # column section at world z 50 (build 47.5) for reference
    kk = int(np.argmin(np.abs(rows[:, 0] - 47.5)))
    out['column_world_z50'] = {'area': round(float(rows[kk, 1]), 1), 'W_y': round(float(rows[kk, 2]), 1), 'W_x': round(float(rows[kk, 3]), 1)}
    # profile every 5 mm
    out['profile'] = [[round(float(r[0]) + 2.5, 1), round(float(r[1]), 1), round(float(r[2]), 1), round(float(r[3]), 1)] for r in rows[::25]]
    res[tag] = out
    print(tag, json.dumps({k: v for k, v in out.items() if k != 'profile'}))
    print('   world z, area, W_y, W_x:', out['profile'][:18])
json.dump(res, open('/home/claude/pa/data/p8_bracket.json', 'w'), indent=1)
