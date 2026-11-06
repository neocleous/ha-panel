# rev F audit-response d4b-2 (2026-11-06), read-only: trial booleans for the door / grommet / cradle edits, all on temporary
#   copies (no body is changed). Writes ~/Documents/HA_panel_renders/d_data/data/d4b2_probe.json.
#   1. old RR boss stub (finding 8): its volume, anything above it, the old hole's notch in the new RR boss;
#   2. door boss bottoms (finding 32): floor and other parts in Ø8 z 2.5–2.85 under each boss;
#   3. bottom flange 0.4 -> 0.85 (finding 7): material added by lifting copies of the door's z 2.7–3.2 slice by 0.25 and 0.45
#      (after the stub cut), its box, and its overlap with every part;
#   4. pin holes (finding 9): the door's wall profile (REF_F_outer − 0.7 recess − (INNER_E − 0.7 layer)) against the door round
#      the old Ø2.1 holes; the fill; the new Ø1.7 holes at x ±13.85 and the web to the cutout;
#   5. USB-C recess (finding 33): what sits in the cloth layer above the sleeve, and in the space a raised sleeve / bezel would use.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
OUTF = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d4b2_probe.json')
GUARD = {'HOUSING_F_door': 51.101, 'GROMMET_usbc_F': 0.4889, 'CRADLE_5807': 2.1564, 'HOUSING_F_front': 236.1678}
BOSSES = ((19.0, -74.5), (-19.0, -77.0), (50.0, -67.0), (-50.0, -67.0))
STUB, RR = (-19.0, -74.5), (-19.0, -77.0)
SKIP_PREFIX = ('REF_', 'INNER_', 'TOOL_', 'RENDER_', 'sk_', 'HOUSING_E', 'V11')
ALWAYS = ('PD_5807_env', 'PIPWR_a_env', 'LEAD_PI_POWER', 'KO_5807_pigtail', 'LEAD_PIGTAIL_20V', 'MAIN_front_env', 'MAIN_back_env')


def parts(X, skip=()):
    res = []
    for b in X.comp.bRepBodies:
        n = b.name
        if n in skip or n.startswith(SKIP_PREFIX) or n.endswith('_tmp'):
            continue
        if b.isLightBulbOn or n in ALWAYS:
            res.append(b)
    return res


def bb_hit(a, b):
    return not (a.maxPoint.x < b.minPoint.x or b.maxPoint.x < a.minPoint.x or a.maxPoint.y < b.minPoint.y or
                b.maxPoint.y < a.minPoint.y or a.maxPoint.z < b.minPoint.z or b.maxPoint.z < a.minPoint.z)


def overlaps(X, t, skip=()):
    res = {}
    for b in parts(X, skip):
        if not bb_hit(t.boundingBox, b.boundingBox):
            continue
        v = vol_x(X, t, X.tbm.copy(b))
        if v > 0:
            res[b.name] = v
    return res or 'all 0'


def ycyl(X, x, z, r, y0=-95.0, y1=-70.0):
    return X.tbm.createCylinderOrCone(Dw(XC + x, y0, z), r / 10, Dw(XC + x, y1, z), r / 10)


