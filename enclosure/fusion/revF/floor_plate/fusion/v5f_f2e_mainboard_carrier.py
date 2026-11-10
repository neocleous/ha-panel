# rev F f2e (2026-11-10): floor plate pass, block 2 - main board behind the display (pose confirmed by f2x), new carrier.
#   Main board (rev 2.1, 90 x 55): centre x_rel 2.55, Zd -28.5; back face 23.7 behind the LCD PCB (d 31.1), parts toward the door.
#     New bodies from the KiCad positions and MAIN_env heights (table of f2x): MAIN_pcb, MAIN_front_env, MAIN_back_env, MAIN_C7_env,
#     KO_C7_vent, MAIN_J2_plug_env. The old ones and MAIN_BRACKET are kept hidden as <name>_v42.
#   RESP_CARRIER (new): plate as before (x -40..45.4, Zd -56.9..2.2, d 15.2..17.2, notch x 28.75..36.95 above Zd -7.03) with ears under
#     four posts Ø7 to the board (x -38.95 / 44.05, Zd -9.5 / -52.5, Ø4.0 x 6.5 holes; the board has Ø2.7 holes for M2.5, so Ruthex M2.5), the ReSpeaker bosses and tie slots
#     4 mm lower, three Ø2.9 holes on the display's Pi standoffs (the fourth, (41.55, -51.93), lies under a post: the plate rests on it).
#   ReSpeaker: RESP_pcb, RESP_top_env, RESP_mic_env, RESP_usbc_plug_env moved 4 mm down the slab. Leads are not touched (block 3).
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
APPLY = globals().get('APPLY', False)
XCB, ZCB, DF = 2.55, -28.5, 32.7          # board centre, component face depth (back face 31.1)
PARTS = {
    'pcb': (0.0, 90.0, -5.0, 50.0, -1.6, 0.0),
    'back_NID': (9.75, 61.05, 0.75, 13.25, -4.5, -1.6), 'back_C5': (22.8, 32.8, 27.5, 37.5, -4.5, -1.6), 'back_C6': (10.5, 20.5, 14.0, 24.0, -4.5, -1.6),
    'back_C7': (47.9, 53.5, -4.84, 0.74, -4.5, -1.6), 'back_J1': (40.8, 49.2, 41.9, 48.7, -4.5, -1.6), 'back_J5': (69.0, 82.4, 0.6, 7.4, -4.5, -1.6),
    'back_J6': (34.3, 47.7, 20.6, 27.4, -4.5, -1.6), 'back_J8': (8.1, 14.9, 39.8, 48.2, -4.5, -1.6), 'back_J9': (73.8, 82.2, 40.6, 47.4, -4.5, -1.6),
    'back_J10': (61.65, 67.74, 0.92, 12.08, -4.5, -1.6), 'back_J3': (53.4, 65.6, 34.0, 38.5, -4.5, -1.6), 'back_J4': (44.0, 48.6, 34.0, 38.5, -4.5, -1.6),
    'back_J7': (53.1, 72.9, 41.0, 43.0, -4.5, -1.6), 'back_LK1': (26.2, 35.8, 45.3, 47.3, -4.5, -1.6), 'back_J2_body': (13.8, 26.2, 39.0, 50.0, -5.06, -1.6),
    'front_low': (0.0, 88.0, -5.0, 50.0, 0.0, 6.5), 'front_NID100': (9.75, 61.05, 0.75, 13.25, 0.0, 27.5), 'front_C5': (22.8, 32.8, 27.5, 37.5, 0.0, 16.0),
    'front_C6': (10.5, 20.5, 14.0, 24.0, 0.0, 16.0), 'front_J1': (40.8, 49.2, 41.9, 48.7, 0.0, 19.8), 'front_J5': (69.0, 82.4, 0.6, 7.4, 0.0, 19.8),
    'front_J6': (34.3, 47.7, 20.6, 27.4, 0.0, 19.8), 'front_J8': (8.1, 14.9, 39.8, 48.2, 0.0, 19.8), 'front_J9': (73.8, 82.2, 40.6, 47.4, 0.0, 19.8),
    'front_J10': (61.65, 67.74, 0.92, 12.08, 0.0, 16.5),
    'C7': (47.9, 53.5, -4.84, 0.74, 6.5, 12.5),        # above the 6.5 blanket of MAIN_front_env
    'C7vent': (47.9, 53.5, -4.84, 0.74, 12.5, 15.5), 'J2plug': (13.8, 26.2, 50.0, 70.0, -6.73, -0.23),
}
HOLES = [(3.5, 3.5), (86.5, 3.5), (3.5, 46.5), (86.5, 46.5)]
OLD = ['MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'MAIN_C7_env', 'KO_C7_vent', 'MAIN_BRACKET', 'RESP_CARRIER']
RESP = ['RESP_pcb', 'RESP_top_env', 'RESP_mic_env', 'RESP_usbc_plug_env']
CHK = ['HOUSING_F_front', 'HOUSING_F_door', 'HOUSING_F_cap', 'SLAB_frame', 'DOOR_tray', 'LCD_panel_body', 'LCD_pcb_76x110', 'LCD_components_env_d8.8',
       'LCD_panelFPC_conn_d9.5', 'SPKBOX_L', 'SPKBOX_R', 'PI5_F', 'PI5_F_cooler', 'FLOOR_PLATE', 'CRADLE_5807', 'PD_5807_env', 'GPIO_plugA_env',
       'GPIO_plugB_env', 'USBA_plug_env', 'USBA_cable_env', 'PIPWR_a_env', 'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR', 'KO_capkey_BL', 'KO_capkey_BR',
       'KO_capkey_SL', 'KO_capkey_SR', 'TOUCH_PCB', 'KO_touch_back']


def run(_context):
    st = {'apply': APPLY}
    t0 = time.time()

    def many(parts):
        t = parts[0]
        for q in parts[1:]:
            X.uni(t, q)
        return t

    def pb(k):
        kx0, kx1, ky0, ky1, d0, d1 = PARTS[k]
        return X.dbox(XCB - 45.0 + kx0, XCB - 45.0 + kx1, DF + d0, DF + d1, ZCB + 22.5 - ky1, ZCB + 22.5 - ky0)
    try:
        X = K()
        nm = X.names()
        if 'MAIN_pcb_v42' in nm:
            raise RuntimeError('already applied')
        st['missing'] = [n for n in OLD + RESP if n not in nm]
        hx = [(XCB - 45.0 + kx, ZCB + 22.5 - ky) for (kx, ky) in HOLES]
        # main board
        pcb = pb('pcb'); X.dif(pcb, many([X.cyld(x, z, 1.6, DF - 2.1, DF + 0.5) for (x, z) in hx]))
        new = {'MAIN_pcb': pcb, 'MAIN_front_env': many([pb(k) for k in PARTS if k.startswith('front_')]),
               'MAIN_back_env': many([pb(k) for k in PARTS if k.startswith('back_')]), 'MAIN_C7_env': pb('C7'), 'KO_C7_vent': pb('C7vent'),
               'MAIN_J2_plug_env': pb('J2plug')}
        # carrier
        c = X.dbox(-40.0, 45.4, 15.2, 17.2, -56.9, 2.2)
        add = []
        for (x, z) in hx:
            add.append(X.dbox(40.0, 47.8, 15.2, 17.2, z - 3.75, z + 3.75) if x > 0 else X.dbox(-42.7, -35.0, 15.2, 17.2, z - 3.75, z + 3.75))
            add.append(X.cyld(x, z, 3.5, 16.7, DF - 1.6))
        add += [X.cyld(-35.11, -16.42, 3.0, 16.7, 22.2), X.cyld(22.6, -45.34, 3.0, 16.7, 22.2)]
        for q in add:
            X.uni(c, q)
        cut = [X.dbox(28.75, 36.95, 14.7, 17.7, -7.03, 2.7)]
        cut += [X.cyld(x, z, 2.0, DF - 1.6 - 6.5, DF - 1.1) for (x, z) in hx]
        cut += [X.cyld(-35.11, -16.42, 0.8, 17.7, 22.7), X.cyld(22.6, -45.34, 0.8, 17.7, 22.7)]
        cut += [X.cyld(x, z, 1.45, 14.7, 17.7) for (x, z) in ((-16.45, -51.93), (-16.45, -2.93), (41.55, -2.93))]
        cut += [X.dbox(x0, x0 + 1.2, 14.7, 17.7, -25.0, -22.0) for x0 in (39.99, 36.59, -31.01, -34.41)]
        X.dif(c, many(cut))
        new['RESP_CARRIER'] = c
        # ReSpeaker 4 mm down the slab
        m = adsk.core.Matrix3D.create(); m.translation = V3(0, 0, -0.4)
        moved = {}
        for n in RESP:
            b = X.body(n)
            if b is not None:
                t = X.cp(b); X.tbm.transform(t, m); moved[n] = t
        st['vol'] = {k: round(X.vol(v), 1) for k, v in list(new.items()) + list(moved.items())}
        st['carrier_lumps'] = len(X.lumps(c))
        # checks: every new or moved body against the fixed parts and against each other
        cl = {}
        allnew = list(new.items()) + list(moved.items())
        for n in CHK:
            q = X.body(n)
            if q is None:
                cl[n] = 'missing'; continue
            for k, v in allnew:
                a = round(X.clash(v, q), 2)
                if a:
                    cl[k + '~' + n] = a
        for i, (k, v) in enumerate(allnew):
            for k2, v2 in allnew[i + 1:]:
                a = round(X.clash(v, v2), 2)
                if a:
                    cl[k + '~' + k2] = a
        st['clash'] = cl
        st['t_checks'] = round(time.time() - t0, 1)
        if APPLY:
            like = {n: X.body(n) for n in OLD + RESP}
            for n in OLD + RESP:
                if like[n] is not None:
                    X.retire(like[n])
            for k, v in allnew:
                src = like.get(k) or like.get('MAIN_front_env')
                X.add(v, k, like=src, show=not k.startswith('KO_'))
            st['added'] = {'dups': X.dups(), 'bodies': X.root.bRepBodies.count}
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status('f2e', st)


run(None)
