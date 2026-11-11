# rev F h2b (2026-11-11): step 3, block 2 - the carrier rebuilt for main board rev 3.
#   Kept from the carrier of f2e: plate x_rel -40.0..45.4, Zd -56.9..2.2, depth 15.2..17.2; the notch over the display's 4-pin power header
#   (x_rel 28.75..36.95 above Zd -7.03); the two ReSpeaker bosses dia 6 with dia 1.6 pilots (M2 x 6 screws for plastic); the four tie slots.
#   New: posts dia 8 from the plate to the board's back face (depth 31.1) at the board's holes, each with a hole dia 4.0 x 6.7 for a
#   Ruthex M3 x 5.7 (the unit's standard: M3 x 8 through the 1.6 board reaches 6.4 into the post); holes dia 2.9 on all FOUR of the
#   display's mounting points (the old carrier had three: one lay under a post); no ears outside the plate.
#   POSTS (board frame u, v) comes from the loader. H2 (30.0, 25.0) cannot have a post: it stands on the display's power header and its
#   plug, where the plate has its notch (h2a) - open with Daniel; this script builds what it is given.
#   Dry by default: volume, lumps, overlaps. APPLY=True: RESP_CARRIER -> RESP_CARRIER_v48 (hidden), the new one added.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_h_lib.py'), encoding='utf-8').read())
APPLY = globals().get('APPLY', False)
POSTS = globals().get('POSTS', {'H1': (-37.0, 22.0), 'H3': (-31.0, -25.25), 'H4': (31.0, -25.25)})
TOPS = globals().get('TOPS', {})                 # post name -> (land dia, set-back) for a stepped top
MOUNT = [(-16.45, -51.93), (-16.45, -2.93), (41.55, -2.93), (41.55, -51.93)]      # x_rel, Zd
BOSS = [(-35.11, -16.42), (22.6, -45.34)]
SLOTS = (39.99, 36.59, -31.01, -34.41)
BACK_D = 31.1
CHK = ['LCD_panel_body', 'LCD_pcb_76x110', 'LCD_M2.5_standoff_d9.0', 'LCD_Pi_standoff_d15.2', 'LCD_pogo_header_d14.1', 'LCD_2x2_header_d15.4', 'LCD_pins_d16.0',
       'LCD_DSI_conn_d9.3', 'LCD_panelFPC_conn_d9.5', 'LCD_touchFPC_conn_d9.3', 'LCD_components_env_d8.8', 'RESP_pcb', 'RESP_top_env', 'RESP_mic_env',
       'RESP_usbc_plug_env', 'MAIN_pcb', 'MAIN_PS1', 'MAIN_conn', 'MAIN_tall', 'MAIN_low', 'MAIN_J2_plug_env', 'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR',
       'SLAB_frame', 'SPKBOX_L', 'SPKBOX_R', 'HOUSING_F_cap']


def build(X):
    c = X.dbox(-40.0, 45.4, 15.2, 17.2, -56.9, 2.2)
    for (x, z) in BOSS:
        X.uni(c, X.cyld(x, z, 3.0, 16.7, 22.2))
    for h, (u, v) in POSTS.items():
        X.uni(c, cyl_b(X, u, v, 4.0, 16.7 - D0, BACK_D - D0))
    cut = [X.dbox(28.75, 36.95, 14.7, 17.7, -7.03, 2.7)]
    cut += [cyl_b(X, u, v, 2.0, BACK_D - 6.7 - D0, BACK_D + 0.5 - D0) for h, (u, v) in POSTS.items()]
    cut += [X.cyld(x, z, 0.8, 17.7, 22.7) for (x, z) in BOSS]
    cut += [X.cyld(x, z, 1.45, 14.7, 17.7) for (x, z) in MOUNT]
    cut += [X.dbox(x0, x0 + 1.2, 14.7, 17.7, -25.0, -22.0) for x0 in SLOTS]
    for h, (land, back) in TOPS.items():
        u, v = POSTS[h]
        ring = cyl_b(X, u, v, 4.5, BACK_D - back - D0, BACK_D + 0.5 - D0)
        X.dif(ring, cyl_b(X, u, v, land / 2.0, BACK_D - back - 0.5 - D0, BACK_D + 1.0 - D0))
        cut.append(ring)
    for q in cut:
        X.dif(c, q)
    return c


def run(_context):
    st = {'apply': APPLY, 'posts': POSTS, 'tops': TOPS}
    t0 = time.time()
    try:
        X = K()
        if 'RESP_CARRIER_v48' in X.names():
            raise RuntimeError('already applied')
        c = build(X)
        st['vol'] = round(X.vol(c), 1); st['lumps'] = c.lumps.count; st['box'] = bbb(c)
        cl = {}
        for n in CHK:
            b = X.body(n)
            if b is None:
                cl[n] = 'missing'; continue
            a = xvol(X, c, tcopy(X, n))
            if abs(a) > 0.005:
                cl[n] = round(a, 2)
        sh = cache().get('crop_front_site')
        if sh is not None:
            cl['shell (cropped)'] = round(xvol(X, c, sh), 2)
        heads = X.cyld(MOUNT[0][0], MOUNT[0][1], 2.5, 17.2, 19.7)
        for (x, z) in MOUNT[1:]:
            X.uni(heads, X.cyld(x, z, 2.5, 17.2, 19.7))
        cl['M2.5 heads dia 5.0 x 2.5'] = round(xvol(X, heads, c), 2)
        cl['M2.5 heads vs ReSpeaker'] = round(sum(max(0.0, xvol(X, heads, tcopy(X, n))) for n in ('RESP_pcb', 'RESP_top_env', 'RESP_mic_env')), 2)
        st['clash'] = cl
        st['leads'] = {b.name: round(xvol(X, c, tcopy(X, b.name)), 1) for b in current(X, leads=True) if b.name.startswith('LEAD_') and c.boundingBox.intersects(b.boundingBox)}
        if APPLY:
            old = X.body('RESP_CARRIER')
            b = X.root.bRepBodies.add(c); b.name = 'NEW_RESP_CARRIER'
            try:
                b.appearance = old.appearance
            except Exception:
                pass
            X.retire(old, '_v48')
            b.name = 'RESP_CARRIER'; b.isLightBulbOn = True
            st['added'] = {'dups': X.dups(), 'bodies': X.root.bRepBodies.count, 'vol': round(X.vol(b), 1), 'lumps': b.lumps.count}
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('h2b_apply' if APPLY else 'h2b', st)


run(None)
