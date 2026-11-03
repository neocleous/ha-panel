# rev F block 2g (2026-11-03), read-only: speaker-chamber net (back) volume per side.
# Air = box (partition chamber face .. side wall, back partition front face y -51.6 .. front, door top z 2.5 .. ceiling
# underside z 74.0) ∩ INNER_E − HOUSING_E − DOOR_F − front cavity (D40 bore, y -0.1 .. 5.5) − driver.
# Driver displacement is not dimensioned (magnet not on the drawing), so two bounds: minus the whole SPK envelope (frame +
# D40 x 26.1 basket cylinder = lower bound) and minus the frame plate only (upper bound).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
XIN = {1: 46.9, -1: 46.8}


def run(_context):
    X = Ctx(); out = {}
    try:
        B = adsk.fusion.BooleanTypes
        for s, nm in ((1, 'SPK_L'), (-1, 'SPK_R')):
            cx = XC + s * 70.5
            xs = sorted((XC + s * XIN[s], XC + s * 130))
            air = X.wbox(xs[0], xs[1], -51.6, 12, 2.5, 74.0)
            X.tbm.booleanOperation(air, X.tbm.copy(X.body('INNER_E')), B.IntersectionBooleanType)
            for n in ('HOUSING_E', 'DOOR_F'):
                X.tbm.booleanOperation(air, X.tbm.copy(X.body(n)), B.DifferenceBooleanType)
            X.diff(air, X.tbm.createCylinderOrCone(Dw(cx, -0.1, 28.0), 2.0, Dw(cx, 5.5, 28.0), 2.0))
            gross = air.volume
            frame = X.wbox(cx - 23.0, cx + 23.0, -3.0, 0.0, 5.0, 51.0)
            a2 = X.tbm.copy(air); X.tbm.booleanOperation(a2, frame, B.DifferenceBooleanType)
            X.tbm.booleanOperation(air, X.tbm.copy(X.body(nm)), B.DifferenceBooleanType)
            out['+x' if s > 0 else '-x'] = {'gross_minus_walls_door_bore_cm3': round(gross, 2),
                                            'net_lower_minus_envelope_cm3': round(air.volume, 2),
                                            'net_upper_minus_frame_only_cm3': round(a2.volume, 2),
                                            'lumps': air.lumps.count}
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b2g_chamber_volume', 'chamber volumes', out)
    print(json.dumps(out))
