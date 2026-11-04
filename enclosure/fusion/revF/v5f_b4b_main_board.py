# rev F block 4b (2026-11-04): main board at candidate A (D21) on a separate printed bracket.
#   Envelopes (hidden): MAIN_pcb 90 × 50 × 1.6 at x_rel ±45, y −65.0…−63.4, z 34…84 (envelope sheet candidate A);
#   MAIN_front_env y −63.4…−33.4 (parts ≤ 30, NID 27.5) for z 35.8…84 (K7: nothing below 35.8 over the fan);
#   MAIN_back_env y −68.5…−65.0 (≤ 3.5, THT tails). Holes Ø2.7 at x_rel ±41.5, z 37.5 / 80.5 (83 × 43).
#   Why a separate bracket: with the R1 door the plane y −65 lies behind the split, and anything fixed to the front shell
#   between the boxes and the door would sit in the speaker boxes' insertion path (boxes go in first).
#   MAIN_BRACKET (new body, printed separately, fitted after the boxes and the touch PCB, before the Pi):
#   posts x_rel ±(46.5…52.5), y −62.5…−58.5, z 8.0…84; four bosses Ø8 in front of the board at the holes, y −63.4…−57.7,
#   Ruthex M2.5 × 5.7 holes Ø4.0 × 6.0 from the board face (screws M2.5 from the board's back, reachable with the door off);
#   arms bosses → posts; foot tabs z 8.0…11.0, y −62.5…−54.0 with Ø3.4 holes over two new floor bosses.
#   HOUSING_F_front: floor bosses Ø8 at (x_rel ±49.5, y −58.0), z 2.0…8.0 (below the boxes' lifted path z 9.0), Ruthex M3
#   holes Ø4.0 from z 8.0 down 5.7; M3 × 6 DIN912 from above through the tabs (as the door screws).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
EXPECT = {'HOUSING_F_front': 242.831, 'HOUSING_F_door': 55.484}
HX, HZ = 41.5, (37.5, 80.5)
PX0, PX1, PY0, PY1 = 46.5, 52.5, -62.5, -58.5
FB = (49.5, -58.0)


