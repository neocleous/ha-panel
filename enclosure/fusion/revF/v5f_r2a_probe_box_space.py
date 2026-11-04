# rev F rework R2a (2026-11-04), read-only: the space the separate speaker boxes must fit (+x side; the housing is
# symmetric about XC, the -x side is checked on the built boxes).
# 1. INNER_E wall x_rel at y -3.7 ... -55.15, z 3 ... 76 (taper of the side wall behind the speaker).
# 2. Clear opening at the split (y -55.15): first front-shell solid going outward from x_rel 50 (lip / root band / wall).
# 3. Floor and cove: first solid going down at 0.5 ... 8 mm inboard of the wall, y -5 ... -50.
# 4. Chin side: first front-shell solid going forward from y -3.0 at the frame corners, the axis, above the frame.
# 5. Solid runs along +y at the inboard frame holes (x_rel 52.75, z 10.25 / 45.75) from y 0 to 20 (insert depth).
# 6. Bodies and front-shell material in slabs z 72...84 over x_rel 44...100, y -56...2 (how high the box can go).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback


def bis(f, a, c, it=20):
    for _ in range(it):
        m = (a + c) / 2
        if f(m): a = m
        else: c = m
    return round((a + c) / 2, 2)


def first_true(f, a, b, st):
    v = a
    while v <= b + 1e-9:
        if f(v):
            if v == a: return round(a, 2)
            return bis(lambda t: not f(t), v - st, v, 12)
        v += st
    return None


def segs(f, a, b, st):
    out = []; cur = None; v = a
    while v <= b + 1e-9:
        s = f(v)
        if s and cur is None: cur = v
        if not s and cur is not None: out.append([round(cur, 2), round(v - st, 2)]); cur = None
        v += st
    if cur is not None: out.append([round(cur, 2), round(b, 2)])
    return out


def wbbox_z(b):
    bb = b.boundingBox; mn = bb.minPoint; mx = bb.maxPoint
    zs = [wz(P3(x, y, z)) for x in (mn.x, mx.x) for y in (mn.y, mx.y) for z in (mn.z, mx.z)]
    ys = [wy(P3(x, y, z)) for x in (mn.x, mx.x) for y in (mn.y, mx.y) for z in (mn.z, mx.z)]
    return min(zs), max(zs), min(ys), max(ys), mn.x * 10, mx.x * 10


def run(_context):
    X = Ctx(); out = {}
    try:
        B = adsk.fusion.BooleanTypes
        ie = X.body('INNER_E'); fb = X.body('HOUSING_F_front')
        YS = [-3.7, -10.0, -20.0, -30.0, -40.0, -50.0, -52.5, -55.15]
        ZS = [3.0, 4.5, 6.0, 10.0, 20.0, 28.0, 40.0, 51.0, 60.0, 70.0, 74.0, 76.0]
        wall = {}
        for y in YS:
            row = []
            for z in ZS:
                row.append(bis(lambda m: X.inside(ie, XC + m, y, z), 0.0, 120.0) if X.inside(ie, XC, y, z) else None)
            wall[str(y)] = row
        out['wall_x'] = {'z': ZS, 'by_y': wall}
        log('v5f_r2a_probe_box_space', 'wall', out['wall_x'])
        ZO = [4.0, 6.0, 8.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 51.0, 55.0, 60.0, 65.0, 70.0, 74.0, 76.0, 78.0]
        out['opening_x_at_y-55.15'] = {str(z): first_true(lambda m: X.inside(fb, XC + m, -55.15, z), 50.0, 100.0, 0.5) for z in ZO}
        out['front_x_at_y-52.5'] = {str(z): first_true(lambda m: X.inside(fb, XC + m, -52.5, z), 50.0, 100.0, 0.5) for z in ZO}
        log('v5f_r2a_probe_box_space', 'opening', {k: out[k] for k in ('opening_x_at_y-55.15', 'front_x_at_y-52.5')})
        cove = {}
        for y in (-5.0, -20.0, -35.0, -50.0):
            w6 = bis(lambda m: X.inside(ie, XC + m, y, 6.0), 0.0, 120.0)
            cove[str(y)] = {'wall_z6': w6}
            for d in (0.5, 1.5, 3.0, 5.0, 8.0):
                x = XC + w6 - d
                cove[str(y)][str(d)] = bis(lambda z: not X.inside(fb, x, y, z), 15.0, 1.0)
        out['floor_top_z_inboard_of_wall'] = cove
        chin = {}
        for xr in (47.5, 52.75, 70.0, 88.25):
            for z in (3.5, 6.0, 10.25, 28.0, 45.75, 51.0, 55.0, 62.0, 70.0, 75.0):
                chin['%g,%g' % (xr, z)] = first_true(lambda y: X.inside(fb, XC + xr, y, z), -3.0, 25.0, 0.5)
        out['chin_first_solid_y'] = chin
        out['runs_y_at_inboard_holes'] = {str(z): segs(lambda y: X.inside(fb, XC + 52.75, y, z), 0.0, 20.0, 0.25) for z in (10.25, 45.75)}
        log('v5f_r2a_probe_box_space', 'cove chin', {k: out[k] for k in ('floor_top_z_inboard_of_wall', 'chin_first_solid_y', 'runs_y_at_inboard_holes')})
        names = [b.name for b in X.comp.bRepBodies]
        cand = [n for n in names if n.startswith('LCD_')] + ['SLAB_frame', 'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR', 'PI5_F',
                                                            'PI5_F_cooler', 'GPIO_plugA_env', 'GPIO_plugB_env', 'KO_K7_fan', 'TOUCH_PCB', 'KO_touch_back', 'SPK_L']
        SL = [(72.0, 74.0), (74.0, 76.0), (76.0, 78.0), (78.0, 80.0), (80.0, 84.0)]
        slabs = {}
        for n in cand:
            b = X.body(n)
            if b is None: continue
            z0, z1, y0, y1, x0, x1 = wbbox_z(b)
            if z1 < 72.0 or z0 > 84.0 or y0 > 2.0 or y1 < -56.0 or x1 < XC + 44.0 or x0 > XC + 100.0:
                continue
            r = {}
            for (a, c) in SL:
                t = X.tbm.copy(b)
                X.tbm.booleanOperation(t, X.wbox(XC + 44.0, XC + 100.0, -56.0, 2.0, a, c), B.IntersectionBooleanType)
                v = round(t.volume * 1000, 2)
                if v > 0: r['%g-%g' % (a, c)] = v
            if r: slabs[n] = r
        fi = X.tbm.copy(fb); X.tbm.booleanOperation(fi, X.tbm.copy(ie), B.IntersectionBooleanType)
        r = {}
        for (a, c) in SL:
            t = X.tbm.copy(fi)
            X.tbm.booleanOperation(t, X.wbox(XC + 44.0, XC + 100.0, -56.0, 2.0, a, c), B.IntersectionBooleanType)
            r['%g-%g' % (a, c)] = round(t.volume * 1000, 2)
        slabs['front_shell_inside_cavity'] = r
        out['slabs_mm3'] = slabs
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_r2a_probe_box_space', 'probe', out)
    print(json.dumps(out))
