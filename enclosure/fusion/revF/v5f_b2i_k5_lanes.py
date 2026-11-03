# rev F block 2i (2026-11-03): K5 LCD-screw access lanes as keep-out bodies KO_K5_{LL,LR,UL,UR} (D7).
# Heads now sit in the D6.5 x 1.0 pockets: seat d 13.8, DIN912 M3 head 3.0 -> key entry at d 16.8 on the screw axes
# (x +-47.5, Z ZS -+ 34): lower (y -3.66, z 79.72), upper (y -17.80, z 146.23). The screw axis (+d) points back and
# 12 deg down. Lower pair: rotated 25 deg up about x -> back and 13 deg up, length 100 (architect log 11-02: "the lower
# lanes run ... back and up at ~13 deg"). Upper pair: rotated 25 deg down -> back and 37 deg down, length 60.
# Reports interference of every lane with the housing, chambers, LCD, slab, Pi, cooler, GPIO envelopes, door, speakers,
# and where each lane first meets HOUSING_E (distance along the lane).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
ZS = -27.43


def run(_context):
    X = Ctx(); out = {}
    try:
        lanes = {}
        for nm, xs, Z, ang, L in (('LL', 47.5, ZS - 34.0, 13.0, 100.0), ('LR', -47.5, ZS - 34.0, 13.0, 100.0),
                                  ('UL', 47.5, ZS + 34.0, -37.0, 60.0), ('UR', -47.5, ZS + 34.0, -37.0, 60.0)):
            p0 = P3(xs / 10, -16.8 / 10, Z / 10)
            y0, z0 = wy(p0), wz(p0)
            a = math.radians(ang)
            y1, z1 = y0 - L * math.cos(a), z0 + L * math.sin(a)
            name = 'KO_K5_' + nm
            b = X.body(name)
            if b is None:
                b = X.add(X.tbm.createCylinderOrCone(Dw(xs, y0, z0), 0.35, Dw(xs, y1, z1), 0.35), name)
                b.isLightBulbOn = False
            lanes[nm] = (b, (xs, y0, z0), (xs, y1, z1))
            hb = X.body('HOUSING_E')
            t_hit = None
            for i in range(1, int(L * 4) + 1):
                t = i * 0.25
                f = t / L
                if X.inside(hb, xs, y0 + (y1 - y0) * f, z0 + (z1 - z0) * f):
                    t_hit = t; break
            out[nm] = {'start': (round(xs - XC, 2), round(y0, 2), round(z0, 2)), 'end': (round(xs - XC, 2), round(y1, 2), round(z1, 2)),
                       'axis_first_hits_housing_at_t': t_hit}
        names = [b.name for b in X.comp.bRepBodies]
        others = [X.body(n) for n in ('HOUSING_E', 'SLAB_frame', 'DOOR_F', 'PI5_F', 'PI5_F_cooler', 'GPIO_plugA_env', 'GPIO_plugB_env', 'SPK_L', 'SPK_R')] + \
                 [X.body(n) for n in names if n.startswith('LCD_')]
        for nm, (b, _, _) in lanes.items():
            r = X.interference(b, others)
            out[nm]['interf_nonzero'] = {k: v for k, v in r.items() if v > 0} or 'all 0'
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b2i_k5_lanes', 'K5 lanes', out)
    print(json.dumps(out))
