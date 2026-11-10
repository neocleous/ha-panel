# rev F g5a (2026-11-10): read-only - where posts of dia 8 for the main board (standard M3 screw, Daniel 22:45 decision 1a) can stand
# between the carrier plate (depth 17.2) and the board's back face (depth 31.1). Board frame: u = x_rel - 2.5, v = Zd + 27.45.
# A post centre is allowed if (1) the post's foot lies on the carrier plate's rectangle (x_rel -40.0..45.4, Zd -56.9..2.2),
# (2) it is at least r + 3.0 from each of the display's four mounting points, (3) a test cylinder r + clearance touches no obstacle
# (ReSpeaker and its plug, display parts, key paths, leads behind the board, shell, slab frame, cap). The present carrier and the present
# main board are left out. Output: per v the free u intervals, for the bottom and the top band and for several clearances.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
R = 4.0
OBS = ['RESP_pcb', 'RESP_top_env', 'RESP_mic_env', 'RESP_usbc_plug_env', 'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR', 'KO_capkey_BL', 'KO_capkey_BR',
       'KO_capkey_SL', 'KO_capkey_SR', 'KO_mic_L_back', 'KO_mic_R_back', 'HOUSING_F_front', 'SLAB_frame', 'HOUSING_F_cap']
LEADS = ['LEAD_LCD_5V', 'LEAD_MIC_L', 'LEAD_MIC_R', 'LEAD_DSI', 'LEAD_USB_RESP']      # run 1 counted them as obstacles; they are re-routed in step 3
if globals().get('WITH_LEADS', False):
    OBS = OBS + LEADS
MP = [(-18.95, -24.48), (39.05, -24.48), (-18.95, 24.52), (39.05, 24.52)]
PLATE = (-42.5, 42.9, -29.45, 29.65)          # u0, u1, v0, v1


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        win = X.dbox(-52.0, 57.0, 17.25, 31.05, -62.0, 8.0)
        pieces = []
        names = OBS + [b.name for b in X.root.bRepBodies if b.name.startswith('LCD_')]
        for n in names:
            b = X.body(n)
            if b is None:
                continue
            if not win.boundingBox.intersects(b.boundingBox):
                continue
            t = X.cp(b)
            try:
                X.tbm.booleanOperation(t, win, BT.IntersectionBooleanType)
            except Exception:
                st.setdefault('skipped', []).append(n); continue
            if X.vol(t) > 0.001:
                pieces.append((n, t, t.boundingBox))
        st['obstacles in the slab'] = {n: round(X.vol(t), 1) for n, t, bb in pieces}
        st['t_pieces'] = round(time.time() - t0, 1); status('g5a', st)

        def free(u, v, rr):
            c = X.cyld(2.5 + u, -27.45 + v, rr, 17.3, 31.0)
            cb = c.boundingBox
            for n, t, bb in pieces:
                if not cb.intersects(bb):
                    continue
                q = X.cp(c)
                try:
                    X.tbm.booleanOperation(q, t, BT.IntersectionBooleanType)
                    if X.vol(q) > 0.002:
                        return n
                except Exception:
                    return n + '?'
            return None

        def scan(vs, us, rr, mp_d):
            rows = []; who = {}
            for v in vs:
                ok = []
                for u in us:
                    if u - R < PLATE[0] or u + R > PLATE[1] or v - R < PLATE[2] or v + R > PLATE[3]:
                        continue
                    if any(math.hypot(u - a, v - b) < mp_d for a, b in MP):
                        continue
                    n = free(u, v, rr)
                    if n is None:
                        ok.append(u)
                    else:
                        who[n] = who.get(n, 0) + 1
                iv = []
                for u in ok:
                    if iv and abs(u - iv[-1][1] - 0.5) < 1e-6:
                        iv[-1][1] = u
                    else:
                        iv.append([u, u])
                if iv:
                    rows.append([round(v, 2), iv])
            return rows, who

        us = [-42.0 + 0.5 * i for i in range(169)]
        res = {}
        for cl in ((0.5, 0.25, 0.1) if globals().get('WITH_LEADS', False) else (0.5,)):
            vs = [-26.0 + 0.05 * i for i in range(41)]
            rows, who = scan(vs, us, R + cl, R + 3.0)
            res['bottom band, clearance %.2f' % cl] = {'rows': rows, 'blocked by': who}
            st['res'] = res; st['t'] = round(time.time() - t0, 1); status('g5a', st)
        vs = [15.0 + 0.25 * i for i in range(45)]
        rows, who = scan(vs, us, R + 0.5, R + 3.0)
        res['top band, clearance 0.50'] = {'rows': rows, 'blocked by': who}
        st['res'] = res
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-6:]
    st['t_end'] = round(time.time() - t0, 1)
    status('g5a' if globals().get('WITH_LEADS', False) else 'g5a_noleads', st)


run(None)
