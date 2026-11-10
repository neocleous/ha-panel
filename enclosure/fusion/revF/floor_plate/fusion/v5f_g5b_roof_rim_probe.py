# rev F g5b (2026-11-10): read-only probes for two follow-ups (Daniel 22:45: 2b, 3b).
#  ROOF: how much of the right speaker box's raised roof (version 42) can come back beside the key path of the box-top screw.
#    Key path: 2.0 key (r 1.2) from the head (-58, -8.25, 79.5), leaning psi toward the middle (psi_min..14 deg) and 0 or 5 deg up; kept clear by
#    2.0, plus a 1.5 wall. Gain = the v42 chamber air above the present ceiling that lies outside that.
#  RIM: sections through plate, shell, cloth and door at the bottom edge (needles along the wall normal), and what the plate carries above
#    z 2.5 under the shell's edge.
import os, re
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
LEGACY = ('DOOR_tray', 'HOUSING_E', 'HOUSING_shell', 'HOUSING_F_wip', 'AMP_env_20x20x10', 'BUCK_20to5V_env_43x25x13', 'DOOR_plate_revE', 'GROMMET_usbc',
          'HOUSING_F_front_d10_sliver', 'HOUSING_F_front_d12a_sliver1', 'LD2410C_env', 'MAIN_BRACKET_d1split_L', 'MAIN_BRACKET_d1split_R',
          'MAIN_BRACKET_d1split_plug', 'PD_trigger_env_20V', 'PI5_board', 'SPKBOX_L_r2', 'SPK_driver_D40', 'V11a_mx', 'V11a_px', 'V11a_up', 'V11b_mx',
          'V11b_px', 'V11b_up', 'V11c_straight', 'VOICEPE_back_env', 'VOICEPE_encoder_env', 'VOICEPE_pcb', 'BME680_env_revD', 'TOUCH_pcb_100x44')
