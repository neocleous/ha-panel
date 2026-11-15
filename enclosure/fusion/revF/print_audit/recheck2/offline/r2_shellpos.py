# recheck2: positions as sliced in the chin-down shell (world y = 6.799 - bed z): the driver-flange pads (y 1.30, facing the door),
#   the four lands (d 12.8, facing the screen) and the screen-facing fronts (d 13.0); printed surfaces against the model planes.
import sys, json, math, numpy as np
sys.path.insert(0, '/home/claude/r2/offline')
from r2_gq import G
C12, S12 = math.cos(math.radians(12)), math.sin(math.radians(12)); H = 143.3
g = G('A_shell_plain', 'shell'); part = g.fmask(exclude=('Support', 'Brim', 'Skirt'))
Z = np.array(sorted(set(round(float(v), 3) for v in g.S[:, 4])))
def wpt(x, d, up):  # slab frame -> world
    return np.array([x, -d * C12 - up * S12, H - d * S12 + up * C12])
def covered_layers(Wpts, zlo, zhi, px=0.02):
    """for each world point: sorted list of layer tops (bed z) whose part extrusions cover its bed xy, zlo < z < zhi"""
    B = g.to_bed(Wpts)
    x0, x1 = B[:, 0].min() - 0.6, B[:, 0].max() + 0.6; y0, y1 = B[:, 1].min() - 0.6, B[:, 1].max() + 0.6
    W = int((x1 - x0) / px) + 1; Hh = int((y1 - y0) / px) + 1
    ii = ((B[:, 0] - x0) / px).astype(int); jj = ((B[:, 1] - y0) / px).astype(int)
    cov = [[] for _ in range(len(B))]
    for z in Z[(Z > zlo) & (Z < zhi)]:
        R = g.raster(part, z, x0, y0, W, Hh, px)
        for k in np.nonzero(R[jj, ii])[0]:
            cov[k].append(float(z))
    return B, cov
out = {}
# 1. driver-flange pads, model y 1.300 (bed z 5.499), x 48.75..56.75 / 84.25..92.25 both sides, z 11.5..44.5
for nm, (xa, xb) in (('pad_L_in', (48.75, 56.75)), ('pad_L_out', (84.25, 92.25)), ('pad_R_in', (-56.75, -48.75)), ('pad_R_out', (-92.25, -84.25))):
    pts = np.array([[x, 1.0, z] for x in np.linspace(xa + 0.6, xb - 0.6, 6) for z in np.linspace(14, 42, 8)])
    B, cov = covered_layers(pts, 4.0, 7.0)
    tops = [max(c) for c in cov if c]
    out[nm] = {'model_y': 1.300, 'printed_top_bed_z': sorted(set(tops)), 'printed_y': sorted(set(round(6.799 - t, 3) for t in tops))}
# 2. lands: d 12.8; top posts x +-70 up 27 (r <= 4.5), bottom posts x +-85 up -82 (3.6 < r <= 4.5)
for nm, (xc, uc, r0) in (('land_TL', (70, 27, 0)), ('land_TR', (-70, 27, 0)), ('land_BL', (85, -82, 3.6)), ('land_BR', (-85, -82, 3.6))):
    S = []
    for r in np.linspace(max(r0, 2.0) + 0.15, 4.35, 5):
        for th in np.linspace(0, 2 * math.pi, 37)[:-1]:
            S.append((xc + r * math.cos(th), uc + r * math.sin(th)))
    Wp = np.array([wpt(x, 12.8, u) for x, u in S])
    zmodel = 6.799 - Wp[:, 1]
    B, cov = covered_layers(Wp, zmodel.min() - 1.5, zmodel.max() + 1.5)
    bottoms = np.array([min(c) - 0.2 if c else np.nan for c in cov])
    dz = zmodel - bottoms               # + = printed surface below the model (toward the bed = toward the plate)
    ok = ~np.isnan(dz)
    out[nm] = {'model_bed_z': [round(float(zmodel.min()), 3), round(float(zmodel.max()), 3)], 'covered': round(float(ok.mean()), 3),
               'protrude_max_normal': round(float(np.nanmax(dz) * C12), 3), 'protrude_mean_normal': round(float(np.nanmean(dz) * C12), 3),
               'protrude_min_normal': round(float(np.nanmin(dz) * C12), 3)}
# 3. fronts at d 13.0: top band (x -70..70, up 30..35.5), side walls' fronts (strip x +-81.0..81.4 at up 0..30; x +-92.8..92.9 at up -40)
fr = {'band_front': [(x, u) for x in np.linspace(-60, 60, 13) for u in np.linspace(30.5, 35.0, 4)],
      'wall_L_up20': [(81.2, u) for u in np.linspace(14, 26, 13)], 'wall_R_up20': [(-81.2, u) for u in np.linspace(14, 26, 13)],
      'rail': [(x, -90.6) for x in np.linspace(-40, 40, 17)]}
for nm, S in fr.items():
    Wp = np.array([wpt(x, 13.0, u) for x, u in S]); zmodel = 6.799 - Wp[:, 1]
    B, cov = covered_layers(Wp, max(0.0, zmodel.min() - 1.5), zmodel.max() + 1.5)
    bottoms = np.array([min(c) - (0.2 if min(c) > 0.21 else 0.2) if c else np.nan for c in cov])
    dz = zmodel - bottoms; ok = ~np.isnan(dz)
    out[nm] = {'model_bed_z': [round(float(zmodel.min()), 3), round(float(zmodel.max()), 3)], 'covered': round(float(ok.mean()), 3),
               'protrude_max_normal': round(float(np.nanmax(dz) * C12), 3) if ok.any() else None,
               'protrude_mean_normal': round(float(np.nanmean(dz) * C12), 3) if ok.any() else None}
print(json.dumps(out, indent=1))
json.dump(out, open('/home/claude/r2/data/shell_positions.json', 'w'), indent=1)
