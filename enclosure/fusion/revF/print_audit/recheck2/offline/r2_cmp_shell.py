# recheck2: compare shell slices (0.2 vs 0.3 first layer): window faces, lands, gap-border faces, post-hole mouths, layer-1 webs
import sys, json, math, numpy as np
sys.path.insert(0, '/home/claude/r2/offline')
from r2_gq import G
from r2_vis import run as vis
from r2_holes import run as holes
C12, S12 = math.cos(math.radians(12)), math.sin(math.radians(12)); H = 143.3
def wpt(x, d, up): return np.array([x, -d * C12 - up * S12, H - d * S12 + up * C12])
def land(g, part, Z, xc, uc, r0, r1, dplane=12.8):
    S = [(xc + r * math.cos(t), uc + r * math.sin(t)) for r in np.linspace(r0, r1, 4) for t in np.linspace(0, 2 * math.pi, 49)[:-1]]
    Wp = np.array([wpt(x, dplane, u) for x, u in S]); zmodel = 6.7992 - Wp[:, 1]
    B = g.to_bed(Wp); px = 0.02
    x0, y0 = B[:, 0].min() - 0.6, B[:, 1].min() - 0.6; W = int((B[:, 0].max() + 0.6 - x0) / px) + 1; Hh = int((B[:, 1].max() + 0.6 - y0) / px) + 1
    ii = ((B[:, 0] - x0) / px).astype(int); jj = ((B[:, 1] - y0) / px).astype(int)
    first = np.full(len(B), np.nan); bottom = {}
    zs = list(Z); 
    for k, z in enumerate(zs):
        if not (zmodel.min() - 1.5 < z < zmodel.max() + 1.5): continue
        R = g.raster(part, z, x0, y0, W, Hh, px); c = R[jj, ii] & np.isnan(first); first[c] = z
    lb = {z: (zs[k - 1] if k else 0.0) for k, z in enumerate(zs)}      # layer bottom
    fb = np.array([lb[z] if not np.isnan(z) else np.nan for z in first])
    dz = (zmodel - fb) * C12
    return [round(float(np.nanmax(dz)), 3), round(float(np.nanmean(dz)), 3), round(float(np.nanmin(dz)), 3)]
for job in sys.argv[1:]:
    g = G(job, 'shell'); part = g.fmask(exclude=('Support', 'Brim', 'Skirt'))
    Z = np.array(sorted(set(np.round(g.S[:, 4], 3))))
    print('==', job, 'first layers', Z[:3].tolist())
    v = vis(job, 'shell', [372, 370, 383, 501, 502], '/mnt/user-data/uploads/print_audit_recheck2/exports/shell.stl')
    for k, d in v.items(): print(' face', k, 'prot mean %.3f (min %.3f, max %.3f), on support %s' % (d['prot_mean'], d['prot_min'], d['prot_max'], d['sup']))
    for nm, a in (('TL', (70, 27, 2.2, 4.3)), ('TR', (-70, 27, 2.2, 4.3)), ('BL', (85, -82, 3.95, 4.35)), ('BR', (-85, -82, 3.95, 4.35))):
        print(' land', nm, 'toward the plate max/mean/min', land(g, part, Z, *a))
    h = holes(job, 'shell', [14, 16, 1479, 1480], 4.5)
    for r in h:
        rows = [x for x in r['rows'] if x[1] > 1.5]
        print(' hole', r['face'], 'mouth layers', [x for x in rows[:6]])
