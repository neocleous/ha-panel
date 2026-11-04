# rev F rework R2d (2026-11-04), read-only: checks for the speaker-box block.
# 1. Interference (analyzeInterference) of SPKBOX_L/R and HOUSING_F_front with every component / keep-out and each other,
#    the closed door included. Designed contacts: box pegs inside the frame envelope (no holes in the envelope, 2 x 22.5 mm3),
#    the +x plug pocket vs the D40 basket envelope (fits only if the real basket is <= D32 over its rear 10 mm - bench check).
# 2. Box path on the built bodies, finer: lift 6, entry at 37 inboard, u 5...75 every 5; slide; lower; forward (box +
#    speaker envelope vs front shell, the other box, LCD + slab).
# 3. Pi fitted after the boxes: PI5_F + cooler + GPIO plug envelopes in from behind along -y, 1.0 above their seat, then
#    lowered: vs both boxes and the front shell.
# 4. Clamp-screw key paths: D6.2 along y from the tube bores back to y -90 vs the front shell; tube bores open.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback


def run(_context):
    X = Ctx(); out = {}
    B = adsk.fusion.BooleanTypes; tbm = X.tbm

    def mv(t, dx, dy, dz):
        m = adsk.core.Matrix3D.create(); m.translation = V3(dx / 10, (dy * C + dz * S) / 10, (-dy * S + dz * C) / 10)
        tbm.transform(t, m); return t

    def isect(a, b):
        t = tbm.copy(a); tbm.booleanOperation(t, tbm.copy(b), B.IntersectionBooleanType); return round(t.volume * 1000, 1)

    def ycyl(x, z, r, y0, y1):
        return tbm.createCylinderOrCone(Dw(x, y0, z), r / 10, Dw(x, y1, z), r / 10)
    try:
        fb = X.body('HOUSING_F_front'); db = X.body('HOUSING_F_door')
        bl = X.body('SPKBOX_L'); br = X.body('SPKBOX_R')
        names = [b.name for b in X.comp.bRepBodies]
        comps = ['PI5_F', 'PI5_F_cooler', 'KO_K7_fan', 'GPIO_plugA_env', 'GPIO_plugB_env', 'SPK_L', 'SPK_R', 'TOUCH_PCB', 'KO_touch_back',
                 'SLAB_frame', 'FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR', 'PD_5807_env', 'KO_5807_pigtail', 'KO_K5_LL', 'KO_K5_LR',
                 'KO_K5_UL', 'KO_K5_UR', 'HOUSING_F_door'] + [n for n in names if n.startswith('LCD_')]
        res = {}
        for tgt in (bl, br):
            r = X.interference(tgt, [X.body(n) for n in comps] + [fb, br if tgt is bl else bl])
            res[tgt.name] = {k: v for k, v in r.items() if v > 0} or 'all 0'
        r = X.interference(fb, [X.body(n) for n in comps if n.startswith(('PI5', 'GPIO', 'SPK', 'TOUCH', 'KO_touch', 'KO_K5', 'KO_K7'))])
        res['HOUSING_F_front'] = {k: v for k, v in r.items() if v > 0} or 'all 0'
        out['interference_nonzero_mm3'] = res
        log('v5f_r2d_checks', 'interference', res)
        lcd = None
        for n in [n for n in names if n.startswith('LCD_')] + ['SLAB_frame']:
            lcd = tbm.copy(X.body(n)) if lcd is None else X.union(lcd, tbm.copy(X.body(n)))
        path = {}
        for s, bx, ot, sp in ((1, bl, br, 'SPK_L'), (-1, br, bl, 'SPK_R')):
            mod = X.union(tbm.copy(bx), tbm.copy(X.body(sp)))
            steps = [('fwd', 0, -1.0, 0)] + [('lower', 0, -1.0, h) for h in (3.0, 6.0)] + \
                    [('side', -s * t, -1.0, 6.0) for t in (5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 37.0)] + \
                    [('in', -s * 37.0, -1.0 - u, 6.0) for u in (5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75)]
            worst = {}
            for (k, dx, dy, dz) in steps:
                t = mv(tbm.copy(mod), dx, dy, dz)
                v = (isect(t, fb), isect(t, ot), isect(t, lcd))
                if any(v): worst['%s %g %g %g' % (k, dx, dy, dz)] = v
            path[bx.name] = worst or 'all 0 (%d steps)' % len(steps)
        out['box_path_nonzero_front_otherbox_lcd'] = path
        log('v5f_r2d_checks', 'box path', path)
        pi = None
        for n in ('PI5_F', 'PI5_F_cooler', 'GPIO_plugA_env', 'GPIO_plugB_env'):
            pi = tbm.copy(X.body(n)) if pi is None else X.union(pi, tbm.copy(X.body(n)))
        pp = {}
        for (k, dy, dz) in [('seat', 0, 0), ('above', 0, 1.0)] + [('in', -u, 1.0) for u in (5, 10, 20, 30, 40, 50, 60, 70)]:
            t = mv(tbm.copy(pi), 0, dy, dz)
            v = (isect(t, bl), isect(t, br), isect(t, fb))
            if any(v): pp['%s %g %g' % (k, dy, dz)] = v
        out['pi_path_nonzero_boxL_boxR_front'] = pp or 'all 0'
        kp = {}
        for s, bx in ((1, bl), (-1, br)):
            for z in (10.25, 45.75):
                key = ycyl(XC + s * 52.75, z, 3.1, -52.0, -90.0)
                kp['%s z%g' % (bx.name, z)] = {'vs_front': isect(key, fb), 'bore_open_y-30': not X.inside(bx, XC + s * 52.75, -30.0, z),
                                               'tube_wall_y-30': X.inside(bx, XC + s * 55.9, -30.0, z) or X.inside(bx, XC + s * 56.3, -30.0, z),
                                               'head_seat_y-5': X.inside(bx, XC + s * 54.6, -4.7, z)}
        out['key_paths'] = kp
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_r2d_checks', 'checks', out)
    print(json.dumps(out))
