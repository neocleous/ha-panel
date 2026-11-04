# rev F block 4c (2026-11-04): 5807 cradle (R1 placed PD_5807_env: PCB 20.32 × 23.5 at x_rel ±10.16, y −83.7…−60.2,
# z 14.0…15.6, receptacle on top at the back edge, face y −84.6 in the door slot).
#   Holes (envelope sheet): 2 × Ø2.5 plated at (2.413; 20.955) / (17.653; 20.955) from the board corner, i.e. 2.54 from the
#   edge opposite the receptacle → x_rel −7.747 / +7.493, y −62.74. Ruthex M2 × 4: hole Ø3.2 (D3), outer 3.6, W ≥ 1.3.
#   Posts Ø6.0 from the floor (z 2.0, 0.5 into it) to the PCB underside z 14.0, insert holes Ø3.2 × 4.5 from z 14.0;
#   M2 × 5 (PCB 1.6 + 3.4 engagement) from the top. Rear support: a rib x_rel ±6.0, y −83.2…−80.2, z 2.0…13.0 under the
#   receptacle end (the 1.0 underside keep-out stays clear), takes the plug-in push down.
#   Checks: posts / rib vs PD_5807_env (0 except the screw axis), vs everything else; the Pi path (lift 2.0, u 0…70) vs the
#   5807 and the cradle (does the 5807 have to go in after the Pi?); speaker-box paths at s 40 (1 mm) vs the new front shell.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
EXPECT = {'HOUSING_F_front': 243.241, 'HOUSING_F_door': 55.484}
HOLES = ((-7.747, -62.74), (7.493, -62.74))


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
        fb = X.body('HOUSING_F_front'); pe = X.body('PD_5807_env')
        add = None
        for (x, y) in HOLES:
            c = X.wcyl_z(XC + x, y, 3.0, 2.0, 14.0)
            add = c if add is None else X.union(add, c)
        add = X.union(add, X.wbox(XC - 6.0, XC + 6.0, -83.2, -80.2, 2.0, 13.0))
        out['add_vs_5807_env_mm3'] = vol_x(add, pe)
        v0 = fb.volume
        X.combine(fb, [X.add(add, 'B4C_cradle_tmp')])
        fb = X.body('HOUSING_F_front')
        holes = None
        for (x, y) in HOLES:
            c = X.wcyl_z(XC + x, y, 1.6, 14.0 - 4.5, 14.5)
            holes = c if holes is None else X.union(holes, c)
        X.combine(fb, [X.add(holes, 'B4C_holes_tmp')], op=CUT)
        fb = X.body('HOUSING_F_front')
        out['front_cm3'] = [round(v0, 3), round(fb.volume, 3)]; out['front_lumps'] = fb.lumps.count
        out['names'] = [b.name for b in X.comp.bRepBodies if b.name.startswith(('HOUSING_F', 'B4C_'))]
        P = lambda x, y, z: X.inside(fb, XC + x, y, z)
        out['probes'] = {'post_solid': all(P(x + 2.2, y, 8.0) for (x, y) in HOLES), 'hole_open_z12': all(not P(x, y, 12.0) for (x, y) in HOLES),
                         'hole_bottom_solid_z9': all(P(x, y, 9.0) for (x, y) in HOLES), 'rib_solid': P(0.0, -81.7, 8.0)}
        log('v5f_b4c_5807_cradle', 'built', out)
        names = [b.name for b in X.comp.bRepBodies]
        comps = ['HOUSING_F_door', 'PI5_F', 'PI5_F_cooler', 'KO_5807_pigtail', 'MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'MAIN_BRACKET',
                 'SPKBOX_L', 'SPKBOX_R', 'GPIO_plugA_env', 'GPIO_plugB_env', 'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR', 'SLAB_frame',
                 'TOUCH_PCB', 'KO_touch_back', 'LD2410C_env_F', 'MIC_strip_L_env', 'MIC_strip_R_env', 'KO_mic_L_back', 'KO_mic_R_back',
                 'VEML_env'] + [n for n in names if n.startswith('LCD_')]
        r = X.interference(fb, [X.body(n) for n in comps] + [pe])
        out['front_interference_nonzero'] = {k: v for k, v in r.items() if v > 0} or 'all 0'
        pi = None
        for n in ('PI5_F', 'PI5_F_cooler'):
            pi = tbm.copy(X.body(n)) if pi is None else X.union(pi, tbm.copy(X.body(n)))
        obst = X.union(tbm.copy(pe), tbm.copy(X.body('KO_5807_pigtail')))
        pp = []
        for u in [0] + list(range(2, 72, 4)):
            v = vol_x(mv(tbm.copy(pi), 0, -float(u), 2.0), obst)
            if v > 0:
                pp.append([u, v])
        out['pi_path_lift2_vs_5807_and_pigtail_ko'] = pp or 'all 0'
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
    log('v5f_b4c_5807_cradle', 'checks', out)
    print(json.dumps(out))
