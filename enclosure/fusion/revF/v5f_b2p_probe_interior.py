# rev F block 2 prep (2026-11-03), read-only: interior extents for the speaker chambers (logged).
# INNER_E half-widths (+x / -x from XC) at y 4 / -10 / -30 / -45 for z 8 / 28 / 51 / 77; inner front surface y (chin inner
# face below z 48, reclined slot wall above) at x_rel 47.5 / 70.5 / 93.5 for z 6..77; inner back wall at XC.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback


def run(_context):
    X = Ctx(); out = {}
    try:
        inner = X.body('INNER_E')
        def edge(b, p0, d, a, c, it=20):
            for _ in range(it):
                m = (a + c) / 2
                if X.inside(b, p0[0] + d[0] * m, p0[1] + d[1] * m, p0[2] + d[2] * m): a = m
                else: c = m
            return round((a + c) / 2, 2)
        hw = {}
        for z in (8, 28, 51, 77):
            hw[z] = {y: (edge(inner, (XC, y, z), (1, 0, 0), 0, 120), edge(inner, (XC, y, z), (-1, 0, 0), 0, 120)) for y in (4, -10, -30, -45)}
        out['inner_halfwidth_+x_-x'] = hw
        fr = {}
        for z in (6, 28, 48, 51, 60, 77):
            fr[z] = {xr: round(-20 + edge(inner, (XC + xr, -20, z), (0, 1, 0), 0, 60), 2) for xr in (47.5, 70.5, 93.5)}
        out['inner_front_y_+x'] = fr
        out['inner_back_y_XC'] = {z: round(-30 - edge(inner, (XC, -30, z), (0, -1, 0), 0, 80), 2) for z in (8, 77)}
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b2p_probe_interior', 'interior extents', out)
    print(json.dumps(out))
