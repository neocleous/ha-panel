# rev F block 5g (2026-11-05): the 0.7 fabric recess (D1), front feet and front Pi insert holes clear of the underside strip.
#   1. Front feet SJ5012: the 6 mm underside strip (cloth wrapped under the R6 edge fillet) ends 12 mm inside the outer
#      outline; the R1a recesses Ø13 at (x_rel ±84, y −6.5) reach 3 mm into it -> filled, new recesses Ø13 × 0.5 at
#      (±80.0, −11.5) (0.5 inside the strip's inner edge at y −4.5, ≈ 0.7 at x ≈ 87.2); FOOT_FL / FOOT_FR moved.
#   2. Front Pi insert holes (x −42.2 / 15.8, y −5.5): Ø4.0 from z 0.8 reach 1.0 into the strip -> bottoms raised to z 1.5
#      (0.8 floor under the strip; the M2.5 Ruthex insert ends at z 2.3, screw tip ≈ z 3.6).
#   3. Recess = TOOL_outer_skin_0p7 ∩ z ≤ 175.3 (top groove lower edge) − slot face / boss (d < 13.0 above design Z −93.43,
#      the under-slab groove's lower edge) − underside inside the strip (TOOL_floor_off12) − floor rim behind the R1 joint
#      (y < −55.0, z < 2.65: stays hard, the door sits on it) -> cut from the front shell and the door. Cloth edges at the
#      joint are cut flush with each part's edge (no wrap, joint gap 0.3 unchanged) – seam options in the checkpoint.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
FEET_OLD = [(84.0, -6.5), (-84.0, -6.5)]
FEET_NEW = [(80.0, -11.5), (-80.0, -11.5)]
PI_FRONT = [(-42.2, -5.5), (15.8, -5.5)]        # world x, y


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        fb = X.body('HOUSING_F_front'); db = X.body('HOUSING_F_door'); f0, d0 = fb.volume, db.volume
        lg = json.load(open(LOG))
        e3 = [e for e in lg if e['script'] == 'v5f_b5e3_front_recut']; ef = [e for e in lg if e['script'] == 'v5f_b5f_door_layer']
        if not e3 or not ef or 'FAIL' in e3[-1]['data'] or 'FAIL' in ef[-1]['data'] or \
                abs(e3[-1]['data']['cm3'][1] - f0) > 0.003 or abs(ef[-1]['data']['cm3'][3] - d0) > 0.003:
            raise RuntimeError('guard: front %s / door %s cm3 are not the B5e-3 / B5f results' % (round(f0, 3), round(d0, 3)))
        fc = {}
        for nm in ('FOOT_FL', 'FOOT_FR'):
            bb0 = wbb(X, X.body(nm)); fc[nm] = ((bb0[0] + bb0[1]) / 2, (bb0[2] + bb0[3]) / 2)
            if abs(abs(fc[nm][0]) - 84.0) > 0.5 or abs(fc[nm][1] + 6.5) > 0.5:
                raise RuntimeError('%s centre (%.2f, %.2f) is not at an R1a front foot position' % ((nm,) + fc[nm]))
        # 1 + 2: fills
        fill = None
        for (xr, y) in FEET_OLD:
            c = X.wcyl_z(XC + xr, y, 6.6, -0.2, 0.55)
            fill = c if fill is None else X.union(fill, c)
        inter(X, fill, tb_copy(X, 'REF_F_outer'))
        for (x, y) in PI_FRONT:
            X.union(fill, X.wcyl_z(x, y, 2.05, 0.75, 1.5))
        X.combine(fb, [X.add(fill, 'B5G_fill_tmp')])
        fb = X.body('HOUSING_F_front'); f1 = fb.volume
        cut = None
        for (xr, y) in FEET_NEW:
            c = X.wcyl_z(XC + xr, y, 6.5, -0.5, 0.5)
            cut = c if cut is None else X.union(cut, c)
        X.combine(fb, [X.add(cut, 'B5G_feet_tmp')], op=CUT)
        fb = X.body('HOUSING_F_front'); f2 = fb.volume
        for nm in ('FOOT_FL', 'FOOT_FR'):
            b = X.body(nm); xc, yc = fc[nm]
            (xn, yn) = [q for q in FEET_NEW if q[0] * xc > 0][0]
            coll = adsk.core.ObjectCollection.create(); coll.add(b)
            m = adsk.core.Matrix3D.create(); dy = yn - yc
            m.translation = V3((xn - xc) / 10, dy * C / 10, -dy * S / 10)
            mf = X.feats.moveFeatures
            try:
                mi = mf.createInput2(coll); mi.defineAsFreeMove(m)
            except Exception:
                mi = mf.createInput(coll, m)
            mf.add(mi)
            bb = wbb(X, X.body(nm)); out[nm + '_centre_x_rel_y'] = [round((bb[0] + bb[1]) / 2, 2), round((bb[2] + bb[3]) / 2, 2)]
        # 3: recess
        R = tb_copy(X, 'TOOL_outer_skin_0p7'); inter(X, R, X.wbox(-250, 250, -250, 250, -5.0, TOP_Z))
        X.diff(R, slot_out(X)); X.diff(R, tb_copy(X, 'TOOL_floor_off12'))
        X.diff(R, X.wbox(-250, 250, -250, YJ_F, -5.0, 2.65))
        out['recess_tool_cm3'] = round(R.volume, 3)
        out['recess_x_front_mm3'] = vol_x(X, R, fb); out['recess_x_door_mm3'] = vol_x(X, R, db)
        X.combine(db, [X.add(X.tbm.copy(R), 'B5G_recess_door_tmp')], op=CUT)
        X.combine(fb, [X.add(R, 'B5G_recess_front_tmp')], op=CUT)
        fb = X.body('HOUSING_F_front'); db = X.body('HOUSING_F_door')
        out['front_cm3'] = [round(f0, 3), round(f1, 3), round(f2, 3), round(fb.volume, 3)]
        out['door_cm3'] = [round(d0, 3), round(db.volume, 3)]
        out['lumps'] = {'front': fb.lumps.count, 'door': db.lumps.count}
        out['names'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('HOUSING_F')]
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
        # wall under the cloth along rays: REF_F_outer entry (= cloth face) and the part's solid runs (entry, exit, length)
        def wall(o, d, part, tmax):
            ref = [r[0] for r in ray_hits(X, o, d, ('REF_F_outer',))]
            return {'ref_t': round(ref[0], 2) if ref else None, 'runs': solid_runs(X, o, d, part, tmax)}
        out['walls'] = {
            'chin_x0_z25_-y': wall((XC, 20.0, 25.0), (0, -1, 0), 'HOUSING_F_front', 25.0),
            'side_+x_y-20_z100_-x': wall((XC + 120.0, -20.0, 100.0), (-1, 0, 0), 'HOUSING_F_front', 40.0),
            'side_-x_y-35_z60_+x': wall((XC - 120.0, -35.0, 60.0), (1, 0, 0), 'HOUSING_F_front', 40.0),
            'back_door_x0_z60_+y': wall((XC, -120.0, 60.0), (0, 1, 0), 'HOUSING_F_door', 45.0),
            'back_front_x50_z170_+y': wall((XC + 50.0, -100.0, 170.0), (0, 1, 0), 'HOUSING_F_front', 60.0),
            'top_hard_+x_y-35_z177.5_-x': wall((XC + 120.0, -35.0, 177.5), (-1, 0, 0), 'HOUSING_F_front', 40.0),
            'floor_strip_x0_y-1.5_+z': wall((XC, -1.5, -5.0), (0, 0, 1), 'HOUSING_F_front', 12.0),
            'floor_in_x0_y-20_+z': wall((XC, -20.0, -5.0), (0, 0, 1), 'HOUSING_F_front', 12.0),
            'floor_rim_x0_y-80_+z': wall((XC, -80.0, -5.0), (0, 0, 1), 'HOUSING_F_front', 12.0),
        }
        out['probes'] = {
            'feet_new_open': [not X.inside(fb, XC + xr, y, 0.25) for (xr, y) in FEET_NEW],
            'feet_old_solid': [X.inside(fb, XC + xr, y, 0.25) for (xr, y) in FEET_OLD],
            'pi_hole_floor_z1.0_solid': [X.inside(fb, x, y, 1.0) for (x, y) in PI_FRONT],
            'pi_hole_open_z2.0': [not X.inside(fb, x, y, 2.0) for (x, y) in PI_FRONT],
            'slot_face_hard_x0_d12.5_Z40': fb.pointContainment(P3(XC / 10, -1.25, 4.0)) in INS,
        }
        out['interf'] = X.interference(fb, [db, X.body('FOOT_FL'), X.body('FOOT_FR'), X.body('SLAB_frame'), X.body('TOUCH_PCB')])
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b5g_recess_feet', 'recess + feet', out)
    print(json.dumps(out))