BACK = re.compile(r'(_v\d+|_[a-e]\d+[a-z0-9]*| \(\d+\))$')
PRE = ('REF_', 'TOOL_', 'INNER', 'RENDER_', 'AUD_')
PCIN = adsk.fusion.PointContainment.PointInsidePointContainment
PART = globals().get('PART', 'roof')
rad = math.radians


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        if PART == 'roof':
            R42 = X.body('SPKBOX_R_v42'); Rc = X.body('SPKBOX_R')

            def chamber(B):
                Rb = [-101.0, -40.0, -60.0, 3.0, 1.0, 92.0]
                A = X.wbox(*Rb)
                X.dif(A, X.cp(B)); X.dif(A, X.wbox(Rb[0], Rb[1], -3.7, -3.0, Rb[4], Rb[5]))
                X.dif(A, X.cyly(-62.0, 30.0, 2.2, -53.5, -49.0))
                pc = Wp(-70.5, -30.0, 62.0)
                for L in A.lumps:
                    try:
                        if L.pointContainment(pc) == PCIN:
                            return X.cp(L)
                    except Exception:
                        pass
                return None

            a42 = chamber(R42); ac = chamber(Rc)
            top = X.wbox(-110, -30, -70, 10, 74.5, 100.0)
            a42t = X.cp(a42); X.sec(a42t, X.cp(top))
            act = X.cp(ac); X.sec(act, X.cp(top))
            h42 = X.cp(R42); X.sec(h42, X.wbox(-110, -30, -70, 10, 76.0, 100.0))
            st['v42 box above z 76'] = [round(X.vol(h42), 1), X.lumps(h42, 20000)[0][1]]
            st['v42 air above z 74.5'] = [round(X.vol(a42t), 1), X.lumps(a42t, 20000)[0][1]]
            st['present air above z 74.5'] = round(X.vol(act), 1)
            st['air v42 / present (cm3)'] = [round(X.vol(a42) / 1000.0, 3), round(X.vol(ac) / 1000.0, 3)]
            # plan outline of the v42 air at z 78: bounding boxes of slices along y
            sl = {}
            for y in (-50.0, -45.0, -40.0, -35.0, -30.0, -25.0, -20.0, -15.0, -12.0):
                t = X.cp(a42t); X.sec(t, X.wbox(-110, -30, y - 0.05, y + 0.05, 77.9, 78.1))
                sl['y%g' % y] = [[l[1][0], l[1][1]] for l in X.lumps(t, 3000) if l[1]]
            st['v42 air at z 78: x extents per y'] = sl
            status('g5b_roof', st)
            H = (-58.0, -8.25, 79.5)

            def corridor(pmin, r):
                c = None
                for ps in range(pmin, 15, 2):
                    for dz in (0, 5):
                        u = (math.sin(rad(ps)) * math.cos(rad(dz)), -math.cos(rad(ps)) * math.cos(rad(dz)), math.sin(rad(dz)))
                        q = X.tbm.createCylinderOrCone(Wp(*H), r / 10.0, Wp(H[0] + 101 * u[0], H[1] + 101 * u[1], H[2] + 101 * u[2]), r / 10.0)
                        c = q if c is None else X.uni(c, q)
                X.uni(c, X.cyly(H[0], H[2], max(r, 3.5), -22.0, -3.0))
                return c

            gains = {}
            for pmin in (6, 8, 10, 12):
                C = corridor(pmin, 1.2 + 2.0 + 1.5)
                g = X.cp(a42t); X.dif(g, C)
                lm = X.lumps(g, 20000)
                gains['psi %d..14' % pmin] = {'air outside mm3': round(X.vol(g), 1), 'lumps': [[l[0], l[1]] for l in lm[:4]]}
                Ck = corridor(pmin, 1.2 + 2.0)
                gains['psi %d..14' % pmin]['v42 box material inside the 2.0 corridor mm3'] = round(X.clash(Ck, R42), 1)
                gains['psi %d..14' % pmin]['present box inside the 2.0 corridor mm3'] = round(X.clash(Ck, Rc), 1)
            st['gain'] = gains
            status('g5b_roof', st)
            # what else stands where the raised roof was
            O = X.cp(a42t); X.uni(O, X.cp(h42))
            cur = [b for b in X.root.bRepBodies if not (b.name in LEGACY or BACK.search(b.name) or b.name.startswith(PRE))]
            st['raised roof envelope (v42) against the present bodies'] = {b.name: round(X.clash(O, b), 2) for b in cur if b.name != 'SPKBOX_R' and abs(X.clash(O, b)) > 0.005}
            S = X.cp(X.body('HOUSING_F_front')); X.sec(S, X.wbox(-110, -30, -70, 12, 40.0, 100.0))
            lift = {}
            for dy, dz in ((-1.3, 0.0), (-1.3, -3.0), (-1.3, -10.0), (-1.3, -30.0), (-0.65, 0.0), (0.0, 0.0), (-1.5, 0.0), (-1.5, -10.0)):
                t = X.cp(O); X.move(t, 0.0, dy, dz)
                try:
                    X.tbm.booleanOperation(t, S, BT.IntersectionBooleanType); lift['dy%g dz%g' % (dy, dz)] = round(X.vol(t), 2)
                except Exception:
                    lift['dy%g dz%g' % (dy, dz)] = -1
            st['raised roof envelope against the shell during the lift-in'] = lift
        else:
            P = X.body('FLOOR_PLATE')
            S = X.cp(X.body('HOUSING_F_front')); X.sec(S, X.wbox(-130, 130, -110, 40, 2.0, 9.0))
            D = X.cp(X.body('HOUSING_F_door')); X.sec(D, X.wbox(-130, 130, -110, 40, 2.0, 9.0))
            CF = X.cp(X.body('RENDER_FABRIC_front')); X.sec(CF, X.wbox(-130, 130, -110, 40, -1.0, 9.0))
            CD = X.cp(X.body('RENDER_FABRIC_door')); X.sec(CD, X.wbox(-130, 130, -110, 40, -1.0, 9.0))
            bodies = {'plate': P, 'shell': S, 'door': D, 'cloth front': CF, 'cloth door': CD}

            def runs(B, axis, a0, a1, c1, c2):
                if axis == 'x':
                    n = X.wbox(a0, a1, c1 - 0.02, c1 + 0.02, c2 - 0.02, c2 + 0.02)
                else:
                    n = X.wbox(c1 - 0.02, c1 + 0.02, a0, a1, c2 - 0.02, c2 + 0.02)
                try:
                    X.tbm.booleanOperation(n, B, BT.IntersectionBooleanType)
                except Exception:
                    return 'fail'
                out = []
                for l in X.lumps(n, 400):
                    if l[1]:
                        out.append([l[1][0], l[1][1]] if axis == 'x' else [l[1][2], l[1][3]])
                return sorted(out)

            STN = {'chin centre (x 0, along y)': ('y', -4.0, 9.0, 0.0), 'chin at the rest pad (x 13, along y)': ('y', -4.0, 9.0, 13.0),
                   'chin at the tongue (x 30, along y)': ('y', -4.0, 9.0, 30.0), 'side (y -30, along x)': ('x', 86.0, 98.0, -30.0),
                   'side near the back (y -50, along x)': ('x', 82.0, 98.0, -50.0), 'back centre (x 0, along y)': ('y', -90.0, -74.0, 0.0),
                   'back at x 40 (along y)': ('y', -90.0, -66.0, 40.0)}
            sec = {}
            for sn, (ax, a0, a1, c1) in STN.items():
                rows = {}
                for z in (0.5, 1.5, 2.2, 2.45, 2.65, 2.9, 3.5, 5.0):
                    row = {}
                    for bn, B in bodies.items():
                        r = runs(B, ax, a0, a1, c1, z)
                        if r:
                            row[bn] = r
                    rows['z%g' % z] = row
                sec[sn] = rows
                st['sections'] = sec; status('g5b_rim', st)
            t = X.cp(P); X.sec(t, X.wbox(-130, 130, -110, 40, 2.55, 2.75))
            pads = []
            Sd = X.cp(S); X.move(Sd, 0, 0, -0.25)
            for L in t.lumps:
                q = X.cp(L)
                bb = X.lumps(X.cp(q), 3000)[0]
                under = X.cp(q)
                try:
                    X.tbm.booleanOperation(under, Sd, BT.IntersectionBooleanType); uv = round(X.vol(under), 2)
                except Exception:
                    uv = -1
                pads.append([bb[0], bb[1], uv])
            st['plate above z 2.55: [mm3 in the slice z 2.55..2.75, bbox, mm3 of it under the shell edge]'] = pads
            Sb = X.cp(S); X.sec(Sb, X.wbox(-130, 130, -110, 40, 2.8, 3.0))
            st['shell edge footprint mm2 (slice z 2.8..3.0)'] = round(X.vol(Sb) / 0.2, 1)
            Db = X.cp(D); X.sec(Db, X.wbox(-130, 130, -110, 40, 2.8, 3.0))
            st['door edge footprint mm2 (slice z 2.8..3.0)'] = round(X.vol(Db) / 0.2, 1)
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-6:]
    st['t_end'] = round(time.time() - t0, 1)
    status('g5b_' + PART, st)


run(None)
