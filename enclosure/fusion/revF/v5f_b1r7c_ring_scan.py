# rev F block 1r-7c (2026-11-03), read-only: ring / door scan round the +x half of the floor outline (mirror-symmetric).
# Per site (generator-section point and outward normal from /home/claude/work/door_outline.py): P0 = REF_E_outer surface
# at z 8 along the normal; then along -n at z 1.25: ring opening edge u_ring, door edge u_door, gap; wall at z 8; bend
# thickness along the 45 deg bisector from (u 6, z 6). u is measured from P0 (the actual outer surface).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
SITES = [(99.922, -0.236, 0.9997, -0.0252), (99.531, -8.273, 0.9972, -0.075), (98.676, -16.236, 0.9901, -0.1407),
         (97.258, -24.05, 0.9759, -0.2183), (95.155, -31.801, 0.9518, -0.3066), (91.485, -41.136, 0.9048, -0.4258),
         (86.66, -49.8, 0.8376, -0.5462), (80.582, -57.79, 0.7496, -0.6619), (73.428, -64.791, 0.6461, -0.7633),
         (65.432, -70.656, 0.535, -0.8448), (56.619, -75.459, 0.4218, -0.9067), (47.328, -79.133, 0.3147, -0.9492),
         (37.724, -81.779, 0.2183, -0.9759), (0.0, -85.0, 0.0, -1.0)]


def run(_context):
    X = Ctx()
    out = {'rows': []}
    try:
        ref = X.body('REF_E_outer'); hb = X.body('HOUSING_E'); door = X.body('DOOR_F')

        def along(b, x, y, z, nx, ny, a, c, it=28):          # a: inside b, c: outside (distance along (nx, ny))
            for _ in range(it):
                m = (a + c) / 2
                if X.inside(b, x + nx * m, y + ny * m, z): a = m
                else: c = m
            return (a + c) / 2

        h = math.sqrt(0.5)
        for (xr, y0, nx, ny) in SITES:
            gx = XC + xr
            t = along(ref, gx, y0, 8.0, nx, ny, -10.0, 10.0)
            px, py = gx + nx * t, y0 + ny * t
            ins = lambda b, u, z: X.inside(b, px - nx * u, py - ny * u, z)
            u_ring = 5.0 + along(hb, px - nx * 5.0, py - ny * 5.0, 1.25, -nx, -ny, 0.0, 3.0)
            lo, hi = u_ring, u_ring + 2.0                      # door entry
            for _ in range(28):
                m = (lo + hi) / 2
                if ins(door, m, 1.25): hi = m
                else: lo = m
            u_door = (lo + hi) / 2
            wall = along(hb, px, py, 8.0, -nx, -ny, 1.25, 4.0)
            def bis(a, c):
                for _ in range(28):
                    m = (a + c) / 2
                    if ins(hb, 6.0 - m * h, 6.0 - m * h) == ins(hb, 6.0 - a * h, 6.0 - a * h): a = m
                    else: c = m
                return (a + c) / 2
            ri = bis(2.5, 4.75); ro = bis(4.75, 7.0)
            out['rows'].append({'site': (xr, y0), 'P0_shift': round(t, 3), 'u_ring': round(u_ring, 3), 'u_door': round(u_door, 3),
                                'gap': round(u_door - u_ring, 3), 'wall_z8': round(wall, 3), 'bend_t': round(ro - ri, 3),
                                'flat_top': round(u_ring - (2.5 + 3.5), 3)})
        R = out['rows']
        out['summary'] = {k: (min(r[k] for r in R), max(r[k] for r in R)) for k in ('u_ring', 'u_door', 'gap', 'wall_z8', 'bend_t', 'flat_top', 'P0_shift')}
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b1r7c_ring_scan', 'ring scan', out)
    print(json.dumps(out))
