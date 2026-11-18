"""recheck3: checks on the final recommended slices: (1) support inside the four post insert holes (before / after the blockers), (2) the lands, pegs and other
bed-facing faces still on support, (3) the screen plate's support by place, (4) the adhesion test piece's low posts."""
import sys, json, math, numpy as np
from r3_gq import *
from r3_under import under, SUP
C12, S12 = math.cos(math.radians(12)), math.sin(math.radians(12))
def slab_to_world(x, up, d): return np.array([x, -d * C12 - up * S12, 143.3 - d * S12 + up * C12])
HOLES = (('top post, viewer left', 70, 27, 12.8), ('top post, viewer right', -70, 27, 12.8), ('bottom post, viewer left', 85, -82, 11.6), ('bottom post, viewer right', -85, -82, 11.6))
def in_hole(g, bp, x, up, d0, r=1.9, zmax=None):
    """Volume of support lines whose midpoint lies inside the hole's cylinder (radius r about the axis, mouth to blind end)."""
    a = bp.to_bed(slab_to_world(x, up, d0))[0]; b = bp.to_bed(slab_to_world(x, up, d0 + 6.35))[0]; ax = (b - a) / np.linalg.norm(b - a); L = np.linalg.norm(b - a)
    S = g.S; sup = np.isin(g.F, [i for i, n in enumerate(g.names) if n in SUP])
    P = np.stack([(S[:, 0] + S[:, 2]) / 2, (S[:, 1] + S[:, 3]) / 2, S[:, 4] - 0.1], axis=1).astype(float) - a
    t = P @ ax; rad = np.linalg.norm(P - np.outer(t, ax), axis=1); m = sup & (t > 0) & (t < L) & (rad < r)
    if zmax is not None: m &= S[:, 4] <= zmax + 1e-3
    ln = np.hypot(S[m, 2] - S[m, 0], S[m, 3] - S[m, 1]); return float((ln * S[m, 6] * 0.2).sum()), int(m.sum()), (float(t[m].max()) if m.any() else 0.0)
if __name__ == '__main__':
    what = sys.argv[1]
    if what == 'shell':
        bp = BedPart('shell', (0, -30, 0))
        for job in ('H4_P3a_w4', 'F4_P3a'):
            g = G(job); print(job, '| support in total %.0f mm3' % sum(v for k, v in volbox(g, (-1e3, 1e3, -1e3, 1e3), -1, 1e3, part=False).items() if k in SUP))
            for nm, x, up, d0 in HOLES:
                v, n, t = in_hole(g, bp, x, up, d0); print('   support inside the insert hole, %-26s %6.2f mm3 in %4d lines, reaching %.2f mm into the hole' % (nm, v, n, t))
            under(g, bp, [65, -19.5, 161], [75, -16.5, 172], label='   top post land, viewer left')
            under(g, bp, [-75, -19.5, 161], [-65, -16.5, 172], label='   top post land, viewer right')
            under(g, bp, [79, 2.5, 54], [91, 6.2, 66.5], label='   bottom post land and peg, viewer left')
            under(g, bp, [-91, 2.5, 54], [-79, 6.2, 66.5], label='   bottom post land and peg, viewer right')
            under(g, bp, [78, 0.5, 52], [94, 4.4, 76], label='   bottom post buttress front + strut, viewer left')
            under(g, bp, [-45, -63.4, 138], [45, -55.3, 158.5], label='   lip at the top of the arch')
            under(g, bp, [-86, -34, 112], [-62, -5, 143], label='   radar pocket and its brace')
    if what == 'adh':
        bp = BedPart('shell', (0, -30, 0))
        for job in ('H0_adh_w4', 'F0_adh'):
            g = G(job); print(job, '| support in total %.0f mm3' % sum(v for k, v in volbox(g, (-1e3, 1e3, -1e3, 1e3), -1, 1e3, part=False).items() if k in SUP))
            for nm, x, up, d0 in HOLES[2:]:
                v, n, t = in_hole(g, bp, x, up, d0, zmax=8.0); print('   support inside the insert hole, %-26s %6.2f mm3 in %4d lines' % (nm, v, n))
    if what == 'plate':
        bp = BedPart('screen', (0, 0, 0))
        for job in ('H3_P3b_tree_if', 'F3_P3b'):
            g = G(job); S = g.S; sup = np.isin(g.F, [i for i, n in enumerate(g.names) if n in SUP]); isif = np.isin(g.F, [i for i, n in enumerate(g.names) if n == 'Support interface'])
            print(job, '| layers with support: tops', sorted(set(np.round(S[sup, 4], 2).tolist())))
            L1 = bp.layer(0.1); L8 = bp.layer(1.5); B = L8.difference(L1.buffer(0.01))           # the raised border = section at 1.5 minus the first layer's island
            holes = [shapely.geometry.Polygon(r) for p in polys_of(L1) for r in p.interiors if 40 < shapely.geometry.Polygon(r).area < 100]
            def foot_of(m, grow=0.0):
                s = S[m]
                if not len(s): return MultiPolygon()
                co = np.stack([s[:, 0:2], s[:, 2:4]], axis=1).astype(float); return shapely.union_all(shapely.buffer(shapely.linestrings(co), s[:, 6].astype(float) / 2 + grow, quad_segs=3))
            Fs = foot_of(sup); Fi = foot_of(isif & (S[:, 4] > 0.7)); Bb = polys_of(B)
            print('   raised border %.1f mm2 in %d pieces; support footprint %.1f mm2, of it under the border %.1f, in the pocket and slot %.1f, elsewhere %.1f' % (
                B.area, len(Bb), Fs.area, Fs.intersection(B).area, sum(Fs.intersection(h).area for h in holes), Fs.difference(unary_union([B] + holes)).area))
            print('   top interface layer covers %.0f%% of the border (lines grown 0.15)' % (100 * foot_of(isif & (S[:, 4] > 0.7), 0.15).intersection(B).area / B.area))
            e = Fs.difference(unary_union([B.buffer(0.3)] + holes))
            for p in sorted(polys_of(e), key=lambda p: -p.area)[:6]:
                if p.area > 1: print('      support outside the border: %.1f mm2 at bed x %.1f..%.1f y %.1f..%.1f' % ((p.area,) + tuple(np.array(p.bounds)[[0, 2, 1, 3]])))
