# rev F g6a (2026-11-10): right speaker box - new raised roof over the free area beside the box-top screw's key path (Daniel 23:07: option 1).
#   Envelope = the box's own outline at its roof (slice z 75.0..75.5) carried up from z 75.5 to z 82.0, less every present body, less the
#   shell in its lift-in positions (box 1.05 / 1.3 / 1.5 behind, and 5 / 10 / 30 below at 1.3 behind) each with 0.3 of play in x, y and z, less
#   the key corridor (2.0 key from the head (-58, -8.25, 79.5), 6..14 deg toward the middle, 0 or 5 deg up, 2.0 clear + 1.5 wall = r 4.7), less the
#   tab zone (x -66..-50, y -22..0). The largest piece of that is the new roof's outer shape. Inside: walls 1.5 (shape moved 1.62 in eight
#   directions and intersected), roof 1.5 (air to z 80.5), the old ceiling (z 74.5..76) opened under it.
# Dry by default; APPLY=True hides the old box as SPKBOX_R_v46 and adds the new one.
import os, re
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
LEGACY = ('DOOR_tray', 'HOUSING_E', 'HOUSING_shell', 'HOUSING_F_wip', 'AMP_env_20x20x10', 'BUCK_20to5V_env_43x25x13', 'DOOR_plate_revE', 'GROMMET_usbc',
          'HOUSING_F_front_d10_sliver', 'HOUSING_F_front_d12a_sliver1', 'LD2410C_env', 'MAIN_BRACKET_d1split_L', 'MAIN_BRACKET_d1split_R',
          'MAIN_BRACKET_d1split_plug', 'PD_trigger_env_20V', 'PI5_board', 'SPKBOX_L_r2', 'SPK_driver_D40', 'V11a_mx', 'V11a_px', 'V11a_up', 'V11b_mx',
          'V11b_px', 'V11b_up', 'V11c_straight', 'VOICEPE_back_env', 'VOICEPE_encoder_env', 'VOICEPE_pcb', 'BME680_env_revD', 'TOUCH_pcb_100x44')
BACK = re.compile(r'(_v\d+|_[a-e]\d+[a-z0-9]*| \(\d+\))$')
PRE = ('REF_', 'TOOL_', 'INNER', 'RENDER_', 'AUD_')
PCIN = adsk.fusion.PointContainment.PointInsidePointContainment
APPLY = globals().get('APPLY', False)
rad = math.radians
HEAD = (-58.0, -8.25, 79.5)                 # not H: the library's H is the frame constant 143.3
ZT, ZA, WALL = 82.0, 80.5, 1.62


