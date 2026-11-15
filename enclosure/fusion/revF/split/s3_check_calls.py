# rev F split (2026-11-15), block 3: checks on version 64 (g19). All read-only; results as printed in the session.
# Uses the rev 3.2 pass's modules still in Fusion: r32.k4 (v5f_k4a_unit_checks.py, its own v5f_k instance), r32.res['m62'] (the measured
# reference = version 63's 76 pairs), r32a (audit-asm/followup/aud4_lib.py: ride_setup(), ride()). See README lessons 181-182 on their caches.
import adsk.core, adsk.fusion, sys, time, math


def matrix64(_context):                               # every unit body against every other (96 bodies, 4,560 pairs); call until left == 0
    k = sys.modules['v5f_k']; X = k.K(); r = sys.modules['r32']
    r.k4['k'].budget(45.0); k.budget(45.0)             # the namespace has its own v5f_k instance: set ITS deadline
    res, left, n = r.k4['matrix'](X, 'v64')
    print(n, len(res), left, len({q: v for q, v in res.items() if v}))       # 96 4560 0 76


def matrix_diff(_context):
    r = sys.modules['r32']; kk = r.k4['k']
    sym = lambda d: {tuple(sorted(q)): v for q, v in d.items() if v}
    a = sym(r.res['m62']); b = sym(kk.c[('k4m', 'v64')])
    print(len(a), len(b), {q: a[q] for q in a if q not in b}, {q: b[q] for q in b if q not in a},
          {q: (a[q], b[q]) for q in a if q in b and abs(a[q] - b[q]) > 0.05})                 # 76 76 {} {} {}


def ride64(_context):                                 # the audit's ride-in, 45 moving pieces x 23 positions, shell AND screen plate fixed
    k = sys.modules['v5f_k']; X = k.K(); a4 = sys.modules['r32a']; R = a4.R
    a4.k.budget(45.0); k.budget(45.0)
    if not R.get('ride64b_ready'):
        for q in ('ride_mov', 'ride_fix', ('crop', 'rideS'), ('crop', 'rideP'), ('tl', 'HOUSING_F_front'), ('tl', 'HOUSING_F_plate'), 'ride64'):
            R.pop(q, None)                             # tl() caches copies by NAME: the old one-piece shell would be used otherwise
        a4.ride_setup(X)
        a4.crop(X, 'HOUSING_F_plate', 'rideP', (-100, 100, 4, 80, -80, 30), 'S')
        R['ride_fix'] = R['ride_fix'] + a4.items(X, crops=['rideP'])
        R['ride64b_ready'] = True
    left = a4.ride(X, time.time(), lim=45.0, tag='ride64')
    # 1035 results, 0 left, 0 touching. Nearest: plate 0.08 (part of LEAD_GPIO_A1, 12 out: the notch floors), shell 1.223
    # (part of LEAD_USB_RESP, 0.5 out), SPKBOX_L 4.642 (MAIN_conn, 0.5 out)


def a_checks(_context):                               # A1-A3
    k = sys.modules['v5f_k']; X = k.K()
    P = X.body('HOUSING_F_plate'); R = X.body('HOUSING_F_front')
    back = sum(f.area * 100.0 for f in P.faces if f.geometry.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType
               and abs(-f.pointOnFace.y * 10.0 - 12.8) < 0.01 and abs(abs(f.geometry.normal.y) - 1.0) < 1e-6)
    a2 = X.cp(R); X.sec(a2, X.wbox(-120.0, 120.0, 6.81, 60.0, -5.0, 200.0))
    a3 = X.cp(R); X.sec(a3, X.dbox(-106.0, 106.0, -5.0, 12.99, -101.0, 46.0))
    print(round(back, 1), round(X.vol(a2), 3), round(X.vol(a3), 2), [l[0] for l in X.lumps(a3)])
    # 16935.8 (one face; plate d 6.4..12.8) | 0.0 | 101.0 [40.801, 40.801, 9.7, 9.7]: the four lands and two pegs only


def key_lines(_context):                              # D7: the 2.0 key (r 1.15, 100 long) from each moved head, 6 / 10 / 14 deg toward the middle
    k = sys.modules['v5f_k']; X = k.K(); k.budget(50.0)
    names = [b.name for b in k.current(X, leads=True)]
    for side, g, p0, sb in (('left', 1.0, (58.5, -0.77, 80.0), -6.62 + 3.168), ('right', -1.0, (-58.6, -0.43, 80.0), -6.964 + 3.168)):
        u = (g * 0.17365, 0.98481, 0.0); s = sb - 1.65
        h = (p0[0] + u[0] * s, p0[1] + u[1] * s, 80.0)
        for ph in (6.0, 10.0, 14.0):
            dv = (-g * math.sin(math.radians(ph)), -math.cos(math.radians(ph)), 0.0)
            key = X.cyl((h[0] + dv[0] * 0.3, h[1] + dv[1] * 0.3, 80.0), (h[0] + dv[0] * 100.0, h[1] + dv[1] * 100.0, 80.0), 1.15)
            print(side, ph, k.clash(X, key, names))
    # only HOUSING_F_door (off at the step) on both sides at 6, 10, 14 deg; left at 14 deg also LEAD_USB_RESP 10.74 (as before the change)


def masses(_context):                                 # D9: volumes and centres (world) of the changed bodies; 1.05 g/cm3 in the report
    k = sys.modules['v5f_k']; X = k.K()
    for n in ('HOUSING_F_front_v63', 'HOUSING_F_front', 'HOUSING_F_plate', 'SPKBOX_L_v63', 'SPKBOX_L', 'SPKBOX_R_v63', 'SPKBOX_R', 'FLOOR_PLATE_v63', 'FLOOR_PLATE'):
        pp = X.body(n).getPhysicalProperties(adsk.fusion.CalculationAccuracy.HighCalculationAccuracy)
        print(n, round(pp.volume * 1000.0, 2), [round(v, 3) for v in k.W(pp.centerOfMass)])
    # front_v63 200372.37 (-2.681, -15.669, 97.632); front 104459.98 (-3.590, -24.923, 82.360); plate 68255.48 (-1.704, -5.231, 116.333)
    # L 26053.04 -> 26086.45; R 26764.59 -> 26806.05; base 32457.88 -> 32456.12 (high-accuracy volumes; guard volumes are the temporary-body ones)
