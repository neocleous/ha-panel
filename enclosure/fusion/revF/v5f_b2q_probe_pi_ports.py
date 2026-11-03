# rev F block 2q (2026-11-03), read-only: Pi 5 connector outlines from PI5_F vertices (after the -0.7 x shift) and the
# room behind them, for the checkpoint-2 USB-pocket and USB-C notes (run with readOnly true).
# 1. +x end: vertices beyond x_rel 42.0, clustered by y (gap > 2) -> RJ45 y -55.8..-39.8; USB stacks y -36.3..-21.6 and
#    -18.3..-3.7, z 10.3..25.9, faces x_rel 45.1..45.2. Port cavities from z line scans at x_rel 43.5: lower port shell
#    z 11.2..16.6 (tongue 14.0..15.6), upper 19.6..25.0 (tongue 22.6..24.0).
# 2. back edge: vertices beyond y -56.5 above the PCB top (z > 9.3), clustered by x -> USB-C x_rel -36.3..-27.6,
#    z 9.4..12.6, face y -59.3; micro-HDMI 0 / 1 x_rel -21.0..-13.8 / -7.6..-0.4, face y -59.7.
# 3. inner back wall (first solid of HOUSING_E going back from y -56, 0.1 steps) behind the USB-C: y -79.3 (x_rel -36.3)
#    .. -80.9 (-27.6) at z 9.4..16 -> 20.0..21.6 mm of plug room.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback


def clusters(pts, axis, gap):
    vals = sorted(set(q[axis] for q in pts))
    cl = []; cur = [vals[0]]
    for v in vals[1:]:
        if v - cur[-1] > gap: cl.append(cur); cur = [v]
        else: cur.append(v)
    cl.append(cur)
    res = []
    for c in cl:
        sel = [q for q in pts if c[0] <= q[axis] <= c[-1]]
        res.append({'x_rel': [min(q[0] for q in sel), max(q[0] for q in sel)], 'y': [min(q[1] for q in sel), max(q[1] for q in sel)],
                    'z': [min(q[2] for q in sel), max(q[2] for q in sel)], 'n': len(sel)})
    return res


def run(_context):
    X = Ctx(); out = {}
    try:
        pi = X.body('PI5_F'); hb = X.body('HOUSING_E')
        end, back = set(), set()
        for v in pi.vertices:
            p = v.geometry
            q = (round(p.x * 10 - XC, 1), round(wy(p), 1), round(wz(p), 1))
            if q[0] > 42.0: end.add(q)
            if q[1] < -56.5 and q[2] > 9.3: back.add(q)
        out['plus_x_end_by_y'] = clusters(end, 1, 2.0)
        out['back_edge_by_x'] = clusters(back, 0, 1.5)

        def first(xr, z, y0=-56.0, y1=-95.0, st=0.1):
            for i in range(int((y0 - y1) / st) + 1):
                y = y0 - i * st
                if X.inside(hb, XC + xr, y, z): return round(y, 2)
        out['inner_back_wall_y'] = {'%g,%g' % (xr, z): first(xr, z) for xr in (-36.3, -31.95, -27.6) for z in (9.4, 11.0, 12.6, 16.0)}
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    print(json.dumps(out))
