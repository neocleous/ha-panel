# rev F d2 (2026-11-06; audit finding 27): the +x box's lower clamp-screw bore (Ø6.2, axis x_rel 52.75, z 10.25) is crossed
#   by the B4i USB slot's floor (z 8.2…9.7) and front wall (y −20.95…−19.45), so the M3 x 10 cannot be pushed or driven to
#   its seat at y −5.7. The audit's fix (screw above the slot) is impossible: the screw clamps the speaker through the
#   DMA45-4 frame's corner hole at (52.75, 10.25). Fix: re-cut the bore through the slot (y −53.0…−19.0). Below the slot
#   floor the bore keeps the tube's 0.9 wall to the chamber; the bore's top joins the slot (outside air), so the chamber
#   stays closed (checked in d9 with the audit's void test). Old body -> SPKBOX_L_d0 (hidden).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback


def run(_context):
    X = Ctx(); out = {}
    try:
        bx = X.body('SPKBOX_L')
        if bx is None or abs(bx.volume - 25.6228) > 0.0005:
            raise RuntimeError('guard SPKBOX_L %s' % (None if bx is None else round(bx.volume, 4)))
        if X.body('SPKBOX_L_d0') is not None:
            raise RuntimeError('SPKBOX_L_d0 exists')
        k = X.add(X.tbm.copy(bx), 'SPKBOX_L_d0'); k.isLightBulbOn = False
        v0 = bx.volume
        cyl = X.tbm.createCylinderOrCone(Dw(XC + 52.75, -53.0, 10.25), 0.31, Dw(XC + 52.75, -19.0, 10.25), 0.31)
        rem = round(vol_x(X, cyl, bx), 2)
        X.combine(bx, [X.add(cyl, 'D2_bore_tmp')], op=CUT); bx = X.body('SPKBOX_L')
        out['box_cm3'] = [round(v0, 4), round(bx.volume, 4)]; out['removed_mm3'] = rem; out['lumps'] = bx.lumps.count
        out['shells'] = [l.shells.count for l in bx.lumps]; out['faces'] = bx.faces.count
        out['names'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('SPKBOX_L')]
        P = lambda x, y, z: X.inside(bx, XC + x, y, z)
        out['probes'] = {'bore_open_y-45_low': not P(52.75, -45.0, 7.6), 'bore_open_y-30_low': not P(52.75, -30.0, 7.6),
                         'bore_open_front_wall_y-20.2': not P(52.75, -20.2, 8.0), 'bore_open_y-12': not P(52.75, -12.0, 8.0),
                         'tube_wall_below_y-45': P(52.75, -45.0, 6.7), 'tube_wall_below_y-30': P(52.75, -30.0, 6.7),
                         'tube_wall_below_y-12': P(52.75, -12.0, 6.7), 'slot_floor_beside_y-30': P(48.0, -30.0, 9.0),
                         'slot_outer_wall_y-30': P(56.4, -30.0, 15.0), 'seat_wall_y-5.2': P(52.75 + 2.5, -5.2, 10.25),
                         'front_wall_hole_open': not P(52.75, -4.7, 10.25)}
        # tool line: Ø3.0 key + Ø5.5 head path along the axis from the seat (y -5.7) back to y -60, box only
        for nm, r in (('key_d3', 1.5), ('head_d5.5', 2.75)):
            c = X.tbm.createCylinderOrCone(Dw(XC + 52.75, -6.0, 10.25), r / 10, Dw(XC + 52.75, -60.0, 10.25), r / 10)
            out['path_' + nm + '_x_box_mm3'] = vol_x(X, c, X.tbm.copy(bx))
        out['x_others'] = {n: vol_x(X, X.tbm.copy(bx), X.tbm.copy(X.body(n))) for n in
                           ('HOUSING_F_front', 'SPK_L', 'USBA_plug_env', 'USBA_cable_env', 'PI5_F', 'MAIN_BRACKET', 'TOUCH_PCB')}
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d2_boxL_bore', 'run', out)
    print(json.dumps(out, separators=(',', ':')))
