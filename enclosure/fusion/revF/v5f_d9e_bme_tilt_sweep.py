# rev F d9e (2026-11-06), read-only: the BME680 board's way into its cup. Straight down along u it meets the wall above the
#   cup (d9 sweeps), so it goes in tilted: the board's lower outer edge (seated at t 0, u -7.5, w -3.0) follows POSES
#   (u offset, w offset, tilt in degrees, top edge away from the wall), the tilt about t through that edge.
#   Logs the overlap with the front and the radar lead at every pose (> 0.005 mm³ is a hit).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
exec(open(os.path.expanduser('~/Documents/HA_panel_renders/scripts_d/v5f_d9c_bme_cup.py')).read())   # frame: P, TT, UU, NI
import traceback
POSES = globals().get('POSES') or [(18.0, 3.0, 35.0), (16.0, 2.5, 30.0), (14.0, 2.0, 25.0), (12.0, 1.5, 20.0), (10.0, 1.0, 15.0),
                                   (8.0, 0.6, 10.0), (6.0, 0.3, 6.0), (4.0, 0.1, 3.0), (2.0, 0.0, 1.0), (0.0, 0.0, 0.0)]


def pose_matrix(du, dw, deg):
    pv = P(0.0, -7.5, -3.0)
    M = adsk.core.Matrix3D.create()
    ax = wv(TT)
    M.setToRotation(math.radians(-deg), ax, Dw(XC + pv[0], pv[1], pv[2]))
    sh = tuple(du * UU[i] + dw * NI[i] for i in range(3))
    w = wv(sh); tr = M.translation; tr.add(V3(w.x / 10, w.y / 10, w.z / 10)); M.translation = tr
    return M


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        env = tb_copy(X, 'BME680_env')
        fx = [(n, tb_copy(X, n)) for n in ('HOUSING_F_front', 'LEAD_RADAR', 'SPKBOX_R')]
        reg = fbox(X, -18, 18, -14, 40, -10, 25)
        fx = [(n, inter(X, q, X.tbm.copy(reg))) for n, q in fx]
        res = []
        for (du, dw, deg) in POSES:
            if time.time() - t0 > 45:
                out['stopped'] = [du, dw, deg]; break
            q = X.tbm.copy(env); X.tbm.transform(q, pose_matrix(du, dw, deg))
            hit = {n: vol_x(X, X.tbm.copy(q), f) for n, f in fx}
            res.append([du, dw, deg, {k: v for k, v in hit.items() if v > 0.005}])
        out['poses'] = res
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d9e_bme_tilt_sweep', 'sweep', out)
    print(json.dumps(out, separators=(',', ':')))
