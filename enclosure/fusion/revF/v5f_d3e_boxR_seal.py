# rev F d3e (2026-11-06): d3's pocket wall in SPKBOX_R was the union of the pocket shifted 1.5 outboard / along y / along z
#   and in the x-z and x-y diagonals - the y-z edges (pocket floor meeting its end faces, y -50.1 / -33.0 / -7.6) got no
#   diagonal copy, so the wall had zero thickness along those edges and the chamber leaked there (d3d: the leak follows the
#   bottom-end layers). Add the missing copies (0, +-1.06, +-1.06) and (-0.87, +-0.87, +-0.87), minus the pocket, clipped as
#   before, and JOIN. Pocket rebuilt exactly as in d3.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback


def run(_context):
    X = Ctx(); out = {}
    try:
        bR = X.body('SPKBOX_R')
        if bR is None or abs(bR.volume - 25.6291) > 0.0005:
            raise RuntimeError('guard SPKBOX_R %s' % (None if bR is None else round(bR.volume, 4)))
        v0 = bR.volume

        def pocket(d, z_top, y0, y1):
            t = X.wbox(XC - 45.99, XC - (46.0 + d), y0, y1, 13.0, z_top)
            n = int(round(d / 0.5))
            for i in range(n):
                u1 = 46.0 + d - 0.5 * i
                X.union(t, X.wbox(XC - 45.99, XC - u1, y0, y1, z_top + 0.5 * i, z_top + 0.5 * (i + 1)))
            return t
        rec = X.union(pocket(6.0, 25.0, -50.1, -33.0), pocket(2.5, 26.5, -33.0, -7.6))
        extra = None
        for (dx, dy, dz) in ((0, 1.06, 1.06), (0, 1.06, -1.06), (0, -1.06, 1.06), (0, -1.06, -1.06),
                             (-0.87, 0.87, 0.87), (-0.87, 0.87, -0.87), (-0.87, -0.87, 0.87), (-0.87, -0.87, -0.87),
                             (0, 1.5, 1.5), (0, 1.5, -1.5), (0, -1.5, 1.5), (0, -1.5, -1.5)):
            c = mvw(X, X.tbm.copy(rec), dx, dy, dz)
            extra = c if extra is None else X.union(extra, c)
        X.diff(extra, X.tbm.copy(rec))
        inter(X, extra, X.wbox(XC - 46.0, XC - 70.0, -51.9, -5.0, 10.0, 34.0))
        X.combine(bR, [X.add(extra, 'D3E_extra_tmp')]); bR = X.body('SPKBOX_R')
        out['box_cm3'] = [round(v0, 4), round(bR.volume, 4)]; out['lumps'] = bR.lumps.count
        out['names'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('SPKBOX_R')]
        for nm, r in (('key_d3', 1.5), ('head_d6.0', 3.0)):
            c = X.tbm.createCylinderOrCone(Dw(XC - 52.75, -6.0, 10.25), r / 10, Dw(XC - 52.75, -60.0, 10.25), r / 10)
            out['low_bore_path_' + nm] = vol_x(X, c, X.tbm.copy(bR))
        out['x_SPK_R'] = vol_x(X, X.tbm.copy(bR), X.tbm.copy(X.body('SPK_R')))
        out['pocket_open'] = not X.inside(bR, XC - 50.0, -40.0, 22.0)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d3e_boxR_seal', 'run', out)
    print(json.dumps(out))
