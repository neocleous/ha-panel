"""recheck3: does each part print as modelled? Layer by layer, the model's section against the printed footprint (lines drawn with their width).
  missing = model minus printed (voids enclosed by printed walls, i.e. sparse infill, are counted as printed), opened by a disc of r 0.12 (so the 0.1 hole compensation, the 0.15 first-layer compensation and line-end
            rounding drop out): material the slicer leaves out (walls under a line, closed-up thin features);
  extra   = printed minus the model grown by 0.15, opened by r 0.10: plastic where the model has none (bridged or filled gaps).
Regions that overlap in consecutive layers are joined. Usage: r3_cover.py <key> ...   (keys in JOBS)"""
import sys, json, time, numpy as np
from r3_gq import *
from fdm_lib import UF, opening
from shapely.strtree import STRtree
JOBS = {'door_thin': ('H7_P6_thin', 'door', (0, 0, 0), None), 'shell': ('H4_P3a_w4', 'shell', (0, -30, 0), None), 'shell_w2': ('H4_P3a_w2', 'shell', (0, -30, 0), None), 'screen': ('H3_P3b_nosup', 'screen', (0, 0, 0), None),
        'door': ('H7_P6', 'door', (0, 0, 0), None), 'cap': ('H6_P4', 'cap', (0, -28, 0), 0), 'grommet': ('H6_P4', 'grommet', (0, 52, 0), 1),
        'base': ('H1s_P1_solid', 'base', (0, 75, 0), 0), 'spkbox_L': ('H1s_P1_solid', 'spkbox_L', (-50, -72, 0), 1), 'spkbox_R': ('H1s_P1_solid', 'spkbox_R', (50, -72, 0), 2),
        'carrier': ('H2_P2', 'carrier', (-38, 0, 0), 0), 'cradle': ('H2_P2', 'cradle', (47, -38, 0), 1), 'clip_L': ('H2_P2', 'clip_L', (37, 0, 0), 2), 'clip_R': ('H2_P2', 'clip_R', (57, 0, 0), 3),
        'bme_hood': ('H2_P2', 'bme_hood', (47, 42, 0), 4), 'slab': ('H5_P5s', 'slab', (34, 0, 0), None)}
OUT = '/home/claude/r3/data'; os.makedirs(OUT, exist_ok=True)

def run(key):
    t0 = time.time(); job, tag, pos, obj = JOBS[key]; g = G(job); bp = BedPart(tag, pos)
    S = g.S; msk = g.part.copy()
    if obj is not None: msk &= S[:, 9] == obj
    b = bp.m.bounds; win = (b[0][0] - 1, b[1][0] + 1, b[0][1] - 1, b[1][1] + 1)
    items = {'missing': [], 'extra': []}; tot = {'model': 0.0, 'printed': 0.0, 'missing': 0.0, 'extra': 0.0}
    PL = np.unique(S[msk, 7]).astype(int)          # the layers that carry this part's lines
    for k, li in enumerate(PL):
        zt = float(g.L[li]); lh = zt - (float(g.L[PL[k - 1]]) if k else 0.0); zm = zt - lh / 2
        if zm > b[1][2] + 0.01: break
        Mo = bp.layer(zm)
        m = msk & (S[:, 7] == li); s = S[m]
        if len(s):
            co = np.stack([s[:, 0:2], s[:, 2:4]], axis=1).astype(float)
            P = shapely.union_all(shapely.buffer(shapely.linestrings(co), s[:, 6].astype(float) / 2.0, quad_segs=3))
        else: P = MultiPolygon()
        tot['model'] += Mo.area * lh; tot['printed'] += P.area * lh
        # printed footprint with its enclosed voids filled: sparse infill inside closed walls is not a missing feature
        # a void of the print that lies wholly inside the model's material is an infill void: fill it; a void that reaches a hole of the model stays open
        if not P.is_empty and not Mo.is_empty:
            Min = Mo.buffer(-0.05, quad_segs=3); fills = []
            for p in polys_of(P):
                for r in p.interiors:
                    H = shapely.geometry.Polygon(r)
                    if Min.contains(H): fills.append(H)
            Pf = unary_union([P] + fills) if fills else P
        else: Pf = P
        mis = opening(Mo.difference(Pf), 0.12, qs=3) if not Mo.is_empty else MultiPolygon()
        ext = opening(P.difference(Mo.buffer(0.15, quad_segs=3)), 0.10, qs=3) if not P.is_empty else MultiPolygon()
        for k, gm in (('missing', mis), ('extra', ext)):
            for p in polys_of(gm):
                if p.area >= 0.03: items[k].append((li, zm, lh, p)); tot[k] += p.area * lh
    out = {'key': key, 'job': job, 'layers': int(len(PL)), 'tot_mm3': {k: round(v, 1) for k, v in tot.items()}}
    for k in ('missing', 'extra'):
        uf = UF(); L = items[k]; by = {}
        for i, it in enumerate(L): by.setdefault(it[0], []).append(i); uf.find(i)
        for li in sorted(by):
            if li - 1 in by:
                prev = by[li - 1]; tree = STRtree([L[i][3] for i in prev])
                for i in by[li]:
                    for j in tree.query(L[i][3].buffer(0.1)):
                        if L[i][3].distance(L[prev[j]][3]) < 0.1: uf.union(i, prev[j])
        groups = {}
        for i in range(len(L)): groups.setdefault(uf.find(i), []).append(i)
        rows = []
        for r, ids in groups.items():
            vol = sum(L[i][3].area * L[i][2] for i in ids)
            if vol < 0.05: continue
            bb = np.array([L[i][3].bounds for i in ids]); zs = [L[i][1] for i in ids]
            lo = bp.to_world([[bb[:, 0].min(), bb[:, 1].min(), min(zs)]])[0]; hi = bp.to_world([[bb[:, 2].max(), bb[:, 3].max(), max(zs)]])[0]
            wmin = np.minimum(lo, hi); wmax = np.maximum(lo, hi)
            rows.append(dict(vol=round(vol, 2), nlayers=len(set(L[i][0] for i in ids)), layers=[int(min(L[i][0] for i in ids)) + 1, int(max(L[i][0] for i in ids)) + 1],
                             amax=round(max(sum(L[i][3].area for i in ids if L[i][0] == l) for l in set(L[i][0] for i in ids)), 2),
                             bed=[round(float(v), 2) for v in (bb[:, 0].min(), bb[:, 1].min(), bb[:, 2].max(), bb[:, 3].max())], z=[round(min(zs), 2), round(max(zs), 2)],
                             wmin=[round(float(v), 1) for v in wmin], wmax=[round(float(v), 1) for v in wmax]))
        rows.sort(key=lambda r: -r['vol']); out[k] = rows
    json.dump(out, open(os.path.join(OUT, 'cover_%s.json' % key), 'w'))
    print('%-9s %-14s layers %d | model %.0f printed %.0f mm3 (%.1f%%) | missing %.1f mm3 in %d regions | extra %.1f mm3 in %d regions | %.0f s' % (
        key, job, len(PL), tot['model'], tot['printed'], 100 * tot['printed'] / tot['model'], tot['missing'], len(out['missing']), tot['extra'], len(out['extra']), time.time() - t0), flush=True)

if __name__ == '__main__':
    for k in sys.argv[1:]: run(k)
