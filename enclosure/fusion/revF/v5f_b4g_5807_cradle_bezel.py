# rev F block 4g (2026-11-04): 5807 cradle rebuilt on the correct hole positions + inlet bezel.
#   B4c/B4d put the 5807's M2 posts 2.54 from the edge OPPOSITE the receptacle. The envelope sheet (Eagle parse) has the holes
#   2.54 from the RECEPTACLE edge: (2.413 / 17.653, 20.955), USB-C edge Y 23.495. Board +Y → world −y, top face up → board
#   +X → world −x: holes at (x_rel +7.747 / −7.493, y −81.16), 1.2 in front of the door's inner wall (y ≈ −82.4). A Ruthex
#   M2 post (Ø3.2 hole, Ø6.0) there crosses the door wall, so:
#   1. Door: the R1 USB-C slot (x ±10.5, z 12.7–19.2) becomes an inlet cutout x ±11.3, z 7.7–20.5 through the back wall.
#   2. CRADLE_5807 (new, separate print; B4d's body → CRADLE_5807_b4d, hidden): plate x ±10.5, y −82.1…−60.5, z 8–11;
#      posts Ø6.0 z 10.5–14.0 at the holes with Ruthex M2 × 4 holes Ø3.2 × 4.5 (M2 × 6 DIN912 from the top through the PCB);
#      bezel x ±11.0, z 8.0–20.2, y −84.6…−81.6 that fills the door cutout with 0.3 all round (the door slides off it),
#      pocket for the PCB end + screw heads (x ±10.41, z 14.0–18.45, y −83.8 →), receptacle window x ±4.67, z 15.4–19.1
#      through, outer face y −84.6 = receptacle face (any plug overmould stays outside); front pads under the PCB corners
#      x ±(7.5…10.0), y −63.0…−60.6; fixing 2 × M3 × 6 DIN912 at (±5.5, −72.5), Ø3.4 + Ø6.5 × 1.5 c-bore.
#   3. Front shell: B4d's floor bosses at (±13.5, −64.5) removed (they lie under the main board: no driver access once the
#      main board is in, and the cradle has to go in after the Pi); new floor bosses Ø8 z 2.0–8.0 at (±5.5, −72.5), behind
#      the main board's back envelope (y −68.5), Ruthex M3 holes Ø4.0 × 5.7.
#   Order: … main board + bracket → Pi → cradle (2 × M3 from above, behind the main board) → 5807 (2 × M2) → cables → door.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
EXPECT = {'HOUSING_F_front': 243.65, 'HOUSING_F_door': 55.484, 'CRADLE_5807': 1.828}
H5807 = ((7.747, -81.16), (-7.493, -81.16))
OLD_FB = ((13.5, -64.5), (-13.5, -64.5))
FB = ((5.5, -72.5), (-5.5, -72.5))


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
        if X.body('CRADLE_5807_b4d') is not None:
            raise RuntimeError('CRADLE_5807_b4d exists already')
        old = X.body('CRADLE_5807'); old.name = 'CRADLE_5807_b4d'; old.isLightBulbOn = False
        # 1. door inlet cutout
        door = X.body('HOUSING_F_door'); d0 = door.volume
        X.combine(door, [X.add(X.wbox(XC - 11.3, XC + 11.3, -86.5, -81.5, 7.7, 20.5), 'B4G_door_cut_tmp')], op=CUT)
        door = X.body('HOUSING_F_door')
        out['door_cm3'] = [round(d0, 3), round(door.volume, 3)]; out['door_lumps'] = door.lumps.count
        # 3. front shell floor bosses
        fb = X.body('HOUSING_F_front'); f0 = fb.volume
        cut = None
        for (x, y) in OLD_FB:
            c = X.wcyl_z(XC + x, y, 4.05, 2.5, 8.6)
            cut = c if cut is None else X.union(cut, c)
        X.combine(fb, [X.add(cut, 'B4G_oldboss_cut_tmp')], op=CUT)
        fb = X.body('HOUSING_F_front'); f1 = fb.volume
        fill = None
        for (x, y) in OLD_FB:
            c = X.wcyl_z(XC + x, y, 2.1, 2.2, 2.5)
            fill = c if fill is None else X.union(fill, c)
        X.combine(fb, [X.add(fill, 'B4G_dimple_fill_tmp')])
        fb = X.body('HOUSING_F_front'); f2 = fb.volume
        add = None
        for (x, y) in FB:
            c = X.wcyl_z(XC + x, y, 4.0, 2.0, 8.0)
            add = c if add is None else X.union(add, c)
        X.combine(fb, [X.add(add, 'B4G_bosses_tmp')])
        fb = X.body('HOUSING_F_front')
        holes = None
        for (x, y) in FB:
            c = X.wcyl_z(XC + x, y, 2.0, 8.0 - 5.7, 8.5)
            holes = c if holes is None else X.union(holes, c)
        X.combine(fb, [X.add(holes, 'B4G_holes_tmp')], op=CUT)
        fb = X.body('HOUSING_F_front')
        out['front_cm3'] = [round(f0, 3), round(f1, 3), round(f2, 3), round(fb.volume, 3)]; out['front_lumps'] = fb.lumps.count
        # 2. cradle
        cr = X.wbox(XC - 10.5, XC + 10.5, -82.1, -60.5, 8.0, 11.0)
        for (x, y) in H5807:
            cr = X.union(cr, X.wcyl_z(XC + x, y, 3.0, 10.5, 14.0))
        cr = X.union(cr, X.wbox(XC - 11.0, XC + 11.0, -84.6, -81.6, 8.0, 20.2))
        for s in (1, -1):
            xs = sorted((XC + s * 7.5, XC + s * 10.0))
            cr = X.union(cr, X.wbox(xs[0], xs[1], -63.0, -60.6, 10.5, 14.0))
        X.diff(cr, X.wbox(XC - 10.41, XC + 10.41, -83.8, -81.0, 14.0, 18.45))
        X.diff(cr, X.wbox(XC - 4.67, XC + 4.67, -85.0, -81.0, 15.4, 19.1))
        for (x, y) in H5807:
            X.diff(cr, X.wcyl_z(XC + x, y, 1.6, 9.5, 14.05))
        for (x, y) in FB:
            X.diff(cr, X.wcyl_z(XC + x, y, 1.7, 7.5, 11.5))
            X.diff(cr, X.wcyl_z(XC + x, y, 3.25, 9.5, 11.5))
        cb = X.add(cr, 'CRADLE_5807')
        out['cradle_cm3'] = round(cb.volume, 3); out['cradle_lumps'] = cb.lumps.count
        P = lambda b, x, y, z: X.inside(b, XC + x, y, z)
        out['probes'] = {
            'door_cutout_open': not P(door, 0.0, -83.6, 10.0) and not P(door, 10.0, -83.6, 19.0),
            'door_wall_below_cutout': P(door, 0.0, -83.6, 6.0), 'door_wall_above_cutout': P(door, 0.0, -83.6, 22.0),
            'door_wall_beside_cutout': P(door, 12.5, -83.6, 14.0),
            'old_boss_gone': not P(fb, 13.5 + 3.0, -64.5, 5.0) and not P(fb, -13.5 - 3.0, -64.5, 5.0),
            'floor_at_old_boss': P(fb, 13.5, -64.5, 2.35) and P(fb, -13.5, -64.5, 2.35),
            'new_boss_solid': P(fb, 5.5 + 3.0, -72.5, 6.0) and P(fb, -5.5 - 3.0, -72.5, 6.0),
            'new_boss_hole_open': not P(fb, 5.5, -72.5, 5.0) and not P(fb, -5.5, -72.5, 5.0),
            'cradle_post_solid': P(cb, 7.747 + 2.3, -81.16, 12.0) and P(cb, -7.493 - 2.3, -81.16, 12.0),
            'cradle_m2_hole_open': not P(cb, 7.747, -81.16, 12.0) and not P(cb, -7.493, -81.16, 12.0),
            'cradle_window_open': not P(cb, 0.0, -84.3, 17.2), 'cradle_skin_beside_window': P(cb, 7.0, -84.3, 17.0),
            'cradle_pocket_open': not P(cb, 9.0, -82.8, 16.5), 'cradle_cbore_open': not P(cb, 5.5, -72.5, 10.5),
            'cradle_under_head_solid': P(cb, 5.5 + 2.4, -72.5, 9.0)}
        log('v5f_b4g_5807_cradle_bezel', 'built', out)
        # checks
        pe = X.body('PD_5807_env')
        ex = X.wbox(XC - 10.16, XC + 10.16, -83.7, -60.2, 14.0, 15.6)
        ex = X.union(ex, X.wbox(XC - 4.47, XC + 4.47, -84.6, -77.0, 15.6, 18.86))
        for (x, y) in H5807:
            ex = X.union(ex, X.wcyl_z(XC + x, y, 1.9, 15.6, 17.6))
            ex = X.union(ex, X.wcyl_z(XC + x, y, 1.0, 9.6, 15.6))
        out['cradle_vs_5807_exact_mm3'] = vol_x(cb, ex)
        out['cradle_vs_5807_env_mm3'] = vol_x(cb, pe)
        names = [b.name for b in X.comp.bRepBodies]
        comps = ['HOUSING_F_front', 'HOUSING_F_door', 'PI5_F', 'PI5_F_cooler', 'MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'MAIN_BRACKET',
                 'SPKBOX_L', 'SPKBOX_R', 'GPIO_plugA_env', 'GPIO_plugB_env']
        r = X.interference(cb, [X.body(n) for n in comps])
        out['cradle_interference_nonzero'] = {k: v for k, v in r.items() if v > 0} or 'all 0'
        r = X.interference(door, [pe, X.body('PI5_F'), X.body('MAIN_BRACKET'), X.body('MAIN_back_env')] + [X.body(n) for n in names if n.startswith('LCD_')])
        out['door_interference_nonzero'] = {k: v for k, v in r.items() if v > 0} or 'all 0'
        out['door_vs_front_mm3'] = vol_x(door, fb)
        mod = X.union(tbm.copy(cb), tbm.copy(pe))
        dr = []
        for u in (0.5, 1, 3, 10, 30, 80):
            dr.append([u, vol_x(mv(tbm.copy(door), 0, -float(u), 0), mod)])
        out['door_removal_vs_cradle_5807'] = dr
        crop = tbm.copy(fb); tbm.booleanOperation(crop, X.wbox(XC - 30, XC + 30, -140, -50, 0, 40), B.IntersectionBooleanType)
        pic = tbm.copy(X.body('PI5_F')); tbm.booleanOperation(pic, X.wbox(XC - 16, XC + 16, -62, -54, 5, 30), B.IntersectionBooleanType)
        obst = X.union(crop, pic)
        for n in ('MAIN_pcb', 'MAIN_back_env', 'MAIN_BRACKET'):
            obst = X.union(obst, tbm.copy(X.body(n)))
        ins = []
        for u in (1, 2, 5, 10, 20, 40):
            v = vol_x(mv(tbm.copy(cb), 0, -float(u), 0.5), obst)
            if v > 0:
                ins.append([u, v])
        out['cradle_slide_in_lift0.5_vs_front_pi_main'] = ins or 'all 0'
        out['cradle_lowered_0.5_vs_front'] = vol_x(mv(tbm.copy(cb), 0, 0, 0.5), crop)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b4g_5807_cradle_bezel', 'checks', out)
    print(json.dumps(out))
