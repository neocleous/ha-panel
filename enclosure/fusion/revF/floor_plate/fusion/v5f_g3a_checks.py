# rev F g3a (2026-11-10): step 1, block 3 - read-only checks that do not depend on the main board.
#  1 microSD: d17c's finger solid (lying on the plate, bottom z 2.9, centre line x_rel -52.25, tip y -33.5, stadium sections
#    13.5 x 11 / 14.5 x 12 / 16 x 13 / 17 x 14 over 10 / 10 / 10 / 31.5 mm) against every current body but the door.
#  2 cooler-exhaust deflector on the right box: the box's inboard wall zone against the v42 box; cooler to box distance; intake field in the
#    plate: open area, anything inside the holes.
#  3 speaker chambers, d14b's method: region - box - a plate closing the baffle bore (y -3.7..-3.0) - a plug in the wire hole; the lump at
#    (+-70.5, -30, 62); upper = that air, lower = minus the driver envelope inside it.
import os, re
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
LEGACY = ('DOOR_tray', 'HOUSING_E', 'HOUSING_shell', 'HOUSING_F_wip', 'AMP_env_20x20x10', 'BUCK_20to5V_env_43x25x13', 'DOOR_plate_revE', 'GROMMET_usbc',
          'HOUSING_F_front_d10_sliver', 'HOUSING_F_front_d12a_sliver1', 'LD2410C_env', 'MAIN_BRACKET_d1split_L', 'MAIN_BRACKET_d1split_R',
          'MAIN_BRACKET_d1split_plug', 'PD_trigger_env_20V', 'PI5_board', 'SPKBOX_L_r2', 'SPK_driver_D40', 'V11a_mx', 'V11a_px', 'V11a_up', 'V11b_mx',
          'V11b_px', 'V11b_up', 'V11c_straight', 'VOICEPE_back_env', 'VOICEPE_encoder_env', 'VOICEPE_pcb', 'BME680_env_revD', 'TOUCH_pcb_100x44')
