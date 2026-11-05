# rev F block 5e-2 (2026-11-05): the R1 lap joint re-built for D1 = 0.7 (R1/R2 open item: lip and magnets 0.7 deeper).
#   Door's new inner surface (B5f) at s −0.7 (s = normal distance from INNER_E's surface, + into the wall), so:
#   lip   (TOOL_inner_skin_2p1 − TOOL_inner_skin_0p9) ∩ (y −63.5…−53.5, z ≥ 6.5): s −0.9…−2.1 (0.2 under the door), extended
#         0.5 further back (R1: −63.0) because the z 25 pad moved back
#   root  TOOL_inner_skin_2p1 ∩ (y −55.0…−53.5, z ≥ 6.5): ties the lip to the front shell's wall and D1 layer
#   pads  Ø12, s −0.9…−3.0 (∩ INNER_E − skin 0.9); lip pockets Ø8.3, s −1.2…−3.1 (open to the cavity) – magnet faces 1.4 apart
#         as in R1 (door pocket floor at s +0.2, B5f). Points on INNER_E by ray (v5f_b5_common.magnet_point) at MAG_D1:
#         z 25 / 60 moved back 0.7 / 0.5 (pads 0.7 deeper would reach y −52.7 in front of the boxes' sideways insertion pose,
#         rear face −53.0); z 150 moved back 1.0 (door pocket 0.86 inside the door's end face).
#   notches r 4.0 along the four LCD-screw lanes, y −64.0…−53.4.
#   NEW body -> interference with the parts -> JOIN.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
CHECK = ['HOUSING_F_door', 'SPKBOX_L', 'SPKBOX_R', 'MAIN_BRACKET', 'MAIN_pcb', 'MAIN_back_env', 'MAIN_front_env', 'CRADLE_5807',
         'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR', 'BME680_env', 'LD2410C_env_F', 'PI5_F_cooler']


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        fb = X.body('HOUSING_F_front'); v0 = fb.volume
        lg = [e for e in json.load(open(LOG)) if e['script'] == 'v5f_b5e1_front_layer']
        if not lg or 'FAIL' in lg[-1]['data'] or abs(lg[-1]['data']['cm3'][2] - v0) > 0.003:
            raise RuntimeError('guard: B5e-1 not the last change to HOUSING_F_front (%s cm3)' % round(v0, 3))
        lip = tb_copy(X, 'TOOL_inner_skin_2p1'); X.diff(lip, tb_copy(X, 'TOOL_inner_skin_0p9'))
        inter(X, lip, X.wbox(-250, 250, -63.5, -53.5, 6.5, 260))
        root = tb_copy(X, 'TOOL_inner_skin_2p1'); inter(X, root, X.wbox(-250, 250, -55.0, -53.5, 6.5, 260))
        out['lip_cm3'] = round(lip.volume, 3); out['root_cm3'] = round(root.volume, 3)
        X.union(lip, root)
        keep = tb_copy(X, 'INNER_E'); X.diff(keep, tb_copy(X, 'TOOL_inner_skin_0p9'))
        pads = None; fcut = None; pts = {}
        for s in (1, -1):
            for (zm, ym) in MAG_D1:
                p, n, xr, nw = magnet_point(X, s, zm, ym)
                pts['%+d,%g' % (s, zm)] = {'x_rel': round(xr, 2), 'y': ym, 'n_world': nw}
                pad = cyl_pn(X, p, n, 0.0, -3.0, 6.0); inter(X, pad, X.tbm.copy(keep))
                pads = pad if pads is None else X.union(pads, pad)
                lp = cyl_pn(X, p, n, -1.2, -3.1, 4.15)
                fcut = lp if fcut is None else X.union(fcut, lp)
        out['magnets'] = pts
        X.union(lip, pads)
        notch = None
        for (a, b) in LANES_UP + LANES_LO:
            t = X.tbm.createCylinderOrCone(Dw(*a), 0.40, Dw(*b), 0.40)
            inter(X, t, X.wbox(-250, 250, -64.0, -53.4, 0, 260))
            notch = t if notch is None else X.union(notch, t)
        X.diff(lip, notch); X.diff(lip, fcut)
        out['tool_cm3'] = round(lip.volume, 3)
        tool = X.add(lip, 'B5E2_lip_tmp')
        out['tool_vs_parts_mm3'] = {k: v for k, v in X.interference(tool, [X.body(n) for n in CHECK]).items() if v > 0} or 'all 0'
        X.combine(fb, [tool])
        fb = X.body('HOUSING_F_front')
        out['cm3'] = [round(v0, 3), round(fb.volume, 3)]
        out['lumps'] = fb.lumps.count
        out['names'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('HOUSING_F')]
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
        # the boxes at their sideways insertion pose (1.0 behind the final pose) vs the front shell
        pose = {}
        for bn in ('SPKBOX_L', 'SPKBOX_R'):
            q = X.tbm.copy(X.body(bn)); mvw(X, q, 0, -1.0, 0)
            pose[bn] = vol_x(X, q, fb)
        out['box_pose_-1.0_mm3'] = pose
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b5e2_lip_d1', 'lip + pads', out)
    print(json.dumps(out))
