# rev F d3d (2026-11-06), read-only: SPKBOX_R's chamber leaks after d3/d3b (box-air test: chamber lump fills the test box).
#   Localise: fill candidate regions in a TemporaryBRep copy of the box and re-run the box-air test on each variant.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
DIFF = adsk.fusion.BooleanTypes.DifferenceBooleanType
PCIN = adsk.fusion.PointContainment.PointInsidePointContainment


def chamber(X, boxtb, spk, sx):
    bb = wbb(X, boxtb); g = 1.0
    Rb = [bb[0] - g, bb[1] + g, bb[2] - g, bb[3] + g, bb[4] - g, bb[5] + g]
    A = wbox_rel(X, Rb)
    X.tbm.booleanOperation(A, X.tbm.copy(boxtb), DIFF)
    X.tbm.booleanOperation(A, wbox_rel(X, [Rb[0], Rb[1], -3.7, -3.0, Rb[4], Rb[5]]), DIFF)
    X.tbm.booleanOperation(A, X.tbm.createCylinderOrCone(Dw(XC + sx * 62.0, -53.0, 30.0), 0.16, Dw(XC + sx * 62.0, -49.5, 30.0), 0.16), DIFF)
    pc = Dw(XC + sx * 70.5, -30.0, 62.0)
    for L in A.lumps:
        t = X.tbm.copy(L)
        if t.pointContainment(pc) == PCIN:
            cb = wbb(X, t)
            return {'cm3': round(t.volume, 3), 'open': any(abs(cb[i] - Rb[i]) < 0.01 for i in range(6))}
    return 'no lump'


def run(_context):
    X = Ctx(); out = {}
    try:
        b = X.body('SPKBOX_R')
        V = {'V0_current': [],
             'V1_fill_pocketA': [[-52.1, -45.9, -50.2, -32.9, 12.9, 31.1]],
             'V2_fill_pocketB': [[-48.6, -45.9, -33.1, -7.5, 12.9, 29.1]],
             'V3_fill_both': [[-52.1, -45.9, -50.2, -32.9, 12.9, 31.1], [-48.6, -45.9, -33.1, -7.5, 12.9, 29.1]],
             'V4_fill_block': [[-50.6, -43.4, -8.6, -3.6, 29.9, 46.1]],
             'V5_fill_lower_bore': 'bore'}
        for k, regs in V.items():
            t = X.tbm.copy(b)
            if regs == 'bore':
                X.union(t, X.tbm.createCylinderOrCone(Dw(XC - 52.75, -53.5, 10.25), 0.32, Dw(XC - 52.75, -5.8, 10.25), 0.32))
            else:
                for r in regs:
                    X.union(t, wbox_rel(X, r))
            out[k] = chamber(X, t, 'SPK_R', -1)
        old = X.body('SPKBOX_R_d0')
        out['old_d0'] = chamber(X, X.tbm.copy(old), 'SPK_R', -1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d3d_leak_find', 'run', out)
    print(json.dumps(out))
