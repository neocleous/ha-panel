# Print files of version 91, block 4: the interface lines the hole reading finds near the mouths of the shell's four upper lip pockets
# on P3a in ABS. Are they in the pocket, or under the lip's own face beside its rim? The pockets lie in the curved lip, so their
# mouths are not flat: the reading's cylinder is 1.6 long on the axis, but the lip's face round the rim stands nearer the skin.
#   segs():  every support line inside each of the four cylinders, to out/hseg_lip_<n>.json (pf91_tools hseg; no Fusion object).
#   rim():   READ-ONLY on the design. For each pocket, the lip's face round the rim, found by asking the shell's body whether points
#            0.2 outside the pocket's wall are in it, every 15 deg and every 0.02 along the axis; then each support line set against
#            the rim at its own angle: in the pocket (nearer the skin than the rim), or beyond the rim (under the lip's face).
import os, json, math, runpy
D = os.path.dirname(os.path.abspath(__file__))
L = runpy.run_path(os.path.join(D, 'pf91_lib.py'))
OUT = os.path.join(L['W'], 'out'); SO = os.path.join(L['W'], 'slicer', 'out')
C12, S12, H0, XC = L['C12'], L['S12'], L['H0'], L['XC']
MX, MY, MZ = 128.003284545, 36.607776054, 6.799166551964105      # the shell's matrix of record (out/pf91_orient.json), its translation
POS = (0.0, -30.0, 0.0)                                            # the shell's place on P3a


def _pockets():
    R = json.load(open(os.path.join(OUT, 'holes_A06_P3a.json')))
    return [r for r in R if r['d'] == 8.3 and r['support_mm3'] > 0.3]


def segs(wait=40):
    lst = [{'cmd': 'hseg', 'job': os.path.join(SO, 'A06_P3a'), 'A': r['bed'][0], 'B': r['bed'][1], 'd': 8.3, 'show': 0,
            'out': os.path.join(OUT, 'hseg_lip_%d.json' % i)} for i, r in enumerate(_pockets())]
    L['tools']([('pf91_hseg_lip', 'hseg', lst)], wait)
    print(open(os.path.join(OUT, 'pf91_hseg_lip.txt')).read())


def _b2w(p):
    return (p[0] - POS[0] - MX, 6.7992 - (p[2] - POS[2]) + (MZ - 6.7992), p[1] - POS[1] - MY)


def _w2d(x, y, z):
    return ((x + XC) / 10.0, (C12 * y + S12 * (z - H0)) / 10.0, (-S12 * y + C12 * (z - H0)) / 10.0)


def rim():
    import adsk.core, adsk.fusion
    rep, root = L['guard'](strict=True); body = root.bRepBodies.itemByName('HOUSING_F_front'); P3 = adsk.core.Point3D.create
    inside = lambda w: body.pointContainment(P3(*_w2d(*w))) == adsk.fusion.PointContainment.PointInsidePointContainment
    res = []
    for i, r in enumerate(_pockets()):
        A, B = r['world']; ax = [B[k] - A[k] for k in range(3)]; La = math.sqrt(sum(c * c for c in ax)); u = [c / La for c in ax]
        e = [1.0, 0.0, 0.0]; d0 = sum(e[k] * u[k] for k in range(3)); e1 = [e[k] - d0 * u[k] for k in range(3)]; m = math.sqrt(sum(c * c for c in e1)); e1 = [c / m for c in e1]
        e2 = [u[1] * e1[2] - u[2] * e1[1], u[2] * e1[0] - u[0] * e1[2], u[0] * e1[1] - u[1] * e1[0]]
        ts = {}
        for j in range(24):
            th = math.radians(15 * j); rr = 4.15 + 0.2; last = None
            for s in range(0, 121):
                t = s * 0.02; w = [A[k] + u[k] * t + rr * (math.cos(th) * e1[k] + math.sin(th) * e2[k]) for k in range(3)]
                if inside(w):
                    last = t
                elif last is not None:
                    break
            ts[j] = last
        S = json.load(open(os.path.join(OUT, 'hseg_lip_%d.json' % i)))['lines']
        n_in = n_out = 0; worst = 0.0
        for (z, k, x1, y1, x2, y2, wd, t_b, r_b) in S:
            p = ((x1 + x2) / 2, (y1 + y2) / 2, z - 0.1); w = _b2w(p); q = [w[k2] - A[k2] for k2 in range(3)]
            t = sum(q[k2] * u[k2] for k2 in range(3)); a1 = sum(q[k2] * e1[k2] for k2 in range(3)); a2 = sum(q[k2] * e2[k2] for k2 in range(3))
            j = int(round((math.degrees(math.atan2(a2, a1)) % 360) / 15.0)) % 24
            if ts[j] is not None and t < ts[j] - 0.05:
                n_in += 1; worst = max(worst, ts[j] - t)
            else:
                n_out += 1
        out = {'pocket': i, 'world': r['world'], 'rim_t_by_15deg': [ts[j] for j in range(24)], 'lines': len(S), 'in_pocket': n_in, 'beyond_rim': n_out,
               'deepest_into_pocket': round(worst, 2)}
        res.append(out)
        print('pocket %d world %s: the lip face round the rim stands at t %.2f to %.2f (axis length 1.60) | support lines %d: in the pocket %d (deepest %.2f in), beyond the rim %d' % (
            i, [round(c, 2) for c in A], min(v for v in ts.values() if v is not None), max(v for v in ts.values() if v is not None), len(S), n_in, worst, n_out))
    rep2, _ = L['guard'](strict=True); print('modified after:', rep2['modified'])
    L['jdump']('pf91_38_lip.json', res)
# END pf91_38_lip.py
