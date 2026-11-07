"""Main-board outline study (2026-11-07): one run that reproduces every figure in the report.

Inputs: e1b meshes (board_zone/mesh) and the d22 front (print_audit/exports/front_d22.stl), staged from the Mac.
Prints: free region at the current plane, the two outlines (T, PMAX) with areas, front/back zones, clearances to the
meshes, leads in front, bracket contact; the plane-move table. Writes plane_cur.npz and main_board_outline_2026-11-07.png.
"""
import numpy as np, bz, sys
sys.path.insert(0, '.')
from scipy import ndimage
from plane import analyze, NAMES, LNAMES
from outlines import C0, T, PMAX, HOLES, kicad
X, Z = np.meshgrid(bz.XS, bz.ZS); A = bz.H**2

R = analyze()
np.savez('plane_cur.npz', **R)
from evalpoly import evaluate, mask            # reads plane_cur.npz
import exact
YB, YF = -65.0, -63.4
box = (np.array([-80, -90, 0]), np.array([80, -40, 135]))
GROUPS = {
    'door sweep (door material in front of y -65)': (['HOUSING_F_door'], lambda P: P[:, 1] > YB),
    'front shell in the slab': (['front_d22'], lambda P: (P[:, 1] > YB) & (P[:, 1] < YF)),
    'K5 LCD-screw lanes in the slab': (['KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR'], lambda P: (P[:, 1] > YB) & (P[:, 1] < YF)),
    'cap-key lanes in the slab': (['KO_capkey_BL', 'KO_capkey_BR', 'KO_capkey_SL', 'KO_capkey_SR'], lambda P: (P[:, 1] > YB) & (P[:, 1] < YF)),
    'Pi-power plug, adapter, cable in the slab': (['PIPWR_a_env', 'LEAD_PI_POWER'], lambda P: (P[:, 1] > YB) & (P[:, 1] < YF)),
    'cradle, PD board, pigtail keep-out in the slab': (['CRADLE_5807', 'PD_5807_env', 'KO_5807_pigtail'], lambda P: (P[:, 1] > YB) & (P[:, 1] < YF)),
}
cache = {}
def exact_report(poly):
    for g, (bodies, sel) in GROUPS.items():
        best = (np.inf, None, None)
        for b in bodies:
            if b not in cache:
                cache[b] = exact.samples(exact.FRONT if b == 'front_d22' else exact.M + b + '.stl', 0.25, box)
            P = cache[b]; P = P[sel(P)]
            d, p = exact.clearance(poly, P)
            if d < best[0]: best = (d, p, b)
        print('     %-46s %6.2f mm at %s (%s)' % (g, best[0], None if best[1] is None else np.round(best[1], 1), best[2]))

def zones(poly):
    m = mask(poly); hf = R['hf'] - 0.5; hb = np.minimum(R['hb_door'], R['hb_fixed'])
    def bb(q): return 'x %.1f..%.1f z %.1f..%.1f (%.0f mm2)' % (X[q].min()-.25, X[q].max()+.25, Z[q].min()-.25, Z[q].max()+.25, q.sum()*A)
    lab, n = ndimage.label(m & (hf < 28))
    for i in range(1, n + 1):
        q = lab == i
        print('     front < 28: %s, %.1f..%.1f, by %s' % (bb(q), hf[q].min(), hf[q].max(), sorted(set(NAMES[w] for w in R['fwho'][q] if w >= 0))))
    lab, n = ndimage.label(m & (hb < 3.4))
    for i in range(1, n + 1):
        q = lab == i
        if q.sum() * A >= 2:
            print('     back < 3.4 (bare only): %s, min %.2f, by %s' % (bb(q), hb[q].min(), 'door' if np.all(R['hb_door'][q] <= R['hb_fixed'][q]) else sorted(set(NAMES[w] for w in R['bwho'][q] if w >= 0 and R['hb_fixed'][q].min() < 3.4))))
    q = m & (R['hbr'] < 2)
    print('     bracket within 2 mm in front: %.0f mm2 (bosses in contact; gussets 0.9)' % (q.sum() * A))

print('free region at the current plane (1.0 lateral clearance): %.0f mm2' % (R['inside'].sum() * A))
for name, poly in (('today 90 x 50', C0), ('T', T), ('PMAX', PMAX)):
    evaluate(poly, name)
    exact_report(poly)
    zones(poly)
    print('     KiCad (x_board = 45 - x_rel, y_board = 84 - z):', kicad(poly))

print('\nplane moves: free area within |x| <= 45 above z 34 with front >= 6 and back >= 1 (connected to the base)')
def metric(Rm):
    ins = Rm['inside']; hb = np.minimum(Rm['hb_door'], Rm['hb_fixed']); hf = Rm['hf'] - 0.5
    ok = ins & (hb >= 1.0) & (hf >= 6) & (Z >= 34) & (np.abs(X) <= 45)
    ok |= ins & (Z >= 34) & (Z <= 35) & (X > 17.8) & (X < 32.2)          # J2 mouth line (designed contact)
    lab, n = ndimage.label(ok)
    reg = lab == lab[np.argmin(np.abs(bz.ZS - 60)), np.argmin(np.abs(bz.XS))]
    tz = lambda x: bz.ZS[reg[:, np.argmin(np.abs(bz.XS - x))]].max() + 0.25
    return reg.sum() * A, tz(0), tz(25), tz(-40)
for YFm, tilt, lab_ in ((-67.4, 0, '4 mm back'), (-65.4, 0, '2 mm back'), (-63.4, 0, 'current'), (-61.4, 0, '2 mm forward'),
                        (-59.4, 0, '4 mm forward'), (-63.4, -3, 'tilt 3 deg top back'), (-63.4, 3, 'tilt 3 deg top forward'),
                        (-63.4, 6, 'tilt 6 deg top forward')):
    a, t0, t25, tm40 = metric(R if (YFm, tilt) == (-63.4, 0) else analyze(YF=YFm, tilt_deg=tilt))
    print('   %-24s %6.0f mm2   top z at x 0 / 25 / -40: %5.1f / %5.1f / %5.1f' % (lab_, a, t0, t25, tm40))
