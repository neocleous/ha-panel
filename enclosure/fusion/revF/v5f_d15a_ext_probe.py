# rev F d15a (2026-11-06), read-only: Daniel 19:44 – the hatch is not usable; a fingertip push-push socket with the door on.
#   Extender route: plug fitted once from below through the hatch opening (pocket widened for an 8 x 18 stiffener, 23 mm
#   plug), flex under the right box and out behind it, push-push socket on the floor behind the box, slit in the door.
#   Regions vs the parts and the current R chamber; rays to the door's inner wall at the back-right corner.
#   Writes ~/Documents/HA_panel_renders/d_data/data/d15a_probe.json.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
OUTF = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d15a_probe.json')
AUDD = os.path.expanduser('~/Documents/audit/data')
NEWP = ['TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'BME_HOOD', 'FOAM_bme_env', 'FOAM_bme_top_env', 'HATCH_COVER']
GUARD = {'HOUSING_F_front': 234.701, 'SPKBOX_R': 25.5694, 'HOUSING_F_door': 47.2694}
PCIN = adsk.fusion.PointContainment.PointInsidePointContainment


def chamber(X, box, sx):
    bb = wbb(X, X.body(box)); g = 1.0
    Rb = [bb[0] - g, bb[1] + g, bb[2] - g, bb[3] + g, bb[4] - g, bb[5] + g]
    A = wbox_rel(X, Rb)
    X.diff(A, tb_copy(X, box)); X.diff(A, wbox_rel(X, [Rb[0], Rb[1], -3.7, -3.0, Rb[4], Rb[5]]))
    a = Dw(XC + sx * 62.0, -53.0, 30.0); b = Dw(XC + sx * 62.0, -49.5, 30.0)
    X.diff(A, X.tbm.createCylinderOrCone(a, 0.16, b, 0.16))
    pc = Dw(XC + sx * 70.5, -30.0, 62.0)
    for L in A.lumps:
        t = X.tbm.copy(L)
        if t.pointContainment(pc) == PCIN:
            return t


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        for k, v in GUARD.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard %s %s' % (k, None if b is None else round(b.volume, 4)))
        ch = chamber(X, 'SPKBOX_R', -1)
        names = json.load(open(os.path.join(AUDD, 'a2a_parts.json'))) + NEWP
        parts = [(n, X.body(n), wbb(X, X.body(n))) for n in names if X.body(n) is not None]

        def region(bb, skip=()):
            t = wbox_rel(X, bb); res = {}
            for (n, b, pb) in parts:
                if n in skip or pb[0] > bb[1] or pb[1] < bb[0] or pb[2] > bb[3] or pb[3] < bb[2] or pb[4] > bb[5] or pb[5] < bb[4]:
                    continue
                q = X.tbm.copy(b); inter(X, q, X.tbm.copy(t)); v = q.volume * 1000
                if v > 0.005:
                    res[n] = [round(v, 1)] + [round(c, 1) for c in wbb(X, q)]
            q = X.tbm.copy(ch); inter(X, q, X.tbm.copy(t))
            return {'bb': bb, 'hits': res, 'air_mm3': round(q.volume * 1000, 1)}
        R = {}
        R['pocket_plug'] = region([-66.7, -45.95, -39.7, -20.1, 3.0, 8.0], ('HATCH_COVER',))
        R['pocket_plug_walls'] = region([-68.2, -46.2, -41.2, -18.6, 3.9, 9.5], ('HATCH_COVER',))
        R['flex_under_box'] = region([-72.0, -56.0, -52.5, -36.0, 2.55, 3.65])
        R['flex_behind_box'] = region([-72.0, -56.0, -68.0, -52.0, 2.55, 3.65])
        R['socket_zone'] = region([-76.0, -54.0, -72.0, -52.05, 2.6, 9.0])
        rays = {}
        for x in (-56.0, -60.0, -64.0, -68.0, -72.0):
            for z in (4.0, 7.0):
                h = [r for r in ray_hits(X, (XC + x, -52.5, z), (0, -1, 0), ('HOUSING_F_door', 'HOUSING_F_front', 'MAIN_BRACKET'))]
                rays['x%g_z%g' % (x, z)] = [[round(r[0], 2), r[1], round(r[3], 2)] for r in h[:3]]
        R['rays_back'] = rays
        out['regions'] = R
        out['t_s'] = round(time.time() - t0, 1)
        os.makedirs(os.path.dirname(OUTF), exist_ok=True)
        json.dump(out, open(OUTF, 'w'))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
        try:
            json.dump(out, open(OUTF, 'w'))
        except Exception:
            pass
    log('v5f_d15a_ext_probe', 'probe', {'t_s': out.get('t_s'), 'FAIL': out.get('FAIL')})
    print(json.dumps({'t_s': out.get('t_s'), 'FAIL': out.get('FAIL')}, separators=(',', ':')))
