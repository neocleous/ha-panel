# rev F audit-response d4b-1 (2026-11-06), read-only: exact geometry for the door / grommet / cradle edits (audit findings
#   2, 7, 8, 9, 32, 33) before writing them. Writes ~/Documents/HA_panel_renders/d_data/data/d4b1_probe.json.
#   1. guard volumes; 2. cylindrical faces (r <= 4.5): grommet, cradle, door near the inlet / bosses, front near the cradle;
#   3. section loops: cradle z 11.0 / 15.2 / 16.8, front z 5.0, door z 3.0 / 3.5 (bottom flange), door x 0 above the cutout;
#   4. door planar faces normal to world z between z 2.7 and 3.7; 5. wall entry / exit and cloth face at the old (x ±15.6) and
#   new (x ±15.85) pin measuring lines, above the cutout and at the grommet flange; 6. containment scans: grommet flange
#   thickness (top, bottom, side), cradle bezel top.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
exec(open(os.path.expanduser('~/Documents/HA_panel_renders/scripts_d/v5f_d0_sections.py')).read())   # sections(), clip(), rdp()
import traceback
OUTF = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d4b1_probe.json')
GUARD = {'HOUSING_F_door': 51.101, 'GROMMET_usbc_F': 0.4889, 'CRADLE_5807': 2.1564, 'HOUSING_F_front': 236.1678}
PLANES1 = {
    'C_z11': ('z', 11.0, (-14.0, 14.0, -86.0, -56.0), ['CRADLE_5807', 'HOUSING_F_front']),
    'C_z15.2': ('z', 15.2, (-14.0, 14.0, -86.0, -56.0), ['CRADLE_5807', 'GROMMET_usbc_F', 'HOUSING_F_door']),
    'C_z16.8': ('z', 16.8, (-14.0, 14.0, -86.0, -56.0), ['CRADLE_5807', 'GROMMET_usbc_F', 'HOUSING_F_door']),
    'F_z5': ('z', 5.0, (-14.0, 14.0, -86.0, -62.0), ['HOUSING_F_front', 'CRADLE_5807']),
    'D_z3.0': ('z', 3.0, (-90.0, 90.0, -92.0, -50.0), ['HOUSING_F_door', 'HOUSING_F_front']),
    'D_z3.5': ('z', 3.5, (-90.0, 90.0, -92.0, -50.0), ['HOUSING_F_door', 'HOUSING_F_front']),
    'D_x0_top': ('x', 0.0, (-90.0, -74.0, 22.0, 38.0), ['HOUSING_F_door', 'GROMMET_usbc_F', 'CRADLE_5807', 'PD_5807_env']),
    'D_x13.85': ('x', 13.85, (-90.0, -76.0, 8.0, 36.0), ['HOUSING_F_door', 'GROMMET_usbc_F']),
}


def wpt(p):
    return [round(p.x * 10 - XC, 3), round(wy(p), 3), round(wz(p), 3)]


def cyls(b, filt=None, rmax=4.5):
    rows = []
    for f in b.faces:
        g = f.geometry
        if g.objectType != adsk.core.Cylinder.classType():
            continue
        r = g.radius * 10
        if r > rmax:
            continue
        ax = g.axis; ax.normalize(); o = g.origin
        ts = [((v.geometry.x - o.x) * ax.x + (v.geometry.y - o.y) * ax.y + (v.geometry.z - o.z) * ax.z) * 10 for v in f.vertices] or [0.0]
        t0, t1 = min(ts), max(ts); tm = (t0 + t1) / 2
        c = P3(o.x + ax.x * tm / 10, o.y + ax.y * tm / 10, o.z + ax.z * tm / 10)
        cw = wpt(c)
        if filt and not filt(cw):
            continue
        p = f.pointOnFace; ok, n = f.evaluator.getNormalAtPoint(p)
        k = (p.x - o.x) * ax.x + (p.y - o.y) * ax.y + (p.z - o.z) * ax.z
        q = P3(o.x + ax.x * k, o.y + ax.y * k, o.z + ax.z * k)
        hole = V3(p.x - q.x, p.y - q.y, p.z - q.z).dotProduct(n) < 0
        zs = [wz(v.geometry) for v in f.vertices] or [cw[2]]
        ys = [wy(v.geometry) for v in f.vertices] or [cw[1]]
        rows.append([round(2 * r, 3), 'hole' if hole else 'boss', [round(v, 3) for v in nw_of(ax)], cw, round(t1 - t0, 3),
                     [round(min(ys), 3), round(max(ys), 3)], [round(min(zs), 3), round(max(zs), 3)], round(f.area * 100, 2)])
    return rows


def zfaces(b, z0, z1):
    rows = []
    for f in b.faces:
        g = f.geometry
        if g.objectType != adsk.core.Plane.classType():
            continue
        n = nw_of(g.normal)
        if abs(n[2]) < 0.999:
            continue
        ok, nn = f.evaluator.getNormalAtPoint(f.pointOnFace)
        sgn = 1 if nw_of(nn)[2] > 0 else -1
        z = wz(f.pointOnFace)
        if not (z0 <= z <= z1):
            continue
        xs = [v.geometry.x * 10 - XC for v in f.vertices]; ys = [wy(v.geometry) for v in f.vertices]
        rows.append([round(z, 3), sgn, round(f.area * 100, 2), [round(min(xs), 2), round(max(xs), 2), round(min(ys), 2), round(max(ys), 2)]])
    return sorted(rows)


