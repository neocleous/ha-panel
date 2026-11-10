# rev F f2c (2026-11-10): floor plate pass, block 2 - speaker boxes reworked, base plate rebuilt for them.
# Found by the probes f2c0..f2c4:
#   - a driver screwed to its box has screw heads in front of its frame, so the unit cannot rise 0.4 behind its place (the baffle land
#     is at y 0.7). The boxes can sit 1.4 behind their place at full height without touching the shell (first contact at 1.5: the
#     rear lip at y -53.5). So: boxes screwed rigidly to the plate (round holes, no slots), the whole unit rises 1.3 back and slides
#     1.3 forward; driver screws are button heads (1.65); the shell gets shallow head channels and pockets (f2d).
#   - SPKBOX_R is not the mirror of SPKBOX_L (microSD channel, inboard relief, hump): each box is edited on its own.
# Boxes: upper tube removed (stubs stay at the walls), its bores plugged; lower tube kept, plugged to y -19; Ø2.5 pilots at the four
#   frame corners (relief 0.35 at the mouth), bosses behind the outboard corners, pegs removed; two floor bosses with Ø4.0 insert holes
#   from below; wire hole Ø4.0 (F6); tab on the roof with a Ø3.6 hole at (±58, z 79.5); -x box: hump removed, roof closed.
# Plate: as f2b, with round box-screw holes at the insert axes, plain pads to z 6.5 under the boxes' raised floor, tongue noses to y 2.35.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
APPLY = globals().get('APPLY', False)
PIP = [(18.35, -5.5), (-39.65, -5.5), (18.35, -54.5), (-39.65, -54.5)]
CRA = [(6.5, -72.5), (-1.5, -72.5)]
FEET = [(80.0, -11.5), (-80.0, -11.5), (30.0, -69.0), (-30.0, -69.0)]
DOOR = [(19.0, -74.5), (-19.0, -77.0), (50.0, -67.0), (-50.0, -67.0)]
BOXSCR = {'L': [(51.0, -14.0, 11.2), (64.0, -45.0, 11.2)], 'R': [(-51.0, -14.0, 12.2), (-72.0, -38.0, 11.2)]}   # insert axis x, y, boss top
BOXPAD = [(82.0, -30.0), (-82.0, -30.0)]          # top 3.7: the boxes' raised underside (6.5) is only the 4.5 band along the wall
TONG = [(24.5, 35.5), (-35.5, -24.5)]
REST = [(8.0, 18.0), (-18.0, -8.0)]
ZL, ZU = 10.25, 45.75
CHK = ['HOUSING_F_front', 'HOUSING_F_door', 'HOUSING_F_cap', 'PI5_F', 'PI5_F_cooler', 'CRADLE_5807', 'PD_5807_env', 'TOUCH_PCB', 'TOUCH_CLIP_L',
       'TOUCH_CLIP_R', 'GPIO_plugA_env', 'GPIO_plugB_env', 'USBA_plug_env', 'USBA_cable_env', 'PIPWR_a_env', 'FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR',
       'SPK_L', 'SPK_R', 'SLAB_frame', 'KO_touch_back', 'LEAD_PI_POWER', 'LEAD_DSI', 'LEAD_GPIO_A', 'LEAD_GPIO_B', 'LEAD_TOUCH', 'LEAD_SPK_L',
       'LEAD_SPK_R', 'LEAD_USB_RESP']


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
        nm = X.names()
        if 'SPKBOX_L_v42' in nm or 'FLOOR_PLATE' not in nm:
            raise RuntimeError('state: boxes already done or no plate')
        front = X.body('HOUSING_F_front'); ref = X.body('REF_F_outer')
        # ---------------- boxes ----------------
        new = {}
        for side, sg in (('L', 1.0), ('R', -1.0)):
            old = X.body('SPKBOX_' + side); b = X.cp(old); v0 = X.vol(b); log = {}
            xi, xo, xt = sg * 52.75, sg * 88.25, sg * 58.0
            if side == 'R':
                try:
                    X.dif(b, X.wbox(-100, -40, -56, 0, 76.0, 95.0)); zt = 76.0
                except Exception:
                    b = X.cp(old); X.dif(b, X.wbox(-94.5, -45.0, -53.0, -9.3, 75.7, 95.0)); zt = 75.4
                log['hump'] = [round(X.vol(b) - v0, 1), zt]; v1 = X.vol(b)
                # the hump's outboard end follows the wall: its inner edge runs (-91.0, -11.5) -> (-88.2, -22.5); a slab along that line
                # (0.6 into the wall, 4.0 inward) closes the taper, a plain box the rest
                ux, uy = 0.2467, -0.9691
                ob = adsk.core.OrientedBoundingBox3D.create(Wp(-87.95, -16.58, (74.0 + zt) / 2.0), V3(ux, uy * C, -uy * S), V3(-uy, ux * C, -ux * S),
                                                            12.15 / 10.0, 4.6 / 10.0, (zt - 74.0) / 10.0)
                X.uni(b, many([X.tbm.createBox(ob), X.wbox(-88.0, -50.8, -23.2, -10.8, 74.0, zt), X.wbox(-56.1, -50.8, -51.2, -22.0, 74.0, zt),
                               X.wbox(-52.0, -46.8, -51.2, -40.8, 74.0, zt)]))
                log['roof'] = round(X.vol(b) - v1, 1)
            v1 = X.vol(b)
            X.dif(b, X.cyly(xi, ZU, 4.3, -49.8, -6.5)); log['tube'] = round(X.vol(b) - v1, 1); v1 = X.vol(b)
            X.uni(b, many([X.cyly(xi, ZU, 3.5, -51.8, -49.5), X.cyly(xi, ZU, 3.5, -11.5, -3.35), X.cyly(xi, ZL, 3.5, -19.0, -3.35),
                           X.cyly(xo, ZL, 3.75, -11.5, -5.0), X.cyly(xo, ZU, 3.75, -11.5, -5.0)]))
            log['plugs_bosses'] = round(X.vol(b) - v1, 1); v1 = X.vol(b)
            X.uni(b, many([X.cylz(x, y, 4.0, 4.2, zt_) for (x, y, zt_) in BOXSCR[side]]))
            log['floor_bosses'] = round(X.vol(b) - v1, 1); v1 = X.vol(b)
            X.uni(b, X.wbox(xt - 4.2, xt + 4.2, -6.6, -3.9, 75.2, 84.0)); log['tab'] = round(X.vol(b) - v1, 1); v1 = X.vol(b)
            cuts = [X.cyly(xo, ZL, 2.0, -3.35, 0.5), X.cyly(xo, ZU, 2.0, -3.35, 0.5), X.cyly(sg * 62.0, 30.0, 2.0, -52.5, -50.0),
                    X.cyly(xt, 79.5, 1.8, -7.1, -3.4)]
            cuts += [X.cyly(x, z, 1.25, -10.5, -3.2) for x in (xi, xo) for z in (ZL, ZU)]
            cuts += [X.cylz(x, y, 2.0, 3.2, 10.2) for (x, y, zt_) in BOXSCR[side]]
            X.dif(b, many(cuts)); log['holes'] = round(X.vol(b) - v1, 1)
            log['vol'] = [round(v0, 1), round(X.vol(b), 1)]; log['lumps'] = [l[0] for l in X.lumps(b)]
            st[side] = log; new[side] = (old, b)
        st['t_boxes'] = round(time.time() - t0, 1); status('f2c', st)
        # ---------------- plate ----------------
        p = X.cp(ref)
        X.sec(p, X.wbox(-130, 130, -110, 40, -1.0, 2.5))
        add = [X.cylz(x, y, 4.0, 1.0, 2.8) for (x, y) in DOOR]
        for (x, y) in PIP:
            add += [X.cylz(x, y, 3.8, 1.0, 7.5), X.cylz(x, y, 3.4, 7.3, 8.0), X.cylz(x, y, 4.6, 2.0, 3.2, 3.75)]
        for (x, y) in CRA:
            add += [X.cylz(x, y, 4.0, 1.0, 8.0), X.cylz(x, y, 4.8, 2.0, 3.3, 3.95)]
        add += [X.cylz(x, y, 4.0, 1.0, 3.7) for s in 'LR' for (x, y, zt_) in BOXSCR[s]]
        add += [X.cylz(x, y, 4.0, 1.0, 3.7) for (x, y) in BOXPAD]
        for (x0, x1) in TONG:
            add += [X.wbox(x0, x1, -0.9, 1.15, 2.0, 5.25), X.wbox(x0, x1, 0.8, 2.35, 4.35, 5.25)]
        add += [X.wbox(x0, x1, 1.9, 4.0, 2.4, 2.8) for (x0, x1) in REST]
        for q in add:
            X.uni(p, q)
        cut = [X.cylz(x, y, 6.5, -0.5, 0.5) for (x, y) in FEET]
        cut += [X.cylz(x, y, 1.7, -1.0, 4.0) for (x, y) in DOOR] + [X.cylz(x, y, 3.25, -1.0, 1.0) for (x, y) in DOOR]
        cut += [X.cylz(x, y, 2.0, 1.5, 9.0) for (x, y) in PIP] + [X.cylz(x, y, 2.0, 2.3, 9.0) for (x, y) in CRA]
        cut += [X.cylz(x, y, 1.7, -1.0, 5.0) for s in 'LR' for (x, y, zt_) in BOXSCR[s]]
        cut += [X.cylz(x, y, 3.25, -1.0, 1.0) for s in 'LR' for (x, y, zt_) in BOXSCR[s]]
        cen = json.load(open(os.path.join(FP, 'f2a_intake.json')))
        cut += [X.cylz(x, y, 1.0, -1.0, 3.5) for (x, y) in cen]
        X.dif(p, many(cut))
        sl = X.cp(front)
        X.sec(sl, many([X.wbox(sx * 74.0, sx * 92.0, -52.5, -47.5, 2.8, 3.2) for sx in (1.0, -1.0)]))
        pads = None
        for sx in (1.0, -1.0):
            a = X.cp(sl); X.sec(a, X.wbox(0.0, sx * 120.0, -60, -40, 2.0, 4.0))
            c = X.cp(a); X.move(c, dx=-sx * 0.6); X.sec(a, c)
            pads = a if pads is None else X.uni(pads, a)
        X.move(pads, dz=-0.4); X.uni(p, pads)
        st['plate'] = [round(X.vol(p), 1), [l[0] for l in X.lumps(p)]]
        st['t_plate'] = round(time.time() - t0, 1); status('f2c', st)
        # ---------------- checks ----------------
        cl = {'plate~L': round(X.clash(p, new['L'][1]), 2), 'plate~R': round(X.clash(p, new['R'][1]), 2)}
        for n in CHK:
            q = X.body(n)
            if q is None:
                cl[n] = 'missing'; continue
            v = [round(X.clash(t, q), 2) for t in (p, new['L'][1], new['R'][1])]
            if any(v):
                cl[n] = v
                for i, s in ((1, 'L'), (2, 'R')):
                    if v[i]:
                        t = X.cp(new[s][1]); X.sec(t, X.cp(q))
                        cl[n + '~' + s] = {'v42': round(X.clash(new[s][0], q), 2), 'where': [l for l in X.lumps(t)[:4]]}
        st['clash[plate,L,R]'] = cl
        st['t_checks'] = round(time.time() - t0, 1)
        if APPLY:
            X.body('FLOOR_PLATE').deleteMe()
            pb = X.add(p, 'FLOOR_PLATE', like=front)
            out = {'FLOOR_PLATE': round(pb.volume * 1000, 1)}
            for side in 'LR':
                old, b = new[side]
                X.retire(old)
                nb = X.add(b, 'SPKBOX_' + side, like=old)
                out['SPKBOX_' + side] = [round(nb.volume * 1000, 1), nb.lumps.count]
            out['dups'] = X.dups(); out['bodies'] = X.root.bRepBodies.count
            st['added'] = out
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status('f2c', st)


run(None)
