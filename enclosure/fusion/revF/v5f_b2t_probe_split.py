# rev F block 2t (2026-11-03), read-only (run with readOnly true): removable-back study. Opening = INNER_E section at a
# vertical split plane y_s (-55 / -60): half-widths vs z and the inner back at XC; cover = HOUSING_E behind y_s (volume,
# mass in ASA 1.05 g/cm3); LCD-screw key entry points where the K5 lanes reach y -55, tested inside the opening.
# Result 2026-11-03:
#   y -55: opening half-width 79.4 (z 3), 78.4 (20), 76.4 (40), 73.6 (60), 70.5 (76), 63.9 (100), 55.8 (120), 42.3 (140),
#          30.9 (150), 21.7 (155), closed at z 160 (inner back at XC: -54.76 at z 160); cover 58.32 cm3 = 61.2 g ASA;
#          key entries LL/LR at z 91.6 (52.7 from the heads), UL/UR at z 118.2 (46.6), all inside the opening.
#   y -60: opening 74.7 (z 3) ... 23.1 (z 140), closed at z 150; cover 49.54 cm3; the UL lane meets the wall at
#          y -59.5 (b2i), i.e. in front of this plane -> y -60 does not clear the upper +x lane.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback


def run(_context):
    X = Ctx(); out = {}
    try:
        B = adsk.fusion.BooleanTypes
        ie = X.body('INNER_E'); hb = X.body('HOUSING_E')

        def hw(y, z, s):
            if not X.inside(ie, XC, y, z): return None
            a, c = 0.0, 110.0
            for _ in range(20):
                m = (a + c) / 2
                if X.inside(ie, XC + s * m, y, z): a = m
                else: c = m
            return round(a, 1)

        def back_y(z):
            a, c = -40.0, -95.0
            if not X.inside(ie, XC, a, z): return None
            for _ in range(22):
                m = (a + c) / 2
                if X.inside(ie, XC, m, z): a = m
                else: c = m
            return round(a, 2)
        out['inner_back_y_at_XC'] = {z: back_y(z) for z in (3, 40, 80, 120, 140, 150, 155, 160, 165, 170, 175)}
        for ys in (-55.0, -60.0):
            out['opening_halfwidth_y%g' % ys] = {z: (hw(ys, z, 1), hw(ys, z, -1)) for z in (3, 20, 40, 60, 76, 100, 120, 140, 150, 155, 160)}
            t = X.tbm.copy(hb)
            X.tbm.booleanOperation(t, X.wbox(-150, 150, -150, ys, -10, 250), B.IntersectionBooleanType)
            out['cover_cm3_y%g' % ys] = round(t.volume, 2)
            out['cover_g_ASA_y%g' % ys] = round(t.volume * 1.05, 1)
        a13, a37 = math.radians(13.0), math.radians(37.0)
        ent = {}
        for nm, xs, y0, z0, ang in (('LL', 47.5, -3.66, 79.72, a13), ('LR', -47.5, -3.66, 79.72, a13),
                                    ('UL', 47.5, -17.80, 146.23, -a37), ('UR', -47.5, -17.80, 146.23, -a37)):
            t = (y0 + 55.0) / math.cos(abs(ang))
            z = z0 + t * math.sin(ang)
            ent[nm] = {'t_to_plane': round(t, 1), 'z_at_y-55': round(z, 1), 'inside_opening': X.inside(ie, xs, -55.0, z)}
        out['k5_key_entry_at_y-55'] = ent
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    print(json.dumps(out))
