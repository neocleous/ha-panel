# rev F f2b (2026-11-10): floor plate pass, block 2 - the base plate and the front shell without its floor.
#   FLOOR_PLATE (new): REF_F_outer below z 2.5 (the whole underside out to the body surface) with the floor's features
#     (foot recesses, door-screw holes + counterbores + pads, intake field, Pi posts, cradle posts), the box pads with
#     slotted holes, two tongues, rest pads for the shell.
#   HOUSING_F_front: floor-standing features removed (Pi posts, cradle posts, the zip-tie anchor at (58.5, -56.5)), two lips for the
#     tongues added, cut at z 2.8, the cove removed along the sides (|x| >= 46.2, y <= 0.5, up to z 5.6) so the boxes can rise past.
#     The cove tool is (INNER_E - TOOL_inner_skin_0p7); its top must stay at or below 5.6: at 5.95 and above the boolean fails
#     (the cove runs out tangent to the wall at z 6.0, and above 6.5 the wall stands 0.02 proud of the tool face) - f2b1 probe.
#   APPLY False (default): everything on TemporaryBRep bodies, nothing changed. APPLY True: deletes the AUD_* templates,
#   adds FLOOR_PLATE, swaps HOUSING_F_front (old one hidden as HOUSING_F_front_v42).
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
APPLY = globals().get('APPLY', False)
PIP = [(18.35, -5.5), (-39.65, -5.5), (18.35, -54.5), (-39.65, -54.5)]
CRA = [(6.5, -72.5), (-1.5, -72.5)]
FEET = [(80.0, -11.5), (-80.0, -11.5), (30.0, -69.0), (-30.0, -69.0)]
DOOR = [(19.0, -74.5), (-19.0, -77.0), (50.0, -67.0), (-50.0, -67.0)]
BOXSCR = [(51.0, -11.2), (64.0, -44.2), (-51.0, -11.2), (-72.0, -37.2)]     # slot centres = insert axis + 0.8 (travel 2.4)
BOXPAD = [(82.0, -30.0), (-82.0, -30.0)]
TONG = [(24.5, 35.5), (-35.5, -24.5)]
LIPX = [(23.5, 36.5), (-36.5, -23.5)]
REST = [(8.0, 18.0), (-18.0, -8.0)]
COVE_TOP = globals().get('COVE_TOP', 5.6)
CUR = ['HOUSING_F_door', 'HOUSING_F_cap', 'SPKBOX_L', 'SPKBOX_R', 'PI5_F', 'PI5_F_cooler', 'CRADLE_5807', 'PD_5807_env', 'GROMMET_usbc_F',
       'TOUCH_PCB', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'GPIO_plugA_env', 'GPIO_plugB_env', 'USBA_plug_env', 'USBA_cable_env', 'PIPWR_a_env',
       'FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR', 'SPK_L', 'SPK_R', 'SLAB_frame', 'KO_touch_back', 'MAIN_BRACKET', 'LEAD_PI_POWER',
       'LEAD_DSI', 'LEAD_GPIO_A', 'LEAD_GPIO_B', 'LEAD_TOUCH', 'LEAD_SPK_L', 'LEAD_SPK_R', 'LEAD_USB_RESP']


