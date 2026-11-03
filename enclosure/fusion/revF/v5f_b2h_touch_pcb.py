# rev F block 2h (2026-11-03): touch PCB (rev C, trimmed to 90 x 44 x 1.6) and its retention (K9 deviation: the floor ring
# blocks insertion from below at the chin, so the PCB goes in from behind).
# TOUCH_PCB at x_rel -45..45, y 2.7..4.3 (front face on the chin inner face after the D1 0.7 layer, y 4.3), z 6.0..50.0
# (bottom on the D1 cove's tangent line). KO_touch_back = 2.9 mm component zone behind it, x_rel -43..43 (2 mm edge bands
# kept free for the retention).
# Retention per side, on the partition cavity faces (+x 45.4, -x -45.3): ledge z 5.0..6.0 under the bottom corners
# (x to +-43.0, y 1.7..chin), lip z 6.0..6.8 behind the bottom edge (y 1.7..2.7), top tab z 43.5..47.5 behind the top
# edge (x to +-44.0, y 1.5..2.7). Fitting: lift the PCB 0.9 behind the tabs, swing the bottom forward over the lips, drop it
# onto the ledges. Top edge at z 50.9 during the lift: slot-wall clearance probed below.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
CF = {1: 45.4, -1: 45.3}


def run(_context):
    X = Ctx(); out = {}
    try:
        if X.body('TOUCH_PCB') is None:
            X.add(X.wbox(XC - 45.0, XC + 45.0, 2.7, 4.3, 6.0, 50.0), 'TOUCH_PCB')
        if X.body('KO_touch_back') is None:
            ko = X.add(X.wbox(XC - 43.0, XC + 43.0, -0.2, 2.7, 6.0, 50.0), 'KO_touch_back'); ko.isLightBulbOn = False
        tb = None
        for s in (1, -1):
            f = XC + s * CF[s]
            for (xa, y0, y1, z0, z1) in ((43.0, 1.7, 8.0, 5.0, 6.0), (43.0, 1.7, 2.7, 5.5, 6.8), (44.0, 1.5, 2.7, 43.5, 47.5)):
                xs = sorted((f, XC + s * xa))
                p = X.wbox(xs[0] - (0.5 if s < 0 else 0), xs[1] + (0.5 if s > 0 else 0), y0, y1, z0, z1)
                tb = p if tb is None else X.union(tb, p)
        X.tbm.booleanOperation(tb, X.tbm.copy(X.body('INNER_E')), adsk.fusion.BooleanTypes.IntersectionBooleanType)
        ret = X.add(tb, 'TOUCH_ret_tmp')
        out['retention_cm3'] = round(ret.volume, 4)
        r = X.interference(ret, [X.body(n) for n in ('TOUCH_PCB', 'KO_touch_back', 'PI5_F', 'GPIO_plugA_env', 'GPIO_plugB_env', 'DOOR_F', 'SPK_L', 'SPK_R')])
        out['ret_interf'] = r
        if any(v > 0 for v in r.values()):
            ret.isLightBulbOn = False
            raise RuntimeError('retention interference %s' % r)
        hb = X.body('HOUSING_E'); v0 = hb.volume
        X.combine(hb, [ret])
        hb = X.body('HOUSING_E')
        out['housing_cm3'] = (round(v0, 3), round(hb.volume, 3))
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
        pcb = X.body('TOUCH_PCB'); kob = X.body('KO_touch_back')
        names = [b.name for b in X.comp.bRepBodies]
        oth = [hb] + [X.body(n) for n in ('PI5_F', 'PI5_F_cooler', 'GPIO_plugA_env', 'GPIO_plugB_env', 'DOOR_F', 'SPK_L', 'SPK_R', 'SLAB_frame')] + [X.body(n) for n in names if n.startswith('LCD_')]
        out['pcb_interf_nonzero'] = {k: v for k, v in X.interference(pcb, oth).items() if v > 0} or 'all 0'
        out['ko_back_interf_nonzero'] = {k: v for k, v in X.interference(kob, oth).items() if v > 0} or 'all 0'
        def first_solid_y(x, z, y0=2.0, y1=9.0, it=24):
            a, c = y0, y1
            for _ in range(it):
                m = (a + c) / 2
                if X.inside(hb, x, m, z): c = m
                else: a = m
            return round((a + c) / 2, 3)
        out['front_wall_y_at_XC'] = {z: first_solid_y(XC, z) for z in (30.0, 48.0, 50.0, 50.9, 51.5)}
        out['probes'] = {s: {'ledge_z5.5': X.inside(hb, XC + s * 44.0, 3.5, 5.5), 'lip_z6.4': X.inside(hb, XC + s * 44.0, 2.2, 6.4),
                             'tab_z45': X.inside(hb, XC + s * 44.5, 2.1, 45.0), 'pcb_slot_open_z30': not X.inside(hb, XC + s * 44.5, 3.5, 30.0)} for s in (1, -1)}
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b2h_touch_pcb', 'touch PCB + retention', out)
    print(json.dumps(out))