def run(_context):
    X = Ctx(); out = {}
    B = adsk.fusion.BooleanTypes; tbm = X.tbm

    def ycyl(x, z, r, y0, y1):
        return tbm.createCylinderOrCone(Dw(x, y0, z), r / 10, Dw(x, y1, z), r / 10)

    def vol_x(a_, b_):
        q = tbm.copy(a_); tbm.booleanOperation(q, tbm.copy(b_), B.IntersectionBooleanType); return round(q.volume * 1000, 2)
    try:
        for k, v in EXPECT.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.003:
                raise RuntimeError('guard: %s volume %s, expected %s' % (k, None if b is None else round(b.volume, 3), v))
        for k in ('MAIN_pcb', 'MAIN_BRACKET'):
            if X.body(k) is not None:
                raise RuntimeError('%s exists already' % k)
        envs = {}
        for nm, box in (('MAIN_pcb', (-45, 45, -65.0, -63.4, 34.0, 84.0)), ('MAIN_front_env', (-45, 45, -63.4, -33.4, 35.8, 84.0)),
                        ('MAIN_back_env', (-45, 45, -68.5, -65.0, 34.0, 84.0))):
            e = X.add(X.wbox(XC + box[0], XC + box[1], box[2], box[3], box[4], box[5]), nm); e.isLightBulbOn = False
            envs[nm] = round(e.volume, 3)
        out['envelopes_cm3'] = envs
        br = None
        for s in (1, -1):
            xs = sorted((XC + s * PX0, XC + s * PX1))
            post = X.wbox(xs[0], xs[1], PY0, PY1, 8.0, 84.0)
            tab = X.wbox(xs[0] - (s < 0) * 1.0, xs[1] + (s > 0) * 1.0, PY0, -54.0, 8.0, 11.0)
            part = X.union(post, tab)
            for z in HZ:
                part = X.union(part, ycyl(XC + s * HX, z, 4.0, -63.4, -57.7))
                ax = sorted((XC + s * HX, XC + s * PX0 + s * 0.5))
                part = X.union(part, X.wbox(ax[0], ax[1], PY0, PY1, z - 4.0, z + 4.0))
            br = part if br is None else X.union(br, part)
        for s in (1, -1):
            for z in HZ:
                X.diff(br, ycyl(XC + s * HX, z, 2.0, -63.5, -57.4))
            X.diff(br, X.wcyl_z(XC + s * FB[0], FB[1], 1.7, 7.0, 12.0))
        bb = X.add(br, 'MAIN_BRACKET')
        out['bracket_cm3'] = round(bb.volume, 3); out['bracket_lumps'] = bb.lumps.count
        fb = X.body('HOUSING_F_front'); v0 = fb.volume
        add = None
        for s in (1, -1):
            c = X.wcyl_z(XC + s * FB[0], FB[1], 4.0, 2.0, 8.0)
            add = c if add is None else X.union(add, c)
        X.combine(fb, [X.add(add, 'B4B_bosses_tmp')])
        fb = X.body('HOUSING_F_front')
        holes = None
        for s in (1, -1):
            c = X.wcyl_z(XC + s * FB[0], FB[1], 2.0, 8.0 - 5.7, 8.5)
            holes = c if holes is None else X.union(holes, c)
        X.combine(fb, [X.add(holes, 'B4B_holes_tmp')], op=CUT)
        fb = X.body('HOUSING_F_front')
        out['front_cm3'] = [round(v0, 3), round(fb.volume, 3)]; out['front_lumps'] = fb.lumps.count
        out['names'] = [b.name for b in X.comp.bRepBodies if b.name.startswith(('HOUSING_F', 'B4B_', 'MAIN_'))]
        log('v5f_b4b_main_board', 'built', out)
        names = [b.name for b in X.comp.bRepBodies]
        comps = ['HOUSING_F_front', 'HOUSING_F_door', 'SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'PI5_F', 'PI5_F_cooler', 'KO_K7_fan',
                 'GPIO_plugA_env', 'GPIO_plugB_env', 'PD_5807_env', 'KO_5807_pigtail', 'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR',
                 'TOUCH_PCB', 'KO_touch_back', 'LD2410C_env_F', 'SLAB_frame'] + [n for n in names if n.startswith('LCD_')]
        res = {}
        for k in ('MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'MAIN_BRACKET'):
            others = [X.body(n) for n in comps] + [X.body(n) for n in ('MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'MAIN_BRACKET') if n != k]
            r = X.interference(X.body(k), others)
            res[k] = {n: v for n, v in r.items() if v > 0} or 'all 0'
        out['interference_nonzero'] = res
        mod = None
        for k in ('MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'MAIN_BRACKET'):
            mod = tbm.copy(X.body(k)) if mod is None else X.union(mod, tbm.copy(X.body(k)))
        door = X.body('HOUSING_F_door'); sw = []
        for u in (1, 3, 10, 30, 80):
            t = tbm.copy(door); m = adsk.core.Matrix3D.create(); m.translation = V3(0, -u * C / 10, u * S / 10); tbm.transform(t, m)
            sw.append([u, vol_x(t, mod)])
        out['door_removal_vs_main_mm3'] = sw
        pi = None
        for n in ('PI5_F', 'PI5_F_cooler'):
            pi = tbm.copy(X.body(n)) if pi is None else X.union(pi, tbm.copy(X.body(n)))
        pp = []
        for u in [0] + list(range(2, 72, 4)):
            t = tbm.copy(pi); m = adsk.core.Matrix3D.create(); m.translation = V3(0, (-u * C + 2.0 * S) / 10, (u * S + 2.0 * C) / 10); tbm.transform(t, m)
            v = vol_x(t, mod)
            if v > 0:
                pp.append([u, v])
        out['pi_path_lift2_vs_main'] = pp or 'all 0'
        P = lambda x, y, z: X.inside(fb, XC + x, y, z)
        out['probes'] = {'floor_boss_solid_z6': P(49.5 + 3.0, -58.0, 6.0) and P(-49.5 - 3.0, -58.0, 6.0),
                         'insert_hole_open_z5': (not P(49.5, -58.0, 5.0)) and (not P(-49.5, -58.0, 5.0)),
                         'floor_under_hole_solid_z1.5': P(49.5, -58.0, 1.5) and P(-49.5, -58.0, 1.5),
                         'bracket_insert_open': not X.inside(X.body('MAIN_BRACKET'), XC + HX, -60.0, 37.5),
                         'bracket_boss_wall': X.inside(X.body('MAIN_BRACKET'), XC + HX + 3.0, -60.0, 37.5)}
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b4b_main_board', 'checks', out)
    print(json.dumps(out))
