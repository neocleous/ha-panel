# rev F d-round box-air runner (2026-11-06): the audit's v5f_a5a_box_air.py with a volume guard.
# (Original:) HA panel model audit (2026-11-05) block 5a: speaker-box air and seal (F.2), read-only (TemporaryBRep only).
#   For each box: R = the box's tight world box grown 1.0 mm; A = R − box − PLATE − wire-hole plug, where PLATE (y −3.7…−3.0
#   over R's x / z) stands in for the rear gasket + speaker frame that close the box's front opening, and the plug (Ø3.2,
#   if PLUG_WIRE) for the sealant in the Ø3 wire hole (a designed seal at assembly). The lump of A that contains the chamber
#   point (±70.5, −30, 62) is the chamber air. If that lump's box reaches R's faces, the chamber is open to the outside.
#   Upper bound = lump volume; lower bound = lump − (SPK ∩ lump), i.e. the whole speaker envelope subtracted.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback


def guard(X):
    for k, v in globals().get('GUARD', {}).items():
        b = X.body(k)
        if b is None or abs(b.volume - v) > 0.0005:
            raise RuntimeError('GUARD %s %s (expected %s)' % (k, None if b is None else round(b.volume, 4), v))
DIFF = adsk.fusion.BooleanTypes.DifferenceBooleanType
INTER = adsk.fusion.BooleanTypes.IntersectionBooleanType
PCIN = adsk.fusion.PointContainment.PointInsidePointContainment


def run(_context):
    X = Ctx(); guard(X); out = {}; t0 = time.time()
    try:
        for (box, spk, sx) in globals().get('BOXES', [['SPKBOX_L', 'SPK_L', 1], ['SPKBOX_R', 'SPK_R', -1]]):
            bb = wbb(X, X.body(box)); g = 1.0
            Rb = [bb[0] - g, bb[1] + g, bb[2] - g, bb[3] + g, bb[4] - g, bb[5] + g]
            A = wbox_rel(X, Rb)
            X.tbm.booleanOperation(A, tb_copy(X, box), DIFF)
            X.tbm.booleanOperation(A, wbox_rel(X, [Rb[0], Rb[1], -3.7, -3.0, Rb[4], Rb[5]]), DIFF)
            if globals().get('PLUG_WIRE', True):
                a = Dw(XC + sx * 62.0, -53.0, 30.0); b = Dw(XC + sx * 62.0, -49.5, 30.0)
                X.tbm.booleanOperation(A, X.tbm.createCylinderOrCone(a, 0.16, b, 0.16), DIFF)
            pc = Dw(XC + sx * 70.5, -30.0, 62.0)
            res = {'n_lumps': A.lumps.count, 'R': [round(v, 2) for v in Rb]}
            ch = None
            for L in A.lumps:
                t = X.tbm.copy(L)
                if t.pointContainment(pc) == PCIN:
                    ch = t
                    break
            if ch is None:
                res['chamber'] = 'point not in any lump'
            else:
                cb = wbb(X, ch)
                res['chamber_cm3'] = round(ch.volume, 3); res['chamber_bb'] = [round(v, 2) for v in cb]
                res['bb_minus_R'] = [round(cb[i] - Rb[i], 2) for i in range(6)]
                s = tb_copy(X, spk); X.tbm.booleanOperation(s, X.tbm.copy(ch), INTER)
                res['spk_in_chamber_cm3'] = round(s.volume, 3)
                res['lower_cm3'] = round(ch.volume - s.volume, 3)
            out[box] = res
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d_box_air', 'run', out)
    print(json.dumps(out))
