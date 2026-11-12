# rev F j5b (2026-11-12): close, block 5.2 - the two coarse envelopes that overlap printed parts and leads.
#   PI5_components_env: a box over the whole Pi. The Pi and its cooler are in the model as their own bodies (PI5_F, PI5_F_cooler),
#     so the box is dropped: -> PI5_components_env_v53, hidden.
#   TOUCH_components_env: a slab over the whole touch board. Replaced by the board's real back parts (rev D, courtyards from
#     hardware/touch-board/touch-board.kicad_pcb at their package heights, as e5a2): U1 1.75, R1..R4, C1, C2 1.0, standing on the
#     board's back face. Frame as e5a2: x_rel = (board's x max) - x_kicad, z = (board's z max) - y_kicad, back face = the board's y min.
#     The wire pads J1 carry no part; the lead's end is LEAD_TOUCH.
#   Dry by default: where the old envelopes are, what they overlap, the new envelope's size, whether it lies inside KO_touch_back,
#   what it overlaps. APPLY=True: old ones -> <name>_v53 (hidden), the new TOUCH_components_env added (hidden, as the old one was).
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_j_lib.py'), encoding='utf-8').read())
APPLY = globals().get('APPLY', False)
TOUCH_PARTS = {'U1': (40.42, 49.58, 10.30, 17.70, 1.75), 'R1': (38.27, 39.73, 19.02, 21.98, 1.0), 'R2': (41.77, 43.23, 19.02, 21.98, 1.0),
               'R3': (45.27, 46.73, 19.02, 21.98, 1.0), 'R4': (48.77, 50.23, 19.02, 21.98, 1.0), 'C1': (38.87, 40.33, 12.52, 15.48, 1.0),
               'C2': (37.07, 38.53, 12.52, 15.48, 1.0)}
OLD = ('PI5_components_env', 'TOUCH_components_env')


def overlaps(X, tb, skip=()):
    out = {}
    c = cache()
    for b in current(X, leads=True):
        if b.name in skip or not tb.boundingBox.intersects(b.boundingBox):
            continue
        v = xvol(X, tb, tcopy(X, b.name))
        if abs(v) > 0.005:
            out[b.name] = round(v, 2)
    return out


def run(_context):
    st = {'apply': APPLY}
    t0 = time.time()
    try:
        X = K()
        if any(X.body(n + '_v53') is not None for n in OLD):
            raise RuntimeError('already applied')
        old = {}
        for n in OLD:
            b = X.body(n)
            old[n] = {'mm3': round(X.vol(b), 1), 'world box': wext(b), 'visible': b.isLightBulbOn, 'overlaps': overlaps(X, X.cp(b), skip=(n,))}
        st['old'] = old
        tp = wext(X.body('TOUCH_PCB'))
        xr0, yb, zt = tp[1], tp[2], tp[5]
        st['touch board world box'] = tp
        st['keep-out behind the touch board, world box'] = wext(X.body('KO_touch_back'))
        env = None; parts = {}
        for ref, (x0, x1, y0, y1, h) in TOUCH_PARTS.items():
            s = X.wbox(xr0 - x1, xr0 - x0, yb - h, yb, zt - y1, zt - y0)
            parts[ref] = [round(xr0 - x1, 2), round(xr0 - x0, 2), round(yb - h, 2), round(yb, 2), round(zt - y1, 2), round(zt - y0, 2)]
            env = s if env is None else X.uni(env, s)
        st['parts (x0, x1, y0, y1, z0, z1)'] = parts
        st['new'] = {'mm3': round(X.vol(env), 1), 'lumps': env.lumps.count, 'world box': wext(env)}
        o = X.cp(env); X.dif(o, tcopy(X, 'KO_touch_back'))
        st['new']['outside KO_touch_back mm3'] = round(X.vol(o), 3)
        st['new']['overlaps'] = overlaps(X, env, skip=OLD + ('KO_touch_back',))
        if APPLY:
            like = X.body('TOUCH_components_env')
            b = X.root.bRepBodies.add(env); b.name = 'NEW_TOUCH_components_env'
            try:
                b.appearance = like.appearance
            except Exception:
                pass
            vis = like.isLightBulbOn
            for n in OLD:
                X.retire(X.body(n), '_v53')
            b.name = 'TOUCH_components_env'; b.isLightBulbOn = vis
            st['purged'] = purge(prefixes=('PI5_components_env', 'TOUCH_components_env'), tables=())
            st['added'] = {'dups': X.dups(), 'bodies': X.root.bRepBodies.count, 'mm3': round(X.vol(b), 1)}
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-6:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('j5b_apply' if APPLY else 'j5b', st)


run(None)
