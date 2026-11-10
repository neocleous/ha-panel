# rev F g1b (2026-11-10): step 1, block 1 - read-only: can a fingertip (dia 24 x 60) or a pinch (dia 40 x 60) reach a plug on the main
# board's door-side face with the display module in and the door off? Tool tip on the target, axis toward the door in six directions.
# Against the shell, cap, boxes, plate, Pi, cooler, inlet cradle and board, carrier and ReSpeaker. The main board itself is left out
# (its layout is open). Targets in the slab frame (x_rel, depth, Zd); 20 mm plugs end at depth 52.5.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
TARGETS = {'bottom centre': (2, 52.5, -50), 'bottom -x': (-30, 52.5, -50), 'bottom +x': (34, 52.5, -50), '-x edge upper': (-36, 52.5, -12),
           '-x edge mid': (-36, 52.5, -36), '+x edge upper': (40, 52.5, -12), '+x edge mid': (40, 52.5, -36), 'top centre': (2, 52.5, -6),
           'top -x': (-14, 52.5, -6), 'top +x': (14, 52.5, -6), 'mid centre': (2, 52.5, -28), 'Pi power plug below the board': (24, 34, -68),
           'face low': (2, 39, -50), 'face mid': (2, 39, -28)}
DIRS = {'straight': (0, 1, 0), 'down25': (0, 0.9063, -0.4226), 'down45': (0, 0.7071, -0.7071), 'up25': (0, 0.9063, 0.4226), 'to-x25': (-0.4226, 0.9063, 0),
        'to+x25': (0.4226, 0.9063, 0)}
FIX = ['HOUSING_F_front', 'HOUSING_F_cap', 'SPKBOX_L', 'SPKBOX_R', 'FLOOR_PLATE', 'PI5_F', 'PI5_F_cooler', 'CRADLE_5807', 'PD_5807_env', 'RESP_CARRIER',
       'RESP_pcb', 'RESP_top_env', 'RESP_usbc_plug_env', 'GPIO_plugA_env', 'GPIO_plugB_env', 'PIPWR_a_env', 'BME_HOOD', 'LD2410C_env_F']


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        fix = {}
        for n in FIX:
            b = X.body(n)
            if b is None:
                continue
            t = X.cp(b)
            if n == 'HOUSING_F_front':
                X.sec(t, X.dbox(-110, 110, 18, 140, -115, 35))
            fix[n] = t
        res = {}
        for tn, (x, d, zd) in TARGETS.items():
            row = {}
            for r, lab in ((12.0, 'finger24'), (20.0, 'pinch40')):
                free = []; blocked = {}
                for dn, (ux, ud, uz) in DIRS.items():
                    c = X.tbm.createCylinderOrCone(Dp(x, d, zd), r / 10.0, Dp(x + 60 * ux, d + 60 * ud, zd + 60 * uz), r / 10.0)
                    hit = []
                    for n, f in fix.items():
                        if not c.boundingBox.intersects(f.boundingBox):
                            continue
                        t = X.cp(c)
                        try:
                            X.tbm.booleanOperation(t, f, BT.IntersectionBooleanType); v = X.vol(t)
                        except Exception:
                            v = -1.0
                        if abs(v) > 1.0:
                            hit.append('%s %d' % (n.replace('HOUSING_F_', ''), v))
                    if hit:
                        blocked[dn] = '; '.join(hit)
                    else:
                        free.append(dn)
                row[lab] = {'free': free, 'blocked': blocked}
            res[tn] = row
            st['reach'] = res; status('g1b', st)
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status('g1b', st)


run(None)
