# rev F h2c (2026-11-11): step 3, block 2 - read-only checks on the rebuilt carrier.
#   A  read back: cylinder faces (axis u, v; radius; depth range), volume, lumps
#   B  smallest distances carrier - neighbours, with both points (board frame u, v and depth)
#   C  the old carrier's overlap with the ReSpeaker's microphone-side envelope, for comparison with the new one's (bosses, by design)
#   D  M3 x 8 at each post: tip depth against the hole's floor; material left under the hole
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_h_lib.py'), encoding='utf-8').read())
NEAR = ['MAIN_pcb', 'MAIN_conn', 'MAIN_PS1', 'MAIN_tall', 'MAIN_low', 'RESP_pcb', 'RESP_top_env', 'RESP_usbc_plug_env', 'LCD_2x2_header_d15.4', 'LCD_pins_d16.0',
        'LCD_Pi_standoff_d15.2', 'LCD_pcb_76x110', 'LCD_components_env_d8.8', 'LCD_DSI_conn_d9.3', 'LCD_pogo_header_d14.1', 'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL',
        'KO_K5_UR', 'SLAB_frame', 'HOUSING_F_front', 'SPKBOX_L', 'SPKBOX_R']


def pd(p):
    q = Bf(p)
    return [round(q[0], 1), round(q[1], 1), round(D0 + q[2], 1)]


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        car = X.body('RESP_CARRIER')
        cyls = []
        for f in car.faces:
            g = f.geometry
            if g.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType:
                o = Bf(g.origin); bb = f.boundingBox
                cyls.append([round(o[0], 2), round(o[1], 2), round(g.radius * 10, 2), round(-bb.maxPoint.y * 10, 2), round(-bb.minPoint.y * 10, 2)])
        st['A'] = {'vol': round(X.vol(car), 1), 'lumps': car.lumps.count, 'faces': car.faces.count, 'cyl': sorted(cyls)}
        B = {}
        for n in NEAR:
            b = X.body(n)
            r = X.app.measureManager.measureMinimumDistance(car, b)
            B[n] = [round(r.value * 10, 2), pd(r.positionOne), pd(r.positionTwo)]
        st['B'] = B
        st['C'] = {'old': round(xvol(X, tcopy(X, 'RESP_mic_env'), tcopy(X, 'RESP_CARRIER_v48')), 1), 'new': round(xvol(X, tcopy(X, 'RESP_mic_env'), tcopy(X, 'RESP_CARRIER')), 1)}
        st['D'] = {'screw tip depth': round(31.1 - 6.4, 2), 'hole floor depth': min(c[3] for c in cyls if abs(c[2] - 2.0) < 0.01), 'plate top depth': 17.2}
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('h2c', st)


run(None)