def scan(b, x, z, y0, y1, step=0.05, axis='y'):
    """solid intervals of body b along a line (world), as [[a, b], ...] at the given step."""
    res = []; cur = None; n = int(round((y1 - y0) / step))
    for i in range(n + 1):
        t = y0 + i * step
        p = (XC + x, t, z) if axis == 'y' else (XC + x, z, t)
        s = X_.inside(b, *p)
        if s and cur is None:
            cur = [round(t, 3), round(t, 3)]
        elif s:
            cur[1] = round(t, 3)
        elif cur is not None:
            res.append(cur); cur = None
    if cur is not None:
        res.append(cur)
    return res


def run(_context):
    global X_
    X = Ctx(); X_ = X; out = {}; t0 = time.time()
    try:
        out['guard'] = {k: round(X.body(k).volume, 4) if X.body(k) else None for k in GUARD}
        out['guard_ok'] = all(X.body(k) is not None and abs(X.body(k).volume - v) <= 0.0005 for k, v in GUARD.items())
        # 2. cylinders
        out['cyl'] = {
            'GROMMET_usbc_F': cyls(X.body('GROMMET_usbc_F')),
            'CRADLE_5807': cyls(X.body('CRADLE_5807')),
            'HOUSING_F_door': cyls(X.body('HOUSING_F_door'), lambda c: abs(c[0]) <= 60 and -90 <= c[1] <= -60 and 0 <= c[2] <= 35),
            'HOUSING_F_front': cyls(X.body('HOUSING_F_front'), lambda c: abs(c[0]) <= 60 and -86 <= c[1] <= -62 and 0 <= c[2] <= 12),
        }
        out['t_cyl'] = round(time.time() - t0, 1)
        # 4. door faces normal to z near the bottom
        out['door_zfaces'] = zfaces(X.body('HOUSING_F_door'), 2.7, 3.7)
        # 5. ray runs
        rr = {}
        for (k, x, z) in (('pin_old_L', 15.6, 20.6), ('pin_old_R', -15.6, 20.6), ('pin_new_L', 15.85, 20.6), ('pin_new_R', -15.85, 20.6),
                          ('top_x0_z29.5', 0.0, 29.5), ('top_x0_z31', 0.0, 31.0), ('top_x0_z32.5', 0.0, 32.5),
                          ('top_x0_z33.5', 0.0, 33.5), ('top_x11_z31', 11.0, 31.0), ('top_x13.5_z31.5', 13.5, 31.5),
                          ('bot_x0_z12', 0.0, 12.0), ('side_x14_z25', 14.0, 25.0)):
            o = (XC + x, -100.0, z)
            ref = [round(-100.0 + h[0], 3) for h in ray_hits(X, o, (0, 1, 0), ('REF_F_outer',))][:2]
            rr[k] = {'cloth_face_y': ref, 'door_runs': solid_runs(X, o, (0, 1, 0), 'HOUSING_F_door', 30.0),
                     'grommet_runs': solid_runs(X, o, (0, 1, 0), 'GROMMET_usbc_F', 30.0)}
        out['rays'] = rr
        out['t_rays'] = round(time.time() - t0, 1)
        # 6. scans
        g = X.body('GROMMET_usbc_F'); cb = X.body('CRADLE_5807')
        out['scan'] = {'g_x0_z29.5_y': scan(g, 0.0, 29.5, -86.5, -80.0), 'g_x0_z12_y': scan(g, 0.0, 12.0, -86.5, -80.0),
                       'g_x14_z20.6_y': scan(g, 14.0, 20.6, -86.5, -78.0), 'g_x13.6_z20.6_y': scan(g, 13.6, 20.6, -86.5, -78.0),
                       'g_x0_y-84.9_z': scan(g, 0.0, -84.9, 8.0, 34.0, axis='z'), 'g_x0_y-83_z': scan(g, 0.0, -83.0, 8.0, 34.0, axis='z'),
                       'c_x0_y-83_z': scan(cb, 0.0, -83.0, 12.0, 30.0, axis='z'), 'c_x0_y-84.55_z': scan(cb, 0.0, -84.55, 12.0, 30.0, axis='z'),
                       'door_x0_y-83_z': scan(X.body('HOUSING_F_door'), 0.0, -83.0, 2.0, 36.0, axis='z')}
        out['wbb'] = {n: [round(v, 3) for v in wbb(X, X.body(n))] for n in ('GROMMET_usbc_F', 'CRADLE_5807', 'PD_5807_env', 'KO_5807_pigtail')
                      if X.body(n) is not None}
        out['t_scan'] = round(time.time() - t0, 1)
        # 3. sections (last: the slowest)
        out['sec'] = sections(X, PLANES1)
        out['t_s'] = round(time.time() - t0, 1)
        os.makedirs(os.path.dirname(OUTF), exist_ok=True)
        json.dump(out, open(OUTF, 'w'))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    short = {k: out.get(k) for k in ('guard', 'guard_ok', 't_cyl', 't_rays', 't_scan', 't_s', 'FAIL')}
    log('v5f_d4b1_probe', 'probe', short)
    print(json.dumps(short, separators=(',', ':')))
