# rev F h1b (2026-11-11): step 3, block 1 - main board rev 3 placed at its site behind the display.
#   Source: the solids of h1a (cache). STEP frame -> board frame: u = X, v = Y, w = Z - 1.6 (site document section 0); design x = u - 0.05,
#   design y = -(31.1 + Z), design z = v - 27.45 (mm).
#   One body per group: MAIN_pcb (the board; 1.51 thick in the file), MAIN_PS1 (supply module and its 13 pins), MAIN_conn (five JST sockets,
#   two pin headers, the USB-C socket), MAIN_tall (C5, C6, C7, L1, the four amplifier coils, the cut lead ends), MAIN_low (the rest, 3.0 or
#   lower), MAIN_plug_env (the seven plug envelopes of the second file, 20 / 25 above the door-side face), MAIN_PS1_tol (the module's top
#   1.0 of tolerance, 27.5 -> 28.5), MAIN_J2_plug_env (Pi power plug below the bottom edge: 12.4 x 20 x 6.5 as before, on the socket's axis).
#   Dry by default: volumes, boxes, overlap with every current body (results kept in the cache, so a second call continues).
#   APPLY=True: the rev 2.1 bodies -> <name>_v47 (hidden), the new ones added.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_h_lib.py'), encoding='utf-8').read())
APPLY = globals().get('APPLY', False)
OLD = ['MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'MAIN_C7_env', 'KO_C7_vent', 'MAIN_J2_plug_env']
CONN = {'J9': (-43.3, -34.7, -29.0, -22.1), 'J1': (-4.3, 4.3, -29.0, -22.1), 'J6': (9.4, 16.3, -29.0, -15.4), 'J2': (16.3, 27.0, -29.6, -19.2),
        'J8': (34.5, 43.0, -29.0, -22.1), 'J5': (-43.3, -36.3, -20.6, -7.1), 'J10': (-36.2, -32.4, -19.8, -8.4), 'J11': (-6.4, 5.0, -13.9, -10.1)}
SHOW = {'MAIN_pcb': True, 'MAIN_PS1': True, 'MAIN_conn': True, 'MAIN_tall': True, 'MAIN_low': True, 'MAIN_plug_env': False, 'MAIN_PS1_tol': False,
        'MAIN_J2_plug_env': True}


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
            raise RuntimeError('run h1a first')
        if 'MAIN_pcb_v47' in X.names():
            raise RuntimeError('already applied')
        m = adsk.core.Matrix3D.create()
        m.setWithArray([1, 0, 0, -0.005, 0, 0, -1, -3.11, 0, 1, 0, -2.745, 0, 0, 0, 1])
        grp = {}; cnt = {}; extra = []
        for path, box, tb in c['step_board'] + [[p, None, t] for p, b, t in c['step_plugs']]:
            g = group(box) if box else 'plugs'
            t = X.cp(tb); X.tbm.transform(t, m)
            cnt[g] = cnt.get(g, 0) + 1
            if g not in grp:
                grp[g] = t; continue
            try:
                X.tbm.booleanOperation(grp[g], t, BT.UnionBooleanType)
            except Exception:
                extra.append([g, path[-40:], t])
        new = {'MAIN_pcb': grp['pcb'], 'MAIN_PS1': grp['PS1'], 'MAIN_conn': grp['conn'], 'MAIN_tall': grp['tall'], 'MAIN_low': grp['low'],
               'MAIN_plug_env': grp['plugs'], 'MAIN_PS1_tol': bbox_b(X, -37.11, 13.79, -4.35, 7.75, 27.495, 28.5),
               'MAIN_J2_plug_env': bbox_b(X, 21.625 - 6.2, 21.625 + 6.2, -48.95, -28.95, 1.72 - 3.25, 1.72 + 3.25)}
        for i, (g, pth, t) in enumerate(extra):
            new['MAIN_%s_x%d' % (g, i)] = t
        st['count'] = cnt; st['union_fail'] = [e[:2] for e in extra]
        st['new'] = {k: [round(X.vol(v), 1), v.lumps.count] + bbb(v) for k, v in new.items()}
        st['t_build'] = round(time.time() - t0, 1); status3('h1b', st)
        if not APPLY:
            res = c.setdefault('h1b_clash', {})
            for b in current(X, leads=True):
                if b.name in OLD or b.name in res:
                    continue
                if time.time() - t0 > 40.0:
                    st['partial'] = True; break
                big = None; row = {}
                for k, v in new.items():
                    if not v.boundingBox.intersects(b.boundingBox):
                        continue
                    if big is None:
                        big = tcopy(X, b.name)
                    a = xvol(X, v, big)
                    if abs(a) > 0.005:
                        row[k[5:]] = round(a, 2)
                res[b.name] = row
            st['checked'] = len(res)
            st['clash'] = {k: v for k, v in res.items() if v}
        else:
            like = {n: X.body(n) for n in OLD}
            added = []
            for k, v in new.items():
                src = like['MAIN_pcb'] if k == 'MAIN_pcb' else (like['MAIN_J2_plug_env'] if k.endswith('plug_env') else like['MAIN_front_env'])
                b = X.root.bRepBodies.add(v)
                b.name = 'NEW_' + k
                try:
                    b.appearance = src.appearance
                except Exception:
                    pass
                added.append([b, k])
            for n in OLD:
                if like[n] is not None:
                    X.retire(like[n], '_v47')
            for b, k in added:
                b.name = k
                b.isLightBulbOn = SHOW.get(k, True)
            st['added'] = {'dups': X.dups(), 'bodies': X.root.bRepBodies.count, 'names': [k for b, k in added]}
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('h1b_apply' if APPLY else 'h1b', st)


run(None)
