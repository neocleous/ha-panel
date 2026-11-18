"""recheck3: faces that look at the bed. For each part layer: the part of the layer that reaches more than 0.45 beyond the layer below (flatter than about 24 deg
from the bed), opened by r 0.2; for each such piece its area and the share of it that has support or interface lines in the 0.45 under it. Pieces that overlap in
consecutive layers or lie within 1.5 mm in one layer are grouped. Usage: r3_overhang.py <key> [min area]"""
import sys, json, numpy as np
from r3_gq import *
from fdm_lib import UF, opening
from shapely.strtree import STRtree
import r3_cover
SUP = ('Support', 'Support interface', 'Support transition')
def run(key, amin=1.0, show=40, cover_max=1.01):
    job, tag, pos, obj = r3_cover.JOBS[key]; g = G(job); bp = BedPart(tag, pos); S = g.S
    msk = g.part.copy()
    if obj is not None: msk &= S[:, 9] == obj
    PL = np.unique(S[msk, 7]).astype(int); sup = np.isin(g.F, [i for i, n in enumerate(g.names) if n in SUP]); isif = np.isin(g.F, [i for i, n in enumerate(g.names) if n == 'Support interface'])
    isbr = np.isin(g.F, [i for i, n in enumerate(g.names) if n in ('Bridge',)])
    items = []; prev = None
    for k, li in enumerate(PL):
        zt = float(g.L[li]); lh = zt - (float(g.L[PL[k - 1]]) if k else 0.0); zm = zt - lh / 2; Mo = bp.layer(zm)
        if prev is not None and not Mo.is_empty:
            O = opening(Mo.difference(prev.buffer(0.45, quad_segs=3)), 0.2, qs=3)
            for p in polys_of(O):
                if p.area < amin: continue
                zb = zt - lh; b = p.bounds
                near = (np.minimum(S[:, 0], S[:, 2]) < b[2] + 1) & (np.maximum(S[:, 0], S[:, 2]) > b[0] - 1) & (np.minimum(S[:, 1], S[:, 3]) < b[3] + 1) & (np.maximum(S[:, 1], S[:, 3]) > b[1] - 1)
                def cov(m):
                    s = S[m]
                    if not len(s): return 0.0
                    co = np.stack([s[:, 0:2], s[:, 2:4]], axis=1).astype(float)
                    return shapely.union_all(shapely.buffer(shapely.linestrings(co), s[:, 6].astype(float) / 2 + 0.15, quad_segs=3)).intersection(p).area / p.area
                below = near & (S[:, 4] > zb - 0.45) & (S[:, 4] <= zb + 1e-3)
                c_sup = cov(below & sup); c_if = cov(below & isif); c_br = cov(near & (S[:, 7] == li) & isbr & msk)
                items.append(dict(li=int(li), zb=zb, lh=lh, p=p, area=p.area, sup=c_sup, ifc=c_if, bridge=c_br))
        prev = Mo
    uf = UF(); by = {}
    for i, it in enumerate(items): by.setdefault(it['li'], []).append(i); uf.find(i)
    lis = sorted(by)
    for a, li in enumerate(lis):
        ids = by[li]
        for x in range(len(ids)):
            for y in range(x + 1, len(ids)):
                if items[ids[x]]['p'].distance(items[ids[y]]['p']) < 1.5: uf.union(ids[x], ids[y])
        if a and PL[np.searchsorted(PL, li) - 1] == lis[a - 1]:
            pr = by[lis[a - 1]]; tree = STRtree([items[i]['p'] for i in pr])
            for i in ids:
                for j in tree.query(items[i]['p'].buffer(1.0)):
                    if items[i]['p'].distance(items[pr[j]]['p']) < 1.0: uf.union(i, pr[j])
    groups = {}
    for i in range(len(items)): groups.setdefault(uf.find(i), []).append(i)
    rows = []
    for r, ids in groups.items():
        A = sum(items[i]['area'] for i in ids); bb = np.array([items[i]['p'].bounds for i in ids]); zs = [items[i]['zb'] for i in ids]
        w = bp.to_world([[bb[:, 0].min(), bb[:, 1].min(), min(zs)], [bb[:, 2].max(), bb[:, 3].max(), max(zs)]])
        rows.append(dict(area=round(A, 1), nlayers=len(set(items[i]['li'] for i in ids)), z=[round(min(zs), 2), round(max(zs), 2)], sup=round(sum(items[i]['area'] * items[i]['sup'] for i in ids) / A, 2),
                         ifc=round(sum(items[i]['area'] * items[i]['ifc'] for i in ids) / A, 2), bridge=round(sum(items[i]['area'] * items[i]['bridge'] for i in ids) / A, 2),
                         wlo=[round(float(v), 1) for v in w.min(0)], whi=[round(float(v), 1) for v in w.max(0)]))
    rows.sort(key=lambda r: -r['area'])
    json.dump(rows, open('/home/claude/r3/data/overhang_%s.json' % key, 'w'))
    tot = sum(r['area'] for r in rows); ts = sum(r['area'] * r['sup'] for r in rows)
    print('%s (%s): faces looking at the bed (beyond 0.45 per layer): %.0f mm2 in %d groups; %.0f mm2 (%.0f%%) over support' % (key, job, tot, len(rows), ts, 100 * ts / tot if tot else 0))
    n = 0
    for r in rows:
        if r['sup'] > cover_max or n >= show: continue
        n += 1
        print('   %7.1f mm2, %2d layers, bed z %.1f..%.1f | world x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f | support %3.0f%% (interface %3.0f%%) | printed as bridge %3.0f%%' % (
            r['area'], r['nlayers'], r['z'][0], r['z'][1], r['wlo'][0], r['whi'][0], r['wlo'][1], r['whi'][1], r['wlo'][2], r['whi'][2], 100 * r['sup'], 100 * r['ifc'], 100 * r['bridge']))
if __name__ == '__main__':
    key = sys.argv[1]; run(key, amin=float(sys.argv[2]) if len(sys.argv) > 2 else 1.0, cover_max=float(sys.argv[3]) if len(sys.argv) > 3 else 1.01)
