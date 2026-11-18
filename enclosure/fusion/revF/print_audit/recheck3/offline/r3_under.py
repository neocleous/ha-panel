"""recheck3: what lies under a named face that looks at the bed. For a world box: per layer the part of the model's section inside the box that reaches more than `step`
beyond the layer below, its area, and the share with support / interface lines in the 0.45 under it, and the share printed as bridge or overhang wall."""
import sys, json, numpy as np
from r3_gq import *
from fdm_lib import opening
SUP = ('Support', 'Support interface', 'Support transition')
def under(g, bp, wlo, whi, step=0.25, obj=None, label='', quiet=False):
    c = bp.to_bed([wlo, whi]); lo = c.min(0); hi = c.max(0); W = box(lo[0], lo[1], hi[0], hi[1]); S = g.S
    sup = np.isin(g.F, [i for i, n in enumerate(g.names) if n in SUP]); isif = np.isin(g.F, [i for i, n in enumerate(g.names) if n == 'Support interface'])
    isbr = np.isin(g.F, [i for i, n in enumerate(g.names) if n == 'Bridge']); isov = np.isin(g.F, [i for i, n in enumerate(g.names) if n == 'Overhang wall'])
    msk = g.part.copy()
    if obj is not None: msk &= S[:, 9] == obj
    near = (np.minimum(S[:, 0], S[:, 2]) < hi[0] + 1) & (np.maximum(S[:, 0], S[:, 2]) > lo[0] - 1) & (np.minimum(S[:, 1], S[:, 3]) < hi[1] + 1) & (np.maximum(S[:, 1], S[:, 3]) > lo[1] - 1)
    PL = [int(l) for l in np.unique(S[msk, 7]) if lo[2] - 0.21 <= g.L[int(l)] <= hi[2] + 0.21]
    tot = dict(area=0.0, sup=0.0, ifc=0.0, br=0.0, ov=0.0); rows = []
    for li in PL:
        lh = g.lh_of(li); zt = float(g.L[li]); zm = zt - lh / 2; zb = zt - lh
        Mo = bp.layer(zm); Pr = bp.layer(zm - lh)
        O = opening(Mo.difference(Pr.buffer(step, quad_segs=3)).intersection(W), 0.08, qs=3) if not Mo.is_empty else MultiPolygon()
        if O.is_empty or O.area < 0.05: continue
        def cov(m, grow=0.15):
            s = S[m]
            if not len(s): return 0.0
            co = np.stack([s[:, 0:2], s[:, 2:4]], axis=1).astype(float)
            return shapely.union_all(shapely.buffer(shapely.linestrings(co), s[:, 6].astype(float) / 2 + grow, quad_segs=3)).intersection(O).area / O.area
        below = near & (S[:, 4] > zb - 0.45) & (S[:, 4] <= zb + 1e-3); here = near & (S[:, 7] == li) & msk
        r = dict(z=zb, area=O.area, sup=cov(below & sup), ifc=cov(below & isif), br=cov(here & isbr, 0.0), ov=cov(here & isov, 0.0)); rows.append(r)
        for k in ('sup', 'ifc', 'br', 'ov'): tot[k] += r[k] * r['area']
        tot['area'] += r['area']
    if tot['area'] > 0:
        for k in ('sup', 'ifc', 'br', 'ov'): tot[k] /= tot['area']
    if not quiet:
        print('%-58s %7.1f mm2 over %2d layers (bed z %s) | support under %3.0f%% (interface %3.0f%%) | printed as bridge %3.0f%%, overhang wall %3.0f%%' % (
            label, tot['area'], len(rows), ('%.1f..%.1f' % (rows[0]['z'], rows[-1]['z'])) if rows else '-', 100 * tot['sup'], 100 * tot['ifc'], 100 * tot['br'], 100 * tot['ov']))
    return tot, rows
if __name__ == '__main__':
    POS = (0, -30, 0); bp = BedPart('shell', POS)
    for job in ('H4_P3a_w4',):
        g = G(job); print(job)
        under(g, bp, [-45, -63.4, 138], [45, -55.3, 158.5], label='lip at the top of the arch, inner face (x -45..45)')
        under(g, bp, [45, -63.4, 100], [72, -55.3, 140], label='lip, shoulder, viewer left (x 45..72, z 100..140)')
        under(g, bp, [60, -63.4, 8], [80, -55.3, 100], label='lip, side, viewer left (z 8..100)')
        under(g, bp, [-80, -63.4, 8], [-60, -55.3, 100], label='lip, side, viewer right (z 8..100)')
        under(g, bp, [64.5, -28.0, 168.7], [78.0, -19.8, 172.5], label='fill under the roof ledge, viewer left top post')
        under(g, bp, [-78.0, -28.0, 168.7], [-64.5, -19.8, 172.5], label='fill under the roof ledge, viewer right top post')
        under(g, bp, [-48.5, 4.4, 48.7], [48.5, 6.0, 50.6], label="cloth groove's roof (the web), x -48..48")
        under(g, bp, [-86, -34, 112], [-62, -5, 143], label='radar pocket and its brace (viewer right)')
        under(g, bp, [-85, -55.6, 4], [85, -54.9, 160], label='seat floor ring at y -55.2', step=0.1)
        under(g, bp, [65, -19.5, 161], [75, -16.5, 172], label='top post land, viewer left')
        under(g, bp, [79, 2.5, 54], [91, 6.2, 66.5], label='bottom post land and peg, viewer left')
        under(g, bp, [-91, 2.5, 54], [-79, 6.2, 66.5], label='bottom post land and peg, viewer right')
        under(g, bp, [78, 0.5, 52], [94, 4.4, 76], label='bottom post buttress front face + strut, viewer left')
