# rev F d3b (2026-11-06): d3's deflector wall (pocket shifted 1.5 down / outboard) reached into SPKBOX_R's lower clamp-screw
#   bore (axis x_rel -52.75, z 10.25; the tool line stopped 26.6 behind the seat). Re-cut the bore Ø6.2 over y -53.0...-6.0;
#   where the pocket floor (z 13.0) and the bore top (z 13.35) meet the two outside-air spaces join - the chamber stays closed
#   behind the pocket wall and the tube wall (void test in the close-out).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback


def run(_context):
    X = Ctx(); out = {}
    try:
        bx = X.body('SPKBOX_R')
        if bx is None or abs(bx.volume - 25.6972) > 0.0005:
            raise RuntimeError('guard SPKBOX_R %s' % (None if bx is None else round(bx.volume, 4)))
        v0 = bx.volume
        cyl = X.tbm.createCylinderOrCone(Dw(XC - 52.75, -53.0, 10.25), 0.31, Dw(XC - 52.75, -6.0, 10.25), 0.31)
        rem = vol_x(X, cyl, bx)
        X.combine(bx, [X.add(cyl, 'D3B_bore_tmp')], op=CUT); bx = X.body('SPKBOX_R')
        out['box_cm3'] = [round(v0, 4), round(bx.volume, 4)]; out['removed_mm3'] = rem; out['lumps'] = bx.lumps.count
        out['shells'] = [l.shells.count for l in bx.lumps]
        for nm, r in (('key_d3', 1.5), ('head_d5.5', 2.75), ('head_d6.0', 3.0)):
            c = X.tbm.createCylinderOrCone(Dw(XC - 52.75, -6.0, 10.25), r / 10, Dw(XC - 52.75, -60.0, 10.25), r / 10)
            out['path_' + nm + '_x_box_mm3'] = vol_x(X, c, X.tbm.copy(bx))
        P = lambda x, y, z: X.inside(bx, XC + x, y, z)
        out['probes'] = {'tube_wall_below_y-40': P(-52.75, -40.0, 6.7), 'tube_wall_below_y-20': P(-52.75, -20.0, 6.7),
                         'seat_wall_y-5.2': P(-52.75 - 2.5, -5.2, 10.25), 'pocket_open': not P(-50.0, -40.0, 22.0),
                         'pocket_wall': P(-52.8, -40.0, 22.0)}
        out['names'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('SPKBOX_R')]
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d3b_boxR_bore', 'run', out)
    print(json.dumps(out, separators=(',', ':')))
