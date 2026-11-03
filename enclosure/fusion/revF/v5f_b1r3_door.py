# rev F block 1r-3 (2026-11-03): new DOOR_F inside the floor ring = outer generator floor section offset 6.8
# (ring opening 6.5 + gap 0.3): chin line y 0.7, front vertical corners R5.2, z 0..2.5. The b1 door is DOOR_F_b1 (hidden).
# Probes: front / back edge at XC, gap door edge -> ring along the local normal at z 1.25 (expect 0.3), plate z range.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
RAYS = {'side_y-30': (XC + 80.0, -30.0, 0.9584, -0.2855), '+x_y-7.66': (XC + 80.0, -7.66, 1.0, 0.0),
        '-x_y-7.66': (XC - 80.0, -7.66, -1.0, 0.0), 'front_XC': (XC, -10.0, 0.0, 1.0), 'back_XC': (XC, -70.0, 0.0, -1.0)}


def run(_context):
    X = Ctx()
    out = {}
    try:
        if X.body('DOOR_F') is not None:
            raise RuntimeError('DOOR_F exists - run v5f_b1r1 first')
        door, YC, rc = outline_body(X, 6.8, 0.0, 2.5, 'DOOR_F')
        out['vol_cm3'] = round(door.volume, 3); out['rc'] = rc; out['chin_y'] = round(YC - 6.8, 3)
        hb = X.body('HOUSING_E')

        def along(b, x, y, z, nx, ny, a, c, it=30):
            for _ in range(it):
                m = (a + c) / 2
                if X.inside(b, x + nx * m, y + ny * m, z): a = m
                else: c = m
            return a

        g = {}
        for k, (x, y, nx, ny) in RAYS.items():
            e = along(door, x, y, 1.25, nx, ny, 0.0, 40.0)                       # door edge
            lo, hi = e, e + 1.5                                                  # gap -> ring
            for _ in range(30):
                m = (lo + hi) / 2
                if X.inside(hb, x + nx * m, y + ny * m, 1.25): hi = m
                else: lo = m
            g[k] = {'door_edge': (round(x + nx * e - XC, 3), round(y + ny * e, 3)), 'gap': round(hi - e, 3)}
        out['edges_and_gaps'] = g
        out['plate'] = {'z0.1': X.inside(door, XC, -40.0, 0.1), 'z2.4': X.inside(door, XC, -40.0, 2.4),
                        'z2.6_open': not X.inside(door, XC, -40.0, 2.6)}
        out['interf'] = X.interference(door, [hb, X.body('SLAB_frame'), X.body('LCD_glass'), X.body('PI5_F')])
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b1r3_door', 'DOOR_F inset 6.8', out)
    print(json.dumps(out))
