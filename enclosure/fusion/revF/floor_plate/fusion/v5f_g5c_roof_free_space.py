# rev F g5c (2026-11-10): read-only - free space above the right speaker box's flat roof (z 76..82), beyond what version 42 used.
# Column = the box's own outline at its roof (slice z 75.0..75.5) carried up to z 82. Taken away: every present body (shell also 1.3 and 1.5
# back for the lift-in, and with the column 0..10 below its place), the display-screw and cap key paths, the box-top screw's key corridor
# (2.0 key, 6..14 deg toward the middle, 0 or 5 deg up, 2.0 clear + 1.5 wall). What is left is the largest envelope a raised roof could
# fill; the air gained is that minus a 1.5 roof and 1.5 walls where the envelope ends in the open.
import os, re
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
LEGACY = ('DOOR_tray', 'HOUSING_E', 'HOUSING_shell', 'HOUSING_F_wip', 'AMP_env_20x20x10', 'BUCK_20to5V_env_43x25x13', 'DOOR_plate_revE', 'GROMMET_usbc',
          'HOUSING_F_front_d10_sliver', 'HOUSING_F_front_d12a_sliver1', 'LD2410C_env', 'MAIN_BRACKET_d1split_L', 'MAIN_BRACKET_d1split_R',
          'MAIN_BRACKET_d1split_plug', 'PD_trigger_env_20V', 'PI5_board', 'SPKBOX_L_r2', 'SPK_driver_D40', 'V11a_mx', 'V11a_px', 'V11a_up', 'V11b_mx',
          'V11b_px', 'V11b_up', 'V11c_straight', 'VOICEPE_back_env', 'VOICEPE_encoder_env', 'VOICEPE_pcb', 'BME680_env_revD', 'TOUCH_pcb_100x44')
BACK = re.compile(r'(_v\d+|_[a-e]\d+[a-z0-9]*| \(\d+\))$')
PRE = ('REF_', 'TOOL_', 'INNER', 'RENDER_', 'AUD_')
rad = math.radians


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        Rc = X.body('SPKBOX_R')
        base = X.cp(Rc); X.sec(base, X.wbox(-110, -30, -70, 10, 75.0, 75.5))
        st['roof slice mm2'] = round(X.vol(base) / 0.5, 1)
        col = None
        for i in range(0, 14):                     # 0.5 slices from z 76.0 to 83.0, overlapping by nothing: stacked
            t = X.cp(base); X.move(t, 0, 0, 1.0 + 0.5 * i)
            col = t if col is None else X.uni(col, t)
        X.sec(col, X.wbox(-110, -30, -70, 10, 76.0, 82.0))
        st['column z 76..82 mm3'] = [round(X.vol(col), 1), col.lumps.count]
        cur = [b for b in X.root.bRepBodies if not (b.name in LEGACY or BACK.search(b.name) or b.name.startswith(PRE)) and b.name != 'SPKBOX_R']
        took = {}
        free = X.cp(col)
        for b in cur:
            if not free.boundingBox.intersects(b.boundingBox):
                continue
            v0 = X.vol(free)
            if b.name == 'HOUSING_F_front':
                S = X.cp(b); X.sec(S, X.wbox(-112, -28, -72, 14, 60.0, 100.0))
                for dy, dz in ((0.0, 0.0), (1.3, 0.0), (1.5, 0.0), (1.3, 5.0), (1.3, 10.0)):   # shell moved instead of the box: +y = box behind, +z = box below
                    t = X.cp(S); X.move(t, 0, dy, dz)
                    try:
                        X.tbm.booleanOperation(free, t, BT.DifferenceBooleanType)
                    except Exception:
                        took['shell FAIL dy%g dz%g' % (dy, dz)] = -1
            else:
                try:
                    X.tbm.booleanOperation(free, X.cp(b), BT.DifferenceBooleanType)
                except Exception:
                    took[b.name + ' FAIL'] = -1
            dv = v0 - X.vol(free)
            if dv > 0.05:
                took[b.name] = round(dv, 1)
        st['taken by'] = took
        st['free after bodies mm3'] = [round(X.vol(free), 1), [[l[0], l[1]] for l in X.lumps(free, 20000)[:5]]]
        status('g5c', st)
        H = (-58.0, -8.25, 79.5)
        C = None
        for ps in range(6, 15, 2):
            for dz in (0, 5):
                u = (math.sin(rad(ps)) * math.cos(rad(dz)), -math.cos(rad(ps)) * math.cos(rad(dz)), math.sin(rad(dz)))
                q = X.tbm.createCylinderOrCone(Wp(*H), 0.47, Wp(H[0] + 101 * u[0], H[1] + 101 * u[1], H[2] + 101 * u[2]), 0.47)
                C = q if C is None else X.uni(C, q)
        X.uni(C, X.cyly(H[0], H[2], 4.7, -22.0, -3.0))
        X.dif(free, C)
        # the tab and the screw's head stay free: nothing within 6 of the screw axis in front of y -22
        X.dif(free, X.wbox(-66.0, -50.0, -22.0, 0.0, 70.0, 90.0))
        lm = X.lumps(free, 20000)
        st['free after the key corridor mm3'] = [round(X.vol(free), 1), [[l[0], l[1]] for l in lm[:6]]]
        # plan extents of the free envelope at z 77 and z 81
        for z in (77.0, 81.0):
            sl = {}
            for y in (-50.0, -45.0, -40.0, -35.0, -30.0, -25.0, -20.0, -15.0, -12.0, -8.0):
                t = X.cp(free); X.sec(t, X.wbox(-110, -30, y - 0.05, y + 0.05, z - 0.1, z + 0.1))
                sl['y%g' % y] = [[l[1][0], l[1][1]] for l in X.lumps(t, 3000) if l[1]]
            st['free envelope at z %g: x extents per y' % z] = sl
        # the part of it that version 42's raised roof already used
        R42 = X.body('SPKBOX_R_v42')
        o42 = X.wbox(-101.0, -40.0, -60.0, 3.0, 76.0, 92.0)
        hull = X.cp(R42); X.sec(hull, X.cp(o42))
        st['free envelope inside v42 box material mm3'] = round(X.clash(free, R42), 1)
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-6:]
    st['t_end'] = round(time.time() - t0, 1)
    status('g5c', st)


run(None)