BACK = re.compile(r'(_v\d+|_[a-e]\d+[a-z0-9]*| \(\d+\))$')
PRE = ('REF_', 'TOOL_', 'INNER', 'RENDER_', 'AUD_', 'KO_')
PCIN = adsk.fusion.PointContainment.PointInsidePointContainment
PART = globals().get('PART', 'all')


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        cur = [b for b in X.root.bRepBodies if not (b.name in LEGACY or BACK.search(b.name) or b.name.startswith(PRE))]
        st['n_current'] = len(cur)
        if PART in ('all', 'sd'):
            XC_F, ZB = -52.25, 2.9
            f = None
            for (y0, y1, w, t) in [(-43.5, -33.5, 13.5, 11.0), (-53.5, -43.5, 14.5, 12.0), (-63.5, -53.5, 16.0, 13.0), (-95.0, -63.5, 17.0, 14.0)]:
                r = t / 2; dx = w / 2 - r; zc = ZB + r
                s = X.wbox(XC_F - dx, XC_F + dx, y0, y1, ZB, ZB + t)
                for xo in (XC_F - dx, XC_F + dx):
                    X.uni(s, X.cyly(xo, zc, r, y0, y1))
                f = s if f is None else X.uni(f, s)
            sd = {'finger mm3': round(X.vol(f), 1)}
            hits = {}
            for b in cur:
                if b.name in ('HOUSING_F_door', 'GROMMET_usbc_F'):
                    continue
                v = X.clash(f, b)
                if abs(v) > 0.005:
                    t = X.cp(f); X.sec(t, X.cp(b))
                    hits[b.name] = [round(v, 2), X.lumps(t, 2000)[0][1]]
            sd['hits'] = hits
            # the same finger 0.5 and 1.0 higher (plate pads), and the card's grip end zone
            for dz in (0.5, 1.0):
                g = X.cp(f); X.move(g, 0, 0, dz)
                sd['hits lifted %.1f' % dz] = {b.name: round(X.clash(g, b), 2) for b in cur if b.name not in ('HOUSING_F_door', 'GROMMET_usbc_F') and abs(X.clash(g, b)) > 0.005}
            pi = X.body('PI5_F')
            c = X.cp(pi); X.sec(c, X.wbox(-47.0, -42.0, -45.0, -15.0, 5.5, 8.5))
            sd['Pi near the card slot (x -47..-42, z 5.5..8.5)'] = X.lumps(c, 3000)
            R = X.body('SPKBOX_R')
            ch = X.wbox(-64.0, -45.9, -52.0, -31.0, 2.9, 16.0)
            sd['box material in the old finger channel (x -64..-45.9, y -52..-31, z 2.9..16)'] = round(X.clash(ch, R), 2)
            sl = X.wbox(-61.3, -45.9, -36.2, -23.6, 2.9, 8.5)
            sd['box material in the card slot (x -61.3..-45.9, y -36.2..-23.6, z 2.9..8.5)'] = round(X.clash(sl, R), 2)
            sd['plate material in channel + slot'] = [round(X.clash(ch, X.body('FLOOR_PLATE')), 2), round(X.clash(sl, X.body('FLOOR_PLATE')), 2)]
            st['microSD'] = sd; status('g3a', st)
        if PART in ('all', 'air'):
            R = X.body('SPKBOX_R'); R0 = X.body('SPKBOX_R_v42')
            Z = X.wbox(-50.0, -44.0, -56.0, -8.0, 11.0, 28.0)
            a = X.cp(R); X.sec(a, X.cp(Z)); b = X.cp(R0); X.sec(b, X.cp(Z))
            d1 = X.cp(a); X.dif(d1, X.cp(b)); d2 = X.cp(b); X.dif(d2, X.cp(a))
            defl = {'box in zone now / v42 (mm3)': [round(X.vol(a), 2), round(X.vol(b), 2)], 'added': [round(X.vol(d1), 2), X.lumps(d1, 2000)[:3]],
                    'removed': [round(X.vol(d2), 2), X.lumps(d2, 2000)[:3]]}
            mm = X.app.measureManager
            co = X.body('PI5_F_cooler')
            r = mm.measureMinimumDistance(co, R); defl['cooler to right box'] = [round(r.value * 10, 2), [round(c, 1) for c in W(r.positionOne)], [round(c, 1) for c in W(r.positionTwo)]]
            r = mm.measureMinimumDistance(co, R0); defl['cooler to right box v42'] = round(r.value * 10, 2)
            # the cooler's -x face and what is beyond it within 12 mm at z 13..24
            cb = X.lumps(X.cp(co), 20000)
            defl['cooler bbox'] = cb[0][1]
            st['deflector'] = defl; status('g3a', st)
            P = X.body('FLOOR_PLATE')
            fld = X.wbox(-42.0, 41.0, -59.0, -6.0, 1.0, 1.5)
            full = X.vol(fld)
            s = X.cp(fld); X.sec(s, X.cp(P))
            intake = {'open area mm2 (slab z 1.0..1.5)': round((full - X.vol(s)) / 0.5, 1)}
            n = 0
            for fc in P.faces:
                g = fc.geometry
                if g.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType and abs(g.radius * 10 - 1.0) < 0.02:
                    n += 1
            intake['faces r 1.0 in the plate'] = n
            air = X.wbox(-42.0, 41.0, -59.0, -6.0, 0.05, 2.45); X.dif(air, X.cp(P))
            intake['hole air mm3'] = round(X.vol(air), 1)
            intake['in the holes'] = {b.name: round(X.clash(air, b), 2) for b in cur if b.name != 'FLOOR_PLATE' and abs(X.clash(air, b)) > 0.005}
            above = X.wbox(-42.0, 41.0, -59.0, -6.0, 2.55, 6.5)
            intake['bodies 2.55..6.5 above the field (mm3)'] = {b.name: round(X.clash(above, b), 1) for b in cur if abs(X.clash(above, b)) > 0.5}
            st['intake'] = intake; status('g3a', st)
        if PART in ('all', 'vol'):
            vol = {}
            for box, spk, sx in (('SPKBOX_L', 'SPK_L', 1), ('SPKBOX_R', 'SPK_R', -1), ('SPKBOX_L_v42', 'SPK_L', 1), ('SPKBOX_R_v42', 'SPK_R', -1)):
                B = X.body(box)
                x0, x1 = sorted((sx * 40.0, sx * 101.0))
                Rb = [x0, x1, -60.0, 3.0, 1.0, 92.0]
                A = X.wbox(*Rb)
                X.dif(A, X.cp(B)); X.dif(A, X.wbox(Rb[0], Rb[1], -3.7, -3.0, Rb[4], Rb[5]))
                X.dif(A, X.cyly(sx * 62.0, 30.0, 2.2, -53.5, -49.0))
                pc = Wp(sx * 70.5, -30.0, 62.0)
                got = None
                for L in A.lumps:
                    try:
                        if L.pointContainment(pc) == PCIN:
                            got = L; break
                    except Exception:
                        pass
                if got is None:
                    vol[box] = 'no lump at the test point (%d lumps)' % A.lumps.count; continue
                t = X.cp(got)
                bb = X.lumps(t, 100000)[0][1]
                s = X.cp(X.body(spk)); X.sec(s, X.cp(t))
                sealed = bb is not None and all(abs(bb[i] - Rb[i]) > 0.05 for i in range(6))
                vol[box] = {'upper cm3': round(X.vol(t) / 1000.0, 3), 'lower cm3': round((X.vol(t) - X.vol(s)) / 1000.0, 3), 'driver envelope inside cm3': round(X.vol(s) / 1000.0, 3),
                            'air bbox': bb, 'sealed': sealed, 'lumps': A.lumps.count}
                st['chambers'] = vol; status('g3a', st)
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-6:]
    st['t_end'] = round(time.time() - t0, 1)
    status('g3a', st)


run(None)
