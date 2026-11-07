# rev F d22d (2026-11-07): print audit F6 opt. 2 (report-print-audit-2026-11-07). The front's cap-screw side pads SL / SR
#   (screw axes (+-43.36, -32.85), undersides z 169.5) hang 17 mm off one rib each and print on ~140 mm trees with interface
#   on the M3 head seats. Per side two hidden additions anchor the pad's first layer on three sides (a bridge between ribs),
#   so a support blocker under the pad is safe (the slicer still supports bridge perimeters without one):
#   WEB  box x +-(30.2..38.2), y -44.6..-32.6, z 169.5-172.6, from the pad's strip to the back pad's outboard rib;
#   FRIB 1.6 thick at x +-(38.2..39.8), from y -33.0 forward into the slab-boss plate, top z 170.0, underside a 46 deg plane
#        through (y -33.0, z 169.5) (self-supporting).
#   Gates: the tools touch no body but the front (parts, keep-outs, leads); 0.5 clear of the M3 head and its vertical
#   insertion (r 2.75, z 155.5-169.5) and of the key lanes (r 2.5). Old front -> HOUSING_F_front_d22 (hidden).
#   DRY (default True) builds and checks the tools only.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py'), encoding='utf-8').read())
import traceback
GUARD = {'HOUSING_F_front': 235.2569, 'HOUSING_F_cap': 9.9441, 'HOUSING_F_door': 47.2633}
AUDD = os.path.expanduser('~/Documents/audit/data')
NEWP = ['TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'BME_HOOD', 'FOAM_bme_env', 'FOAM_bme_top_env', 'HOUSING_F_door']
AX, AY = 43.36, -32.85                                         # side pads' screw axes (x_rel +-AX)
LANE = (0.152, -0.4371, -0.8865)                              # SR key lane direction (KO_capkey_SR axis); SL mirrored in x
A46 = math.radians(46.0)


def tools_side(X, s):                                         # s = +1: SL (x_rel > 0), -1: SR
    xs = lambda a, b: sorted((s * a, s * b))
    web = wbox_rel(X, xs(30.2, 38.2) + [-44.6, -32.6, 169.5, 172.6])
    fr = wbox_rel(X, xs(38.2, 39.8) + [-33.0, -16.0, 152.5, 170.0])
    n = (0.0, math.sin(A46), math.cos(A46)); d = (0.0, -math.cos(A46), math.sin(A46)); L = 300.0
    inter(X, fr, lbox(X, (s * 39.0, -33.0 + L / 2 * n[1], 169.5 + L / 2 * n[2]), (1.0, 0.0, 0.0), d, L, L, L))
    return web, fr


def keepouts_side(X, s, m):                                   # M3 head + vertical insertion, key lane; grown by m
    ko = X.wcyl_z(XC + s * AX, AY, 2.75 + m, 155.5, 169.5)
    ln = (-s * LANE[0], LANE[1], LANE[2])                     # lanes run inboard: SR +x, SL -x
    q = wv(ln); q.normalize()
    X.union(ko, cyl_pn(X, Dw(XC + s * AX, AY, 166.2), q, -0.3, 110.0, 2.5 + m))
    return ko


def run(_context):
    X = Ctx(); out = {}; t0 = time.time(); dry = globals().get('DRY', True)
    try:
        for k, v in GUARD.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard: %s %s' % (k, None if b is None else round(b.volume, 4)))
        if X.body('HOUSING_F_front_d22') is not None:
            raise RuntimeError('HOUSING_F_front_d22 exists already')
        tools = {}
        for s, tag in ((1, 'SL'), (-1, 'SR')):
            w, f = tools_side(X, s); tools['web_' + tag] = w; tools['frib_' + tag] = f
        out['tool_mm3'] = {k: round(t.volume * 1000, 1) for k, t in tools.items()}
        out['tool_bb'] = {k: [round(c, 2) for c in wbb(X, t)] for k, t in tools.items()}
        allt = None
        for t in tools.values():
            allt = X.tbm.copy(t) if allt is None else X.union(allt, X.tbm.copy(t))
        fr0 = tb_copy(X, 'HOUSING_F_front')
        out['tools_in_front_mm3'] = vol_x(X, allt, fr0)
        new = X.union(tb_copy(X, 'HOUSING_F_front'), X.tbm.copy(allt))
        out['added_mm3'] = round((new.volume - fr0.volume) * 1000, 2); out['lumps'] = new.lumps.count
        names = json.load(open(os.path.join(AUDD, 'a2a_parts.json'), encoding='utf-8')) + NEWP
        others = [b.name for b in X.comp.bRepBodies if b.name.startswith(('KO_', 'LEAD_')) or b.name.endswith('_env')]
        ab = wbb(X, allt); hits = {}
        for nm in list(dict.fromkeys(names + others)):
            b = X.body(nm)
            if b is None or nm == 'HOUSING_F_front':
                continue
            pb = wbb(X, b)
            if pb[0] > ab[1] + 0.6 or pb[1] < ab[0] - 0.6 or pb[2] > ab[3] + 0.6 or pb[3] < ab[2] - 0.6 or pb[4] > ab[5] + 0.6 or pb[5] < ab[4] - 0.6:
                continue
            v = vol_x(X, allt, b)
            if v > 0.0:
                hits[nm] = v
        out['tools_x_bodies'] = hits
        out['keepout_x_tools_mm3'] = {}
        for s, tag in ((1, 'SL'), (-1, 'SR')):
            for m in (0.0, 0.5):
                out['keepout_x_tools_mm3']['%s_m%.1f' % (tag, m)] = vol_x(X, allt, keepouts_side(X, s, m))
        out['keepout_x_newfront_mm3'] = {tag: vol_x(X, new, keepouts_side(X, s, 0.0)) for s, tag in ((1, 'SL'), (-1, 'SR'))}
        out['keepout_x_oldfront_mm3'] = {tag: vol_x(X, fr0, keepouts_side(X, s, 0.0)) for s, tag in ((1, 'SL'), (-1, 'SR'))}
        bad = {k: v for k, v in hits.items()}
        bad.update({k: v for k, v in out['keepout_x_tools_mm3'].items() if v > 0.0})
        if new.lumps.count != 1:
            bad['lumps'] = new.lumps.count
        out['gate_ok'] = not bad
        if not dry:
            if bad:
                raise RuntimeError('gates failed: %s' % bad)
            o = X.body('HOUSING_F_front'); app = o.appearance; mat = o.material; vis = o.isLightBulbOn
            o.name = 'HOUSING_F_front_d22'; o.isLightBulbOn = False
            nb = X.add(new, 'HOUSING_F_front')
            for attr, val in (('material', mat), ('appearance', app), ('isLightBulbOn', vis)):
                try:
                    setattr(nb, attr, val)
                except Exception:
                    pass
            out['applied'] = [round(nb.volume, 4), nb.lumps.count]
            I = lambda x, y, z: X.inside(nb, XC + x, y, z)
            pr = {}
            for s, tag in ((1, 'SL'), (-1, 'SR')):
                pr[tag] = {'web': I(s * 34.0, -38.0, 170.0), 'frib_top': I(s * 39.0, -30.0, 169.8),
                           'frib_low': I(s * 39.0, -20.5, 160.5), 'below_frib': not I(s * 39.0, -26.0, 160.0),
                           'seat_open': not I(s * 41.0, AY, 169.3), 'hole_open': not I(s * AX, AY, 171.0),
                           'pad_top': I(s * 38.6, -36.0, 172.55)}
            out['probes'] = pr
            out['probes_ok'] = all(all(v.values()) for v in pr.values())
        out['dry'] = dry
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d22d_f6_pad_anchors', 'dry' if globals().get('DRY', True) else 'run', out)
    print(json.dumps(out, separators=(',', ':')))
