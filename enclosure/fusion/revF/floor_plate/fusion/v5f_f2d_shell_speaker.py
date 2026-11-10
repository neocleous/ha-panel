# rev F f2d (2026-11-10): floor plate pass, block 2 - the front shell's side of the new speaker fixing.
#   baffle land (y 0.7, x 47.5..93.5, z 5..51 each side): the four corner pads go; two stop bars (y 0, x 58..83, z 5.3..7.7 and 48.3..50.7)
#     carry the driver frame; head channels 8 wide to y 1.3 run up the two screw columns (x 52.75, 88.25) from below the land to the
#     upper screws, with pockets Ø8.4 to y 2.0 at the four screws (button heads 1.65 high, the unit rises 1.3 behind its place).
#   wall behind the screen: boss Ø8.4 along y at (±58.0, z 79.5), rear face y -3.9 (the box tab's front face), flat underside z 76.3,
#     Ø4.0 x 6.2 hole for a Ruthex M3 pressed in from the back.
#   DRV_screw_heads_env (new body): the eight button heads Ø5.7 x 1.65 in front of the driver frames, for the checks.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
APPLY = globals().get('APPLY', False)
ZL, ZU = 10.25, 45.75
CHK = ['SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'FLOOR_PLATE', 'HOUSING_F_cap', 'SLAB_frame', 'TOUCH_PCB', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'KO_touch_back',
       'LCD_panel_body', 'LCD_pcb_76x110', 'LCD_components_env_d8.8', 'LCD_panelFPC_conn_d9.5', 'LEAD_TOUCH', 'LEAD_DSI', 'LEAD_SPK_L', 'LEAD_SPK_R']


def run(_context):
    st = {'apply': APPLY}
    t0 = time.time()

    def many(parts):
        t = parts[0]
        for q in parts[1:]:
            X.uni(t, q)
        return t
    try:
        X = K()
        if X.body('DRV_screw_heads_env') is not None:
            raise RuntimeError('already applied')
        front = X.body('HOUSING_F_front')
        add = []; cut = []; heads = []
        for sx in (1.0, -1.0):
            add += [X.wbox(sx * 58.0, sx * 83.0, 0.0, 1.2, 5.3, 7.7), X.wbox(sx * 58.0, sx * 83.0, 0.0, 1.2, 48.3, 50.7)]
            boss = X.cyly(sx * 58.0, 79.5, 4.2, -3.9, 0.5); X.sec(boss, X.wbox(sx * 50.0, sx * 66.0, -6.0, 3.0, 76.3, 90.0)); add.append(boss)
            cut.append(X.cyly(sx * 58.0, 79.5, 2.0, -4.4, 2.3))
            for xc in (52.75, 88.25):
                cut.append(X.wbox(sx * (xc - 4.0), sx * (xc + 4.0), -0.5, 1.3, 4.0, ZU))
                for z in (ZL, ZU):
                    cut.append(X.cyly(sx * xc, z, 4.2, -0.5, 2.0))
                    heads.append(X.cyly(sx * xc, z, 2.85, 0.0, 1.65))
        addt = many(add); cutt = many(cut); headt = many(heads)
        s = X.cp(front); v0 = X.vol(s)
        X.uni(s, X.cp(addt)); v1 = X.vol(s)
        X.dif(s, X.cp(cutt)); v2 = X.vol(s)
        st['shell_mm3'] = [round(v0, 1), round(v1 - v0, 1), round(v2 - v1, 1), round(v2, 1)]
        st['lumps'] = [l[0] for l in X.lumps(s)]
        st['t_shell'] = round(time.time() - t0, 1); status('f2d', st)
        cl = {'heads~shell': round(X.clash(headt, s), 3)}
        for n in CHK:
            q = X.body(n)
            if q is None:
                cl[n] = 'missing'; continue
            v = [round(X.clash(addt, q), 2), round(X.clash(headt, q), 2)]
            if any(v):
                cl[n] = v
        st['clash[bars+bosses, heads]'] = cl
        # remaining wall in front of the pockets and behind the insert holes (thinnest), from the shell copy
        st['t_checks'] = round(time.time() - t0, 1)
        if APPLY:
            front.deleteMe()
            nb = X.add(s, 'HOUSING_F_front', like=X.body('HOUSING_F_front_v42'))
            hb = X.add(headt, 'DRV_screw_heads_env', like=X.body('SPK_L'))
            st['added'] = {'HOUSING_F_front': [round(nb.volume * 1000, 1), nb.lumps.count], 'heads': hb.lumps.count, 'dups': X.dups(),
                           'bodies': X.root.bRepBodies.count}
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status('f2d', st)


run(None)
