# rev F block 4d (2026-11-04): the 5807 cradle becomes a separate part.
#   B4c's posts (z to 14.0 on the front shell) sit in both speaker boxes' insertion path (boxes enter 40 inboard, inboard faces
#   at x_rel ±6, bottom z 9.0): 36.8 / 41.0 mm³ along the whole entry. The 5807 itself (z 13–18.9, x_rel ±10.2) is in that
#   path too, and in the Pi's (lift 2.0) – so the 5807 has to go in after the boxes and after the Pi.
#   1. Front shell: remove B4C's posts and rib (cut above the floor, z 2.5…14.5); add two floor bosses Ø8 at (x_rel ±13.5,
#      y −64.5), z 2.0…8.0 (below the boxes' path z 9.0 and the Pi's underside 8.56 at lift 2.0), Ruthex M3 holes Ø4.0 × 5.7.
#   2. CRADLE_5807 (new body, printed separately): plate x_rel ±10.5, y −83.2…−60.5, z 8.0…11.0, ears Ø8 at the floor bosses
#      with Ø3.4 holes (M3 × 6 DIN912, as the door screws), posts Ø6 z 11.0…14.0 at the 5807 holes with Ruthex M2 holes Ø3.2
#      from z 14.0 down 4.5 (M2 × 5 through the PCB), rear stop rib x_rel ±6, y −83.2…−80.2, z 11.0…13.0 (1.0 under the PCB).
#   Order: … main board + bracket → Pi → cradle (screwed down) → 5807 on the cradle → cables → door.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
EXPECT = {'HOUSING_F_front': 244.197, 'HOUSING_F_door': 55.484}
HOLES = ((-7.747, -62.74), (7.493, -62.74))
FBS = ((13.5, -64.5), (-13.5, -64.5))


