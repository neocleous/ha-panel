# rev F i1b (2026-11-11): step 3 repeated, block 1 - main board rev 3.1 placed at its site in place of rev 3.
#   Source: the solids of i1a (cache). Frame and grouping as h1b (STEP X = u, Y = v, Z 0 = the back face at depth 31.1):
#   MAIN_pcb, MAIN_PS1, MAIN_conn, MAIN_tall, MAIN_low, MAIN_plug_env. MAIN_PS1_tol (the module's top millimetre) and MAIN_J2_plug_env
#   (the Pi power plug below the edge) are not in the STEP files and stay as they are: neither part moved.
#   Dry by default: volumes, lumps and boxes beside rev 3's, the board's holes read from its cylinder faces, overlap of each new body
#   with every current body except the six rev 3 bodies (the front shell as its crop to the site; results kept in the cache, so a
#   second call continues). APPLY=True: the six rev 3 bodies -> <name>_v50 (hidden), the new ones added with the old ones' appearance
#   and visibility.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_i_lib.py'), encoding='utf-8').read())
APPLY = globals().get('APPLY', False)
OLD = ['MAIN_pcb', 'MAIN_PS1', 'MAIN_conn', 'MAIN_tall', 'MAIN_low', 'MAIN_plug_env']
CONN = {'J9': (-43.3, -34.7, -29.0, -22.1), 'J1': (-4.3, 4.3, -29.0, -22.1), 'J6': (9.4, 16.3, -29.0, -15.4), 'J2': (16.3, 27.0, -29.6, -19.2),
        'J8': (34.5, 43.0, -29.0, -22.1), 'J5': (-43.3, -36.3, -20.6, -7.1), 'J10': (-32.3, -28.5, -19.8, -8.4), 'J11': (-6.4, 5.0, -14.9, -11.1)}
GRP = {'pcb': 'MAIN_pcb', 'PS1': 'MAIN_PS1', 'conn': 'MAIN_conn', 'tall': 'MAIN_tall', 'low': 'MAIN_low', 'plugs': 'MAIN_plug_env'}


def group(box):
    x0, x1, y0, y1, z0, z1 = box
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    if x1 - x0 > 80.0:
        return 'pcb'
    if z1 > 25.0 or z0 < -2.5:
        return 'PS1'
    for k, (a, b, c, d) in CONN.items():
        if a <= cx <= b and c <= cy <= d:
            return 'conn'
    if z1 > 6.0 or z0 < -1.0:
        return 'tall'
    return 'low'


def run(_context):
    st = {'apply': APPLY}
    t0 = time.time()
    try:
        X = K()
        c = cache()
        if 'step_board' not in c:
            raise RuntimeError('run i1a first')
        if 'MAIN_pcb_v50' in X.names():
            raise RuntimeError('already applied')
        m = adsk.core.Matrix3D.create()
        m.setWithArray([1, 0, 0, -0.005, 0, 0, -1, -3.11, 0, 1, 0, -2.745, 0, 0, 0, 1])
        grp = {}; cnt = {}; fail = []
        for path, box, tb in c['step_board'] + [[p, None, t] for p, b, t in c['step_plugs']]:
            g = group(box) if box else 'plugs'
            t = X.cp(tb); X.tbm.transform(t, m)
            cnt[g] = cnt.get(g, 0) + 1
            if g not in grp:
                grp[g] = t; continue
            try:
                X.tbm.booleanOperation(grp[g], t, BT.UnionBooleanType)
            except Exception:
                fail.append([g, path[-40:]])
        if fail:
            raise RuntimeError('union failed: %s' % fail)
        new = {GRP[g]: t for g, t in grp.items()}
        st['count'] = cnt
        st['new'] = {k: [round(X.vol(v), 1), v.lumps.count] + bbb(v) for k, v in new.items()}
        st['rev3'] = {n: [round(X.vol(X.body(n)), 1), X.body(n).lumps.count] + bbb(X.body(n)) for n in OLD}
        holes = []
        for f in new['MAIN_pcb'].faces:
            gm = f.geometry
            if gm.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType and abs(gm.radius * 10 - 1.6) < 0.01:
                o = Bf(gm.origin); holes.append([round(o[0], 2), round(o[1], 2)])
        st['holes dia 3.2'] = sorted(set(tuple(h) for h in holes))
        status3('i1b', st)
        if not APPLY:
            if 'crop_front_site' not in c:
                t = X.cp(tcopy(X, 'HOUSING_F_front')); X.sec(t, X.dbox(U0 - 62, U0 + 62, -30, 75, V0 - 47, V0 + 47)); c['crop_front_site'] = t
            res = c.setdefault('i1b_clash', {})
            for b in current(X, leads=True):
                if b.name in OLD or b.name in res:
                    continue
                if time.time() - t0 > 35.0:
                    st['partial'] = True; break
                big = None; row = {}
                for k, v in new.items():
                    if not v.boundingBox.intersects(b.boundingBox):
                        continue
                    if big is None:
                        big = c['crop_front_site'] if b.name == 'HOUSING_F_front' else tcopy(X, b.name)
                    a = xvol(X, v, big)
                    if abs(a) > 0.005:
                        row[k[5:]] = round(a, 2)
                res[b.name] = row
            st['checked'] = len(res)
            st['clash'] = {k: v for k, v in res.items() if v}
        else:
            old = {n: X.body(n) for n in OLD}
            added = []
            for k, v in new.items():
                b = X.root.bRepBodies.add(v)
                b.name = 'NEW_' + k
                try:
                    b.appearance = old[k].appearance
                except Exception:
                    pass
                added.append([b, k, old[k].isLightBulbOn])
            for n in OLD:
                X.retire(old[n], '_v50')
            for b, k, vis in added:
                b.name = k
                b.isLightBulbOn = vis
            st['purged'] = purge()
            st['added'] = {'dups': X.dups(), 'bodies': X.root.bRepBodies.count, 'names': [k for b, k, vis in added],
                           'model': {k: [round(X.vol(X.body(k)), 1), X.body(k).lumps.count] + bbb(X.body(k)) for k in OLD}}
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('i1b_apply' if APPLY else 'i1b', st)


run(None)