def vol(t):
    return round(t.volume * 1000, 3)


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        out['guard'] = {k: round(X.body(k).volume, 4) for k in GUARD}
        door = tb_copy(X, 'HOUSING_F_door')
        # 1. stub
        ring = X.wcyl_z(XC + STUB[0], STUB[1], 4.05, 2.7, 3.3); X.diff(ring, X.wcyl_z(XC + RR[0], RR[1], 4.0, 0.0, 12.0))
        out['stub_mm3'] = vol_x(X, door, ring)
        top = X.tbm.copy(ring); inter(X, top, X.wbox(XC - 30, XC, -90, -60, 3.21, 3.3))
        out['above_stub_mm3'] = vol_x(X, door, top)
        notch = X.wcyl_z(XC + RR[0], RR[1], 4.0, 2.8, 3.2); X.diff(notch, X.wcyl_z(XC + RR[0], RR[1], 2.0, 2.0, 4.0)); X.diff(notch, X.tbm.copy(door))
        out['rr_notch_mm3'] = vol(notch)
        out['rr_rib_probe'] = {k: X.inside(X.body('HOUSING_F_door'), XC + RR[0] + dx, RR[1] + dy, 6.0)
                               for k, dx, dy in (('-y3', 0, -3.0), ('-y5', 0, -5.0), ('+x5', 5.0, 0), ('-x5', -5.0, 0), ('+y5', 0, 5.0))}
        # 2. boss bottoms
        bb = {}
        for (x, y) in BOSSES:
            c = X.wcyl_z(XC + x, y, 4.0, 2.5, 2.85)
            bb['%g,%g' % (x, y)] = {'in_gap': overlaps(X, c, ('HOUSING_F_door',)),
                                    'floor_below_mm3': vol_x(X, X.wcyl_z(XC + x, y, 4.0, 2.3, 2.5), tb_copy(X, 'HOUSING_F_front')),
                                    'boss_z2.8-3.3_mm3': vol_x(X, X.wcyl_z(XC + x, y, 4.0, 2.8, 3.3), door),
                                    'boss_z2.6-2.8_mm3': vol_x(X, X.wcyl_z(XC + x, y, 4.0, 2.6, 2.79), door)}
        out['boss_bottoms'] = bb
        out['t1'] = round(time.time() - t0, 1)
        # 3. flange: stub cut on the copy, then the lifted slice copies
        d2 = X.tbm.copy(door); X.diff(d2, X.tbm.copy(ring))
        T = X.tbm.copy(d2); inter(X, T, X.wbox(XC - 100, XC + 100, -100, -40, 2.7, 3.2))
        out['slice_mm3'] = vol(T); out['slice_box'] = [round(v, 2) for v in wbb(X, T)]
        Tu = X.tbm.copy(T); mvw(X, Tu, 0, 0, 0.25); T2 = X.tbm.copy(T); mvw(X, T2, 0, 0, 0.45); X.union(Tu, T2)
        add = X.tbm.copy(Tu); X.diff(add, X.tbm.copy(d2))
        out['flange_add_mm3'] = vol(add); out['flange_add_box'] = [round(v, 2) for v in wbb(X, add)]
        out['flange_add_lumps'] = add.lumps.count if hasattr(add, 'lumps') else None
        out['flange_add_x'] = overlaps(X, add, ('HOUSING_F_door',))
        out['t3'] = round(time.time() - t0, 1)
        # 4. pin holes
        wallp = tb_copy(X, 'REF_F_outer'); X.diff(wallp, tb_copy(X, 'TOOL_outer_skin_0p7'))
        cav = tb_copy(X, 'INNER_E'); X.diff(cav, tb_copy(X, 'TOOL_inner_skin_0p7')); X.diff(wallp, cav)
        inter(X, wallp, X.wbox(XC - 60, XC + 60, -95.0, YJ_D, -1.0, 60.0))
        pins = {}
        dfill = X.tbm.copy(door)
        for s, k in ((1, 'L'), (-1, 'R')):
            rg = ycyl(X, s * 13.6, 20.6, 1.8); X.diff(rg, ycyl(X, s * 13.6, 20.6, 1.15, -96.0, -69.0))
            a = X.tbm.copy(door); inter(X, a, X.tbm.copy(rg)); X.diff(a, X.tbm.copy(wallp))
            b = X.tbm.copy(wallp); inter(X, b, X.tbm.copy(rg)); X.diff(b, X.tbm.copy(door))
            F = ycyl(X, s * 13.6, 20.6, 1.1); inter(X, F, X.tbm.copy(wallp))
            fd = X.tbm.copy(F); X.diff(fd, X.tbm.copy(door))
            pins[k] = {'ring_door_not_wall_mm3': vol(a), 'ring_wall_not_door_mm3': vol(b), 'fill_mm3': vol(F), 'fill_new_mm3': vol(fd),
                       'fill_box': [round(v, 2) for v in wbb(X, F)]}
            X.union(dfill, F)
        for s, k in ((1, 'L'), (-1, 'R')):
            H = ycyl(X, s * 13.85, 20.6, 0.85)
            pins[k]['new_hole_cut_mm3'] = vol_x(X, dfill, H)
            far = X.tbm.copy(H); inter(X, far, X.wbox(XC - 60, XC + 60, -80.2, -70.0, 0, 60)); pins[k]['new_hole_beyond_y-80.2_mm3'] = vol_x(X, dfill, far)
            X.diff(dfill, H)
        # web after the edit: solid runs along x at y -83.0 / -82.0 / -84.0, z 20.6 (from the temp body, by point containment)
        tmpb = X.add(dfill, 'D4B2_door_trial_tmp'); tmpb.isLightBulbOn = False
        webs = {}
        for yy in (-84.0, -83.0, -82.0):
            for s, k in ((1, 'L'), (-1, 'R')):
                runs = []; cur = None
                for i in range(0, 81):
                    xx = s * (11.5 + 0.05 * i)
                    sol = X.inside(tmpb, XC + xx, yy, 20.6)
                    if sol and cur is None: cur = [round(abs(xx), 2), round(abs(xx), 2)]
                    elif sol: cur[1] = round(abs(xx), 2)
                    elif cur is not None: runs.append(cur); cur = None
                if cur is not None: runs.append(cur)
                webs['%s_y%g' % (k, yy)] = runs
        out['pins'] = pins; out['webs_x_abs'] = webs
        tmpb.deleteMe()
        out['t4'] = round(time.time() - t0, 1)
        # 5. USB-C recess space
        cl = tb_copy(X, 'REF_F_outer'); mvw(X, cl, 0.0, -0.3, 0.0)
        dout = tb_copy(X, 'REF_F_outer'); X.diff(dout, tb_copy(X, 'TOOL_outer_skin_0p7'))
        X.diff(cl, dout)                                                       # cloth layer + 0.3 into the flange
        col = X.wbox(XC - 12.1, XC + 12.1, -95.0, -75.0, 26.9, 30.9); inter(X, col, cl)
        out['collar_mm3'] = vol(col); out['collar_box'] = [round(v, 2) for v in wbb(X, col)]
        out['collar_x'] = overlaps(X, col, ('GROMMET_usbc_F',))
        out['raised_sleeve_space_x'] = overlaps(X, X.wbox(XC - 12.6, XC + 12.6, -84.0, -76.0, 27.0, 33.5), ('HOUSING_F_door', 'GROMMET_usbc_F'))
        out['bezel_ext_space_x'] = overlaps(X, X.wbox(XC - 11.0, XC + 11.0, -84.6, -81.6, 26.7, 29.8), ('CRADLE_5807',))
        out['flange_ext_space_x'] = overlaps(X, X.wbox(XC - 15.2, XC + 15.2, -88.0, -84.0, 29.5, 33.5), ('GROMMET_usbc_F',))
        out['t_s'] = round(time.time() - t0, 1)
        os.makedirs(os.path.dirname(OUTF), exist_ok=True)
        json.dump(out, open(OUTF, 'w'))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
    log('v5f_d4b2_probe', 'probe', out)
    print(json.dumps(out, separators=(',', ':')))