def run(_context):
    X = Ctx(); out = {}
    B = adsk.fusion.BooleanTypes; tbm = X.tbm

    def vol_x(a_, b_):
        q = tbm.copy(a_); tbm.booleanOperation(q, tbm.copy(b_), B.IntersectionBooleanType); return round(q.volume * 1000, 2)

    def mv(t, dx, dy, dz):
        m = adsk.core.Matrix3D.create(); m.translation = V3(dx / 10, (dy * C + dz * S) / 10, (-dy * S + dz * C) / 10)
        tbm.transform(t, m); return t
    try:
        for k, v in EXPECT.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.003:
                raise RuntimeError('guard: %s volume %s, expected %s' % (k, None if b is None else round(b.volume, 3), v))
        if X.body('CRADLE_5807') is not None:
            raise RuntimeError('CRADLE_5807 exists already')
        fb = X.body('HOUSING_F_front'); v0 = fb.volume
        cut = None
        for (x, y) in HOLES:
            c = X.wcyl_z(XC + x, y, 3.05, 2.5, 14.5)
            cut = c if cut is None else X.union(cut, c)
        cut = X.union(cut, X.wbox(XC - 6.05, XC + 6.05, -83.25, -80.15, 2.5, 13.5))
        X.combine(fb, [X.add(cut, 'B4D_cut_tmp')], op=CUT)
        fb = X.body('HOUSING_F_front'); v1 = fb.volume
        add = None
        for (x, y) in FBS:
            c = X.wcyl_z(XC + x, y, 4.0, 2.0, 8.0)
            add = c if add is None else X.union(add, c)
        X.combine(fb, [X.add(add, 'B4D_bosses_tmp')])
        fb = X.body('HOUSING_F_front')
        holes = None
        for (x, y) in FBS:
            c = X.wcyl_z(XC + x, y, 2.0, 8.0 - 5.7, 8.5)
            holes = c if holes is None else X.union(holes, c)
        X.combine(fb, [X.add(holes, 'B4D_holes_tmp')], op=CUT)
        fb = X.body('HOUSING_F_front')
        out['front_cm3'] = [round(v0, 3), round(v1, 3), round(fb.volume, 3)]; out['front_lumps'] = fb.lumps.count
        cr = X.wbox(XC - 10.5, XC + 10.5, -83.2, -60.5, 8.0, 11.0)
        for (x, y) in FBS:
            cr = X.union(cr, X.wcyl_z(XC + x, y, 4.0, 8.0, 11.0))
            cr = X.union(cr, X.wbox(XC + min(x, 0) * 1.0 + (0 if x < 0 else 0), XC + max(x, 0) * 1.0, y - 3.0, y + 3.0, 8.0, 11.0))
        for (x, y) in HOLES:
            cr = X.union(cr, X.wcyl_z(XC + x, y, 3.0, 10.5, 14.0))
        cr = X.union(cr, X.wbox(XC - 6.0, XC + 6.0, -83.2, -80.2, 10.5, 13.0))
        for (x, y) in FBS:
            X.diff(cr, X.wcyl_z(XC + x, y, 1.7, 7.0, 12.0))
        for (x, y) in HOLES:
            X.diff(cr, X.wcyl_z(XC + x, y, 1.6, 14.0 - 4.5, 14.5))
        cb = X.add(cr, 'CRADLE_5807')
        out['cradle_cm3'] = round(cb.volume, 3); out['cradle_lumps'] = cb.lumps.count
        log('v5f_b4d_5807_cradle_part', 'built', out)
        pe = X.body('PD_5807_env')
        names = [b.name for b in X.comp.bRepBodies]
        comps = ['HOUSING_F_front', 'HOUSING_F_door', 'PI5_F', 'PI5_F_cooler', 'KO_5807_pigtail', 'MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env',
                 'MAIN_BRACKET', 'SPKBOX_L', 'SPKBOX_R', 'GPIO_plugA_env', 'GPIO_plugB_env', 'PD_5807_env']
        r = X.interference(cb, [X.body(n) for n in comps])
        out['cradle_interference_nonzero'] = {k: v for k, v in r.items() if v > 0} or 'all 0'
        r = X.interference(fb, [X.body(n) for n in comps if n != 'HOUSING_F_front'] + [cb] + [X.body(n) for n in names if n.startswith('LCD_')] + [X.body('SLAB_frame')])
        out['front_interference_nonzero'] = {k: v for k, v in r.items() if v > 0} or 'all 0'
        obst = None
        for n in ('PI5_F', 'PI5_F_cooler', 'MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'MAIN_BRACKET', 'HOUSING_F_front'):
            obst = tbm.copy(X.body(n)) if obst is None else X.union(obst, tbm.copy(X.body(n)))
        ins = []
        for u in (2, 5, 10, 20, 30, 40):
            v = vol_x(mv(tbm.copy(cb), 0, -float(u), 0.5), obst)
            if v > 0:
                ins.append([u, v])
        out['cradle_insertion_path_vs_pi_main_front'] = ins or 'all 0'
        dr = []
        mod = X.union(tbm.copy(cb), tbm.copy(pe))
        for u in (1, 3, 10, 30, 80):
            t = mv(tbm.copy(X.body('HOUSING_F_door')), 0, -float(u), 0)
            dr.append([u, vol_x(t, mod)])
        out['door_removal_vs_cradle_5807'] = dr
        pi = None
        for n in ('PI5_F', 'PI5_F_cooler'):
            pi = tbm.copy(X.body(n)) if pi is None else X.union(pi, tbm.copy(X.body(n)))
        crop = tbm.copy(fb); tbm.booleanOperation(crop, X.wbox(XC - 52, XC + 52, -140, 5, 0, 40), B.IntersectionBooleanType)
        pp = []
        for u in [0] + list(range(1, 71)):
            v = vol_x(mv(tbm.copy(pi), 0, -float(u), 2.0), crop)
            if v > 0:
                pp.append([u, v])
        out['pi_path_lift2_vs_front'] = pp or 'all 0 (1 mm)'
        bx = {}
        for s, bn, sp in ((1, 'SPKBOX_L', 'SPK_L'), (-1, 'SPKBOX_R', 'SPK_R')):
            mod = X.union(tbm.copy(X.body(bn)), tbm.copy(X.body(sp)))
            xs = sorted((XC, XC + s * 115.0))
            crop = tbm.copy(fb); tbm.booleanOperation(crop, X.wbox(xs[0], xs[1], -140, 5, -5, 95), B.IntersectionBooleanType)
            steps = [('lower', 0, -1.0, float(h)) for h in range(1, 7)] + [('side', -s * float(t), -1.0, 6.0) for t in range(1, 41)] + \
                    [('in', -s * 40.0, -1.0 - u, 6.0) for u in range(1, 77)]
            hits = []
            for (k, dx, dy, dz) in steps:
                v = vol_x(mv(tbm.copy(mod), dx, dy, dz), crop)
                if v > 0:
                    hits.append([k, dx, dy, dz, v])
            bx[bn] = hits or 'all 0 (%d steps)' % len(steps)
        out['box_paths_s40_vs_front'] = bx
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b4d_5807_cradle_part', 'checks', out)
    print(json.dumps(out))
