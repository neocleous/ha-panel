# rev F e6a (2026-11-09): read-only - V24, the lip magnets to an AliExpress size. Per magnet station: the door pocket's
#   D8.3 cylinder (axis = outward wall normal n, world), and along lines parallel to n, inward from 6 mm outside the
#   pocket: where the door and the front start and end (containment on local TemporaryBRep crops, 0.25 steps, bisected to
#   0.002). Lines: the axis; radius 2.0 and 4.0 inside the pocket (floor, skin, lap gap, pad face, lip pocket floor) at 4
#   angles; radius 4.45 just outside the pocket wall (outer surface = rim height, door wall) at 8 angles. Also KO_K5_* /
#   KO_capkey_* against the door. Writes e6/e6a_status.json.
import os, traceback
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py'), encoding='utf-8').read())
OUT = os.path.expanduser('~/Documents/HA_panel_renders/e6/e6a_status.json')
GUARD = {'HOUSING_F_front': 235.9107, 'HOUSING_F_door': 47.2633, 'HOUSING_F_cap': 9.9441, 'MAIN_BRACKET': 6.5563}
R_POCKET = 4.15
KO = ('KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR', 'KO_capkey_BL', 'KO_capkey_BR', 'KO_capkey_SL', 'KO_capkey_SR')
TMAX, STEP = 12.0, 0.25


def wpt(p):
    return (p.x * 10 - XC, wy(p), wz(p))


def transitions(body, q0, d, tmax=TMAX, step=STEP):
    """inside/outside changes of `body` along q0 + t d (world mm): [(t, entering)] with t bisected to 0.002"""
    ins = lambda t: body.pointContainment(Dw(*(q0[k] + d[k] * t for k in range(3)))) in INS
    out = []; prev = ins(0.0); t = 0.0
    while t < tmax:
        t1 = min(t + step, tmax); cur = ins(t1)
        if cur != prev:
            a, b = t, t1
            while b - a > 0.002:
                m = (a + b) / 2
                if ins(m) == prev:
                    a = m
                else:
                    b = m
            out.append([round((a + b) / 2, 3), cur])
        prev, t = cur, t1
    return out


def run(_context):
    st = {'t0': time.strftime('%H:%M:%S')}
    t0 = time.time()
    try:
        X = Ctx(); tbm = X.tbm
        st['version'] = [X.doc.dataFile.versionNumber, X.doc.isModified]
        bad = [[k, None if X.body(k) is None else round(X.body(k).volume, 4)] for k, v in GUARD.items()
               if X.body(k) is None or abs(X.body(k).volume - v) > 0.0005]
        st['guard_bad'] = bad
        if bad:
            raise RuntimeError('GUARD %s' % bad)
        door = X.body('HOUSING_F_door'); front = X.body('HOUSING_F_front')
        st['vis'] = {'door': door.isLightBulbOn, 'front': front.isLightBulbOn}
        cyl = []
        for f in door.faces:
            if f.geometry.objectType != adsk.core.Cylinder.classType():
                continue
            g = adsk.core.Cylinder.cast(f.geometry)
            if abs(g.radius * 10 - R_POCKET) > 0.005:
                continue
            a = g.axis.copy(); a.normalize(); aw = nw_of(a)
            if aw[1] > 0:                                   # outward normals point back (-y) at every station
                aw = (-aw[0], -aw[1], -aw[2])
            o = wpt(g.origin)
            vs = [wpt(v.geometry) for v in f.vertices]
            ts = [sum((v[k] - o[k]) * aw[k] for k in range(3)) for v in vs] or [0.0]
            cyl.append({'o': o, 'n': aw, 't': [min(ts), max(ts)], 'area': round(f.area * 100, 3), 'nv': len(vs)})
        st['n_cyl'] = len(cyl)
        stations = []
        for c in sorted(cyl, key=lambda c: (c['o'][0] > 0, c['o'][2])):
            n = c['n']; o = c['o']; top = max(c['t'])
            base = tuple(o[k] + n[k] * (top + 6.0) for k in range(3))
            dn = tuple(-n[k] for k in range(3))
            ctr = tuple(base[k] + dn[k] * 6.0 for k in range(3))
            crop = X.wbox(XC + ctr[0] - 12, XC + ctr[0] + 12, ctr[1] - 12, ctr[1] + 12, ctr[2] - 12, ctr[2] + 12)
            dq = tbm.copy(door); inter(X, dq, tbm.copy(crop))
            fq = tbm.copy(front); inter(X, fq, tbm.copy(crop))
            u = (n[1], -n[0], 0.0); ul = math.sqrt(u[0] ** 2 + u[1] ** 2) or 1.0; u = (u[0] / ul, u[1] / ul, 0.0)
            v = (n[1] * u[2] - n[2] * u[1], n[2] * u[0] - n[0] * u[2], n[0] * u[1] - n[1] * u[0])
            lines = {}
            for r, na in ((0.0, 1), (2.0, 4), (4.0, 4), (4.45, 8)):
                for k in range(na):
                    th = 2 * math.pi * k / na
                    q = tuple(base[i] + r * (math.cos(th) * u[i] + math.sin(th) * v[i]) for i in range(3))
                    lines['%.2f_%d' % (r, k)] = {'door': transitions(dq, q, dn), 'front': transitions(fq, q, dn)}
            stations.append({'o': [round(x, 3) for x in o], 'n': [round(x, 4) for x in n], 't_face': [round(x, 3) for x in c['t']],
                             'area_mm2': c['area'], 'base': [round(x, 3) for x in base], 'lines': lines,
                             't_s': round(time.time() - t0, 1)})
            st['stations'] = stations
            json.dump(st, open(OUT, 'w'), indent=1)
        st['ko_x_door_mm3'] = {k: vol_x(X, X.body(k), door) for k in KO if X.body(k) is not None}
        st['door_cm3_faces_lumps'] = [round(door.volume, 4), door.faces.count, door.lumps.count]
        st['done'] = True
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    st['t_s'] = round(time.time() - t0, 1)
    json.dump(st, open(OUT, 'w'), indent=1)
    print(json.dumps({k: st.get(k) for k in ('t_s', 'done', 'guard_bad', 'n_cyl', 'ko_x_door_mm3', 'FAIL')}))


run(None)