def run(_context):
    st = {'apply': APPLY}
    t0 = time.time()
    name = 'g6a_apply' if APPLY else 'g6a_dry'
    try:
        X = K()
        nm = X.names()
        try:
            st['version'] = X.doc.dataFile.versionNumber
        except Exception:
            st['version'] = None
        if any(n.startswith(('AUD_', 'RENDER_tmp_')) for n in nm) or 'SPKBOX_R_v46' in nm:
            raise RuntimeError('state: templates present or already applied')
        Rc = X.body('SPKBOX_R')
        if abs(X.vol(Rc) - 25622.0) > 0.3:
            raise RuntimeError('guard SPKBOX_R %.1f' % X.vol(Rc))

        def corridor(r):
            c = None
            for ps in range(6, 15, 2):
                for dz in (0, 5):
                    u = (math.sin(rad(ps)) * math.cos(rad(dz)), -math.cos(rad(ps)) * math.cos(rad(dz)), math.sin(rad(dz)))
                    q = X.tbm.createCylinderOrCone(Wp(*HEAD), r / 10.0, Wp(HEAD[0] + 101 * u[0], HEAD[1] + 101 * u[1], HEAD[2] + 101 * u[2]), r / 10.0)
                    c = q if c is None else X.uni(c, q)
            return c

        def chamber(B):
            Rb = [-101.0, -40.0, -60.0, 3.0, 1.0, 92.0]
            A = X.wbox(*Rb)
            X.dif(A, X.cp(B)); X.dif(A, X.wbox(Rb[0], Rb[1], -3.7, -3.0, Rb[4], Rb[5]))
            X.dif(A, X.cyly(-62.0, 30.0, 2.2, -53.5, -49.0))
            pc = Wp(-70.5, -30.0, 62.0)
            for L in A.lumps:
                try:
                    if L.pointContainment(pc) == PCIN:
                        t = X.cp(L); bb = X.lumps(X.cp(t), 100000)[0][1]
                        return t, bb is not None and all(abs(bb[i] - Rb[i]) > 0.05 for i in range(6)), bb
                except Exception:
                    pass
            return None, False, None

        base = X.cp(Rc); X.sec(base, X.wbox(-110, -30, -70, 10, 75.0, 75.5))
        col = None
        for i in range(0, 14):
            t = X.cp(base); X.move(t, 0, 0, 0.5 + 0.5 * i)
            col = t if col is None else X.uni(col, t)
        X.sec(col, X.wbox(-110, -30, -70, 10, 75.5, ZT))
        st['column'] = [round(X.vol(col), 1), col.lumps.count]
        cur = [b for b in X.root.bRepBodies if not (b.name in LEGACY or BACK.search(b.name) or b.name.startswith(PRE)) and b.name != 'SPKBOX_R']
        free = X.cp(col); took = {}
        S = X.cp(X.body('HOUSING_F_front')); X.sec(S, X.wbox(-112, -28, -72, 14, 40.0, 100.0))
        for b in cur:
            if not free.boundingBox.intersects(b.boundingBox):
                continue
            v0 = X.vol(free)
            if b.name == 'HOUSING_F_front':
                for (by, bz) in ((0.0, 0.0), (1.05, 0.0), (1.3, 0.0), (1.5, 0.0), (1.3, 5.0), (1.3, 10.0), (1.3, 30.0)):
                    for (jx, jy, jz) in ((0, 0, 0), (0.3, 0, 0), (-0.3, 0, 0), (0, 0.3, 0), (0, -0.3, 0), (0, 0, 0.3), (0, 0, -0.3)):
                        t = X.cp(S); X.move(t, jx, by + jy, bz + jz)
                        try:
                            X.tbm.booleanOperation(free, t, BT.DifferenceBooleanType)
                        except Exception:
                            took['shell FAIL %g %g %g %g %g' % (by, bz, jx, jy, jz)] = -1
            else:
                try:
                    X.tbm.booleanOperation(free, X.cp(b), BT.DifferenceBooleanType)
                except Exception:
                    took[b.name + ' FAIL'] = -1
            dv = v0 - X.vol(free)
            if dv > 0.05:
                took[b.name] = round(dv, 1)
        st['taken by'] = took
        C47 = corridor(4.7); X.uni(C47, X.cyly(HEAD[0], HEAD[2], 4.7, -22.0, -3.0))
        X.dif(free, C47); X.dif(free, X.wbox(-66.0, -50.0, -22.0, 0.0, 70.0, 90.0))
        big = None
        for L in free.lumps:
            if big is None or L.volume > big.volume:
                big = L
        Ho = X.cp(big)
        st['outer shape'] = [round(X.vol(Ho), 1), X.lumps(X.cp(Ho), 20000)[0][1], free.lumps.count]
        status(name, st)
        A2 = X.cp(Ho)
        for k in range(8):
            a = math.pi / 4 * k
            t = X.cp(Ho); X.move(t, WALL * math.cos(a), WALL * math.sin(a), 0.0)
            X.sec(A2, t)
        X.sec(A2, X.wbox(-110, -30, -70, 10, 75.5, ZA))
        st['air shape above z 75.5'] = [round(X.vol(A2), 1), A2.lumps.count]
        Cc = X.cp(A2); t = X.cp(A2); X.move(t, 0, 0, -1.1); X.uni(Cc, t)
        new = X.cp(Rc); X.uni(new, X.cp(Ho)); X.dif(new, Cc)
        st['box'] = {'vol': [round(X.vol(Rc), 1), round(X.vol(new), 1)], 'lumps': new.lumps.count}
        a0, s0, b0 = chamber(Rc); a1, s1, b1 = chamber(new)
        st['chamber air cm3 before / after'] = [round(X.vol(a0) / 1000.0, 3), None if a1 is None else round(X.vol(a1) / 1000.0, 3)]
        st['sealed before / after'] = [s0, s1]; st['air bbox after'] = b1
        spk = X.body('SPK_R')
        if a1 is not None:
            s = X.cp(spk); X.sec(s, X.cp(a1)); st['lower bound cm3 after'] = round((X.vol(a1) - X.vol(s)) / 1000.0, 3)
        status(name, st)
        add = X.cp(new); X.dif(add, X.cp(Rc))
        st['added material'] = [round(X.vol(add), 1), add.lumps.count]
        hits = {}
        for b in cur:
            v = X.clash(add, b)
            if abs(v) > 0.005:
                hits[b.name] = round(v, 2)
        st['added material against the present bodies'] = hits
        lift = {}
        for (by, bz) in ((0.0, 0.0), (1.05, 0.0), (1.3, 0.0), (1.5, 0.0), (1.3, 2.0), (1.3, 5.0), (1.3, 10.0), (1.3, 20.0), (1.3, 30.0), (0.65, 0.0)):
            t = X.cp(S); X.move(t, 0, by, bz)
            lift['%g behind, %g below' % (by, bz)] = round(X.clash(add, t), 3)
        st['added material against the shell in the lift-in positions'] = lift
        C32 = corridor(3.2)
        st['new box inside the key corridor (2.0 clear), without the tab'] = round(X.clash(C32, new), 2)
        # sections: wall and roof thickness
        sec = {}

        def needle(axis, a0_, a1_, c1, c2):
            if axis == 'x':
                n = X.wbox(a0_, a1_, c1 - 0.02, c1 + 0.02, c2 - 0.02, c2 + 0.02)
            elif axis == 'y':
                n = X.wbox(c1 - 0.02, c1 + 0.02, a0_, a1_, c2 - 0.02, c2 + 0.02)
            else:
                n = X.wbox(c1 - 0.02, c1 + 0.02, c2 - 0.02, c2 + 0.02, a0_, a1_)
            X.tbm.booleanOperation(n, new, BT.IntersectionBooleanType)
            i = {'x': 0, 'y': 2, 'z': 4}[axis]
            return sorted([[l[1][i], l[1][i + 1]] for l in X.lumps(n, 400) if l[1]])
        for y in (-45.0, -30.0, -15.0):
            sec['along x at y %g, z 78' % y] = needle('x', -98.0, -44.0, y, 78.0)
        for x in (-85.0, -75.0, -65.0):
            sec['along y at x %g, z 78' % x] = needle('y', -56.0, 0.0, x, 78.0)
        sec['up at (-75, -30)'] = needle('z', 70.0, 84.0, -75.0, -30.0)
        sec['up at (-62, -40)'] = needle('z', 70.0, 84.0, -62.0, -40.0)
        st['sections of the new box'] = sec
        if APPLY:
            X.retire(Rc, '_v46')
            nb = X.add(new, 'SPKBOX_R', like=Rc, show=True)
            st['applied'] = [round(X.vol(nb), 1), nb.lumps.count, nb.isLightBulbOn]; st['dups'] = X.dups(); st['n_bodies'] = len(X.names())
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-6:]
    st['t_end'] = round(time.time() - t0, 1)
    status(name, st)


run(None)