def run(_context):
    st = {'t0': time.strftime('%Y-%m-%d %H:%M:%S'), 'apply': APPLY}
    t0 = time.time()

    def mark(k, v=None):
        st[k] = v if v is not None else round(time.time() - t0, 1)
        status('f2b', st)

    def many(parts):                                  # union of temporary solids into one tool
        t = parts[0]
        for q in parts[1:]:
            X.uni(t, q)
        return t
    try:
        X = K()
        nm = X.names()
        st['state'] = {'version': X.doc.dataFile.versionNumber, 'bodies': len(nm), 'aud': len([n for n in nm if n.startswith('AUD_')])}
        if 'FLOOR_PLATE' in nm or 'HOUSING_F_front_v42' in nm:
            raise RuntimeError('already applied')
        front = X.body('HOUSING_F_front'); ref = X.body('REF_F_outer')
        # ---------------- plate ----------------
        p = X.cp(ref)
        X.sec(p, X.wbox(-130, 130, -110, 40, -1.0, 2.5))
        st['blank_mm3'] = round(X.vol(p), 1)
        for (x, y) in DOOR:
            X.uni(p, X.cylz(x, y, 4.0, 1.0, 2.8))
        for (x, y) in PIP:
            X.uni(p, X.cylz(x, y, 3.8, 1.0, 7.5)); X.uni(p, X.cylz(x, y, 3.4, 7.3, 8.0)); X.uni(p, X.cylz(x, y, 4.6, 2.0, 3.2, 3.75))
        for (x, y) in CRA:
            X.uni(p, X.cylz(x, y, 4.0, 1.0, 8.0)); X.uni(p, X.cylz(x, y, 4.8, 2.0, 3.3, 3.95))
        for (x, y) in BOXSCR:
            X.uni(p, X.obz(x, y, 4.0, 2.4, 1.0, 3.7))
        for (x, y) in BOXPAD:
            X.uni(p, X.cylz(x, y, 4.0, 1.0, 3.7))
        for (x0, x1) in TONG:
            X.uni(p, X.wbox(x0, x1, -0.9, 1.15, 2.0, 5.25)); X.uni(p, X.wbox(x0, x1, 0.8, 3.0, 4.35, 5.25))     # stop: 0.15 to the lip
        for (x0, x1) in REST:
            X.uni(p, X.wbox(x0, x1, 1.9, 4.0, 2.4, 2.8))
        for (x, y) in FEET:
            X.dif(p, X.cylz(x, y, 6.5, -0.5, 0.5))
        for (x, y) in DOOR:
            X.dif(p, X.cylz(x, y, 1.7, -1.0, 4.0)); X.dif(p, X.cylz(x, y, 3.25, -1.0, 1.0))
        for (x, y) in PIP:
            X.dif(p, X.cylz(x, y, 2.0, 1.5, 9.0))
        for (x, y) in CRA:
            X.dif(p, X.cylz(x, y, 2.0, 2.3, 9.0))
        for (x, y) in BOXSCR:
            X.dif(p, X.obz(x, y, 1.7, 2.4, -1.0, 5.0)); X.dif(p, X.obz(x, y, 3.25, 2.4, -1.0, 1.0))
        cen = json.load(open(os.path.join(FP, 'f2a_intake.json')))
        X.dif(p, many([X.cylz(x, y, 1.0, -1.0, 3.5) for (x, y) in cen]))
        st['intake'] = len(cen)
        mark('t_plate')
        # ---------------- shell ----------------
        s = X.cp(front); v0 = X.vol(s)
        lips = many([X.wbox(x0, x1, 1.3, 4.6, 2.0, 4.2) for (x0, x1) in LIPX])
        X.uni(s, X.cp(lips)); v1 = X.vol(s)
        cut = [X.wbox(-130, 130, -110, 40, -2.0, 2.8), X.wbox(54.7, 62.3, -59.0, -54.0, 2.0, 8.5)]
        cut += [X.cylz(x, y, 5.0, 2.0, 8.6) for (x, y) in PIP] + [X.cylz(x, y, 5.4, 2.0, 8.6) for (x, y) in CRA]
        X.dif(s, many(cut)); v2 = X.vol(s)
        mark('t_shell_floor')
        inner = X.body('INNER_E'); skin = X.body('TOOL_inner_skin_0p7')
        core = X.cp(inner)
        X.sec(core, many([X.wbox(sx * 46.2, sx * 110.0, -75.0, 0.5, 2.3, COVE_TOP) for sx in (1.0, -1.0)]))
        X.dif(core, X.cp(skin))
        st['core'] = X.lumps(core)
        X.dif(s, core); v3 = X.vol(s)
        st['shell_mm3'] = {'v42': round(v0, 1), 'lips': round(v1 - v0, 1), 'floor_posts_anchor': round(v2 - v1, 1), 'coves': round(v3 - v2, 1),
                           'new': round(v3, 1)}
        st['shell_lumps'] = X.lumps(s)[:12]
        mark('t_shell_cove')
        # rest pads under the side walls' rear ends: the inner part of the shell's own edge (0.6 in from the outside), 0.3 high
        sl = X.cp(s)
        X.sec(sl, many([X.wbox(sx * 74.0, sx * 92.0, -52.5, -47.5, 2.8, 3.2) for sx in (1.0, -1.0)]))
        st['rear_edge'] = X.lumps(sl)
        pads = None
        for sx in (1.0, -1.0):
            a = X.cp(sl); X.sec(a, X.wbox(0.0, sx * 120.0, -60, -40, 2.0, 4.0))
            b = X.cp(a); X.move(b, dx=-sx * 0.6); X.sec(a, b)
            pads = a if pads is None else X.uni(pads, a)
        X.move(pads, dz=-0.4)
        st['rear_pads'] = X.lumps(pads)
        X.uni(p, pads)
        st['plate_mm3'] = round(X.vol(p), 1)
        st['plate_lumps'] = X.lumps(p)[:6]
        mark('t_pads')
        # ---------------- checks on the temporary bodies ----------------
        # the shell only lost material except for the lips, so the lips stand in for it (a copy of the shell costs 13 s)
        cl = {'plate~shell': round(X.clash(p, s), 3), 'v42 shell~TOUCH_PCB': round(X.clash(X.body('TOUCH_PCB'), front), 2)}
        for n in CUR:
            b = X.body(n)
            if b is None:
                cl[n] = 'missing'; continue
            a = round(X.clash(p, b), 2); c = round(X.clash(lips, b), 2)
            if a or c:
                cl[n] = [a, c]
        st['clash_plate_lips'] = cl
        mark('t_checks')
        if APPLY:
            for b in [b for b in X.root.bRepBodies if b.name.startswith('AUD_')]:
                b.deleteMe()
            X.retire(front)
            nb = X.add(s, 'HOUSING_F_front', like=front)
            pb = X.add(p, 'FLOOR_PLATE', like=front)
            st['added'] = {'HOUSING_F_front': [round(nb.volume * 1000, 1), nb.lumps.count], 'FLOOR_PLATE': [round(pb.volume * 1000, 1), pb.lumps.count],
                           'aud_left': [n for n in X.names() if n.startswith('AUD_')], 'dups': X.dups(), 'bodies': X.root.bRepBodies.count}
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status('f2b', st)


run(None)
