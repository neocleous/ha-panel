# rev F block 5h (2026-11-05): top groove + rail (D2) and the under-slab groove.
#   Top groove: 1.5 wide at constant z 175.3–176.8 (upper edge 0.5 below the R3 tangent on the sides – z 177.3 – and 0.9 at
#   the back; hard band 3.2), depth 2.0 below the recessed surface (TOOL_outer_skin_2p7), around the sides, rear corners and
#   back (y < −22.5; the slot face's 2.7 skin ends at y −22.3 at z 176). Behind it the D1 layer stops (z 175.3), so a rail
#   backs it: TOOL_inner_cup_2p1 (2.1 inside INNER_E, top cap removed) ∩ z 173.8–177.6, minus the slot zone (d < 17.5) and
#   the VEML6030 envelope + 0.5 -> groove floor 2.0. The rail is joined before the groove is cut; the exhaust slots are re-cut
#   after it (the upper slot z 171.5–174.5 overlaps the rail by 0.7).
#   Under-slab groove (rev D, relative to the slab): design Z ZS−66…ZS−64.5 = −93.43…−91.93, 1.5 to 3.0 above the slab's
#   bottom edge (Z −94.93, hidden behind it), on the slot face below the boss (boss bottom Z −89.93), x_rel ±93.5:
#   2.0 below the recessed surface (d 12.3 -> 15.0) where the baffle blocks back it (|x_rel| ≥ 48);
#   1.3 (d 14.3, 0.5 floor to the slot's inner surface d 14.8) across the touch PCB (|x_rel| < 48), whose top edge sits right
#   behind it (y 4.3, z 50.0; 50.9 lifted) – no room for a rail there.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
NEAR = ['VEML_env', 'MIC_strip_L_env', 'MIC_strip_R_env', 'KO_mic_L_back', 'KO_mic_R_back', 'LEAD_VEML', 'LEAD_MIC_L', 'LEAD_MIC_R',
        'SLAB_frame', 'LCD_glass', 'LCD_pcb_76x110', 'TOUCH_PCB']
GZ0, GZ1 = -93.43, -91.93


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        fb = X.body('HOUSING_F_front'); f0 = fb.volume
        lg = [e for e in json.load(open(LOG)) if e['script'] == 'v5f_b5g_recess_feet']
        if not lg or 'FAIL' in lg[-1]['data'] or abs(lg[-1]['data']['front_cm3'][3] - f0) > 0.003:
            raise RuntimeError('guard: HOUSING_F_front %s cm3 is not the B5g result' % round(f0, 3))
        rail = tb_copy(X, 'TOOL_inner_cup_2p1'); inter(X, rail, X.wbox(-250, 250, -250, 250, 173.8, 177.6))
        X.diff(rail, dbox(X, -250, 250, -17.5, 60.0, -94.0, 260.0))
        X.diff(rail, veml_excl(X))
        out['rail_cm3'] = round(rail.volume, 3)
        rb = X.add(rail, 'B5H_rail_tmp')
        out['rail_vs_parts_mm3'] = {k: v for k, v in X.interference(rb, [X.body(n) for n in NEAR]).items() if v > 0} or 'all 0'
        X.combine(fb, [rb])
        fb = X.body('HOUSING_F_front'); f1 = fb.volume
        cut = tb_copy(X, 'TOOL_outer_skin_2p7'); inter(X, cut, X.wbox(-250, 250, -250, -22.5, GROOVE_Z[0], GROOVE_Z[1]))
        out['top_groove_tool_cm3'] = round(cut.volume, 3)
        for (x0, x1, y0) in ((XC + 48.0, XC + 93.5, -15.0), (XC - 93.5, XC - 48.0, -15.0), (XC - 48.0, XC + 48.0, -14.3)):
            X.union(cut, dbox(X, x0, x1, y0, -12.2, GZ0, GZ1))
        X.union(cut, tb_copy(X, 'TOOL_exhaust_slots'))
        X.combine(fb, [X.add(cut, 'B5H_cut_tmp')], op=CUT)
        fb = X.body('HOUSING_F_front')
        out['cm3'] = [round(f0, 3), round(f1, 3), round(fb.volume, 3)]
        out['lumps'] = fb.lumps.count
        out['names'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('HOUSING_F')]
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]

        def wall(o, d, part='HOUSING_F_front', tmax=75.0):
            ref = [r[0] for r in ray_hits(X, o, d, ('REF_F_outer',))]
            return {'ref_t': round(ref[0], 2) if ref else None, 'runs': solid_runs(X, o, d, part, tmax)}
        zg = (GROOVE_Z[0] + GROOVE_Z[1]) / 2
        out['top'] = {'groove_+x_y-35': wall((XC + 120.0, -35.0, zg), (-1, 0, 0)),
                      'groove_-x_y-40': wall((XC - 120.0, -40.0, zg), (1, 0, 0)),
                      'groove_back_x30': wall((XC + 30.0, -100.0, zg), (0, 1, 0)),
                      'below_groove_+x_y-35_z174.5': wall((XC + 120.0, -35.0, 174.5), (-1, 0, 0)),
                      'hard_band_+x_y-35_z177.3': wall((XC + 120.0, -35.0, 177.3), (-1, 0, 0))}
        dw = (0.0, -C, -S)                      # design +d (into the slot wall) as a world direction
        Zm = (GZ0 + GZ1) / 2

        def org(xr, dd, Z):                     # world point at design (x_rel, d, Z)
            return (XC + xr, -dd * C - Z * S, H - dd * S + Z * C)
        out['under_slab'] = {'x70_deep': wall(org(70.0, 10.0, Zm), dw), 'x0_shallow': wall(org(0.0, 10.0, Zm), dw),
                             'x-70_deep': wall(org(-70.0, 10.0, Zm), dw), 'x0_above_groove_Z-91.0': wall(org(0.0, 10.0, -91.0), dw)}
        out['interf_near'] = {k: v for k, v in X.interference(fb, [X.body(n) for n in NEAR]).items() if v > 0} or 'all 0'
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b5h_grooves', 'grooves', out)
    print(json.dumps(out))
