# rev F d17c (2026-11-06), read-only: the finger's own solid along its line (lesson 76). A straight finger lying on the floor
#   (bottom z 2.9, over the door's boss pads), tip at y −33.5 with its inboard edge at x_rel −45.5 (the card's grip end is at
#   −44.85), stadium sections growing from the tip: 13.5 × 11 / 14.5 × 12 / 16 × 13 / 17 × 14 (w × t) over 10 / 10 / 10 / 31.5 mm.
#   Hits vs every part but the door (off for service). Also the driver for the right box's lower screw (Ø6 along y from behind)
#   and for the bracket's new foot screw (Ø6 from below). GUARD is set by the loader (run before d17b as the control).
#   Writes ~/Documents/HA_panel_renders/d_data/data/d17c_<TAG>.json.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
TAG = globals().get('TAG', 'after')
OUTF = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d17c_%s.json' % TAG)
AUDD = os.path.expanduser('~/Documents/audit/data')
NEWP = ['TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'BME_HOOD', 'FOAM_bme_env', 'FOAM_bme_top_env']
XC_F, ZB = -52.25, 2.9                                        # finger centre line (x_rel), bottom
SEGS = [(-43.5, -33.5, 13.5, 11.0), (-53.5, -43.5, 14.5, 12.0), (-63.5, -53.5, 16.0, 13.0), (-95.0, -63.5, 17.0, 14.0)]
FOOT = (-65.0, -57.0)


def stadium(X, y0, y1, w, t):
    r = t / 2; dx = w / 2 - r; zc = ZB + r
    s = wbox_rel(X, [XC_F - dx, XC_F + dx, y0, y1, ZB, ZB + t])
    for xo in (XC_F - dx, XC_F + dx):
        X.union(s, X.tbm.createCylinderOrCone(Dw(XC + xo, y0, zc), r / 10, Dw(XC + xo, y1, zc), r / 10))
    return s


def run(_context):
    X = Ctx(); out = {'tag': TAG}; t0 = time.time()
    try:
        for k, v in globals().get('GUARD', {}).items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard %s %s (expected %s)' % (k, None if b is None else round(b.volume, 4), v))
        f = None
        for (y0, y1, w, t) in SEGS:
            s = stadium(X, y0, y1, w, t); f = s if f is None else X.union(f, s)
        out['finger'] = {'mm3': round(f.volume * 1000, 1), 'bb': [round(c, 2) for c in wbb(X, f)]}
        drv_box = X.tbm.createCylinderOrCone(Dw(XC - 52.75, -95.0, 10.25), 0.3, Dw(XC - 52.75, -31.5, 10.25), 0.3)
        drv_foot = X.tbm.createCylinderOrCone(Dw(XC + FOOT[0], FOOT[1], -60.0), 0.3, Dw(XC + FOOT[0], FOOT[1], 0.0), 0.3)
        names = json.load(open(os.path.join(AUDD, 'a2a_parts.json'))) + NEWP
        parts = [(n, X.body(n), wbb(X, X.body(n))) for n in names if X.body(n) is not None and n != 'HOUSING_F_door']
        out['n_parts'] = len(parts)

        def hits(t):
            tb = wbb(X, t); res = {}
            for (n, b, pb) in parts:
                if pb[0] > tb[1] or pb[1] < tb[0] or pb[2] > tb[3] or pb[3] < tb[2] or pb[4] > tb[5] or pb[5] < tb[4]:
                    continue
                q = X.tbm.copy(b); inter(X, q, X.tbm.copy(t)); v = q.volume * 1000
                if v > 0.005:
                    res[n] = [round(v, 2)] + [round(c, 2) for c in wbb(X, q)]
            return res
        out['finger_hits'] = hits(f)
        out['driver_box_lower_screw_hits'] = hits(drv_box)
        out['driver_foot_screw_hits'] = hits(drv_foot)
        out['t_s'] = round(time.time() - t0, 1)
        os.makedirs(os.path.dirname(OUTF), exist_ok=True)
        json.dump(out, open(OUTF, 'w'))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
        try:
            json.dump(out, open(OUTF, 'w'))
        except Exception:
            pass
    log('v5f_d17c_finger_check', TAG, out)
    print(json.dumps(out, separators=(',', ':')))
