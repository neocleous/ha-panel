"""recheck3: regions of a part that start in mid-air (a piece of a layer with nothing of the part in the layer below), on the model's layers in the bed frame,
and what the slice with supports puts under each: the share of the region's footprint covered by support or interface lines in the 0.45 below it.
Usage: r3_midair.py <key> ...  (keys as r3_cover.JOBS)"""
import sys, json, numpy as np
from r3_gq import *
import r3_cover
SUP = ('Support', 'Support interface', 'Support transition')
def run(key, amin=0.5, lh0=None):
    job, tag, pos, obj = r3_cover.JOBS[key]; g = G(job); bp = BedPart(tag, pos); S = g.S
    msk = g.part.copy()
    if obj is not None: msk &= S[:, 9] == obj
    PL = np.unique(S[msk, 7]).astype(int); sup = np.isin(g.F, [i for i, n in enumerate(g.names) if n in SUP])
    rows = []; prev = None
    for k, li in enumerate(PL):
        zt = float(g.L[li]); lh = zt - (float(g.L[PL[k - 1]]) if k else 0.0); zm = zt - lh / 2; Mo = bp.layer(zm)
        if prev is not None and not Mo.is_empty:
            pb = prev.buffer(0.02)
            for p in polys_of(Mo):
                if p.area >= amin and not p.intersects(pb):
                    zb = zt - lh                                   # the region's underside
                    b = p.bounds; m = sup & (S[:, 4] > zb - 0.45) & (S[:, 4] <= zb + 1e-3) & (np.minimum(S[:, 0], S[:, 2]) < b[2] + 1) & (np.maximum(S[:, 0], S[:, 2]) > b[0] - 1) & \
                        (np.minimum(S[:, 1], S[:, 3]) < b[3] + 1) & (np.maximum(S[:, 1], S[:, 3]) > b[1] - 1)
                    s = S[m]; cov = 0.0; ifc = 0.0
                    if len(s):
                        co = np.stack([s[:, 0:2], s[:, 2:4]], axis=1).astype(float)
                        U = shapely.union_all(shapely.buffer(shapely.linestrings(co), s[:, 6].astype(float) / 2 + 0.15, quad_segs=3)); cov = U.intersection(p).area / p.area
                        si = s[np.isin(g.F[m], [i for i, n in enumerate(g.names) if n == 'Support interface'])]
                        if len(si):
                            coi = np.stack([si[:, 0:2], si[:, 2:4]], axis=1).astype(float)
                            ifc = shapely.union_all(shapely.buffer(shapely.linestrings(coi), si[:, 6].astype(float) / 2 + 0.15, quad_segs=3)).intersection(p).area / p.area
                    # does the layer's own first pass over the region count as a bridge between printed neighbours? (not judged here)
                    c = p.representative_point(); w = bp.to_world([[c.x, c.y, zb]])[0]
                    wb = bp.to_world([[b[0], b[1], zb], [b[2], b[3], zb]])
                    rows.append(dict(z=round(zb, 2), area=round(p.area, 2), world=[round(float(v), 1) for v in w], wlo=[round(float(v), 1) for v in wb.min(0)], whi=[round(float(v), 1) for v in wb.max(0)],
                                     support=round(cov, 2), interface=round(ifc, 2)))
        prev = Mo
    rows.sort(key=lambda r: -r['area'])
    json.dump(rows, open('/home/claude/r3/data/midair_%s.json' % key, 'w'))
    print('%s (%s): %d regions of %.1f mm2 or more start in mid-air' % (key, job, len(rows), amin))
    for r in rows:
        print('   %7.2f mm2 at bed z %.2f | world x %.1f..%.1f y %.1f z %.1f..%.1f | support under %3.0f%% (interface %3.0f%%)' % (r['area'], r['z'], r['wlo'][0], r['whi'][0], r['world'][1], r['wlo'][2], r['whi'][2],
              100 * r['support'], 100 * r['interface']) if tag == 'shell' else '   %7.2f mm2 at bed z %.2f | world x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f | support under %3.0f%% (interface %3.0f%%)' % (
              r['area'], r['z'], r['wlo'][0], r['whi'][0], r['wlo'][1], r['whi'][1], r['wlo'][2], r['whi'][2], 100 * r['support'], 100 * r['interface']))
if __name__ == '__main__':
    for k in sys.argv[1:]: run(k)
