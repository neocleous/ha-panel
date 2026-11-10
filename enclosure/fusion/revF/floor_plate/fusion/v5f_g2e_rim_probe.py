# rev F g2e (2026-11-10): step 1, block 2 - read-only: what the rim renders can be built from. The old cloth bodies cut at the shell's
# bottom edge (z 2.8), and the plate's rim layer (the 0.7 skin under the body surface) as the "set back" treatment.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        P = X.body('FLOOR_PLATE'); st['plate'] = round(X.vol(P), 1)
        sk = X.body('TOOL_outer_skin_0p7')
        st['skin'] = None if sk is None else round(X.vol(sk), 1)
        a = X.cp(P); X.sec(a, X.cp(sk))
        st['plate in skin'] = round(X.vol(a), 1)
        for z0, z1 in ((0.0, 0.7), (0.7, 1.5), (1.5, 2.5), (2.5, 9.0)):
            t = X.cp(a); X.sec(t, X.wbox(-150, 150, -150, 60, z0, z1)); st['plate in skin z%.1f-%.1f' % (z0, z1)] = round(X.vol(t), 1)
        for nm in ('TOOL_floor_off6', 'TOOL_floor_off12'):
            fo = X.body(nm)
            if fo is None:
                st[nm] = 'missing'; continue
            t = X.cp(a); X.dif(t, X.cp(fo)); st['plate in skin - ' + nm] = [round(X.vol(t), 1), t.lumps.count]
            t2 = X.cp(P); X.sec(t2, X.cp(fo)); st['plate in ' + nm] = round(X.vol(t2), 1)
        status('g2e', st)
        # rim section at the front centre (x 60, chin side) and at the side (y -30): solid runs of plate, skin along horizontal lines
        sec = {}
        for nm, body in (('plate', P), ('skin', sk), ('shell', X.body('HOUSING_F_front')), ('cloth', X.body('RENDER_FABRIC_front'))):
            rows = {}
            for z in (0.3, 1.0, 1.8, 2.4, 2.65, 3.0, 4.0):
                # line along +x at y -30 from x 85 to 100: points inside
                ins = []
                for i in range(0, 151):
                    x = 85.0 + 0.1 * i
                    if body.pointContainment(Wp(x, -30.0, z)) == adsk.fusion.PointContainment.PointInsidePointContainment:
                        ins.append(x)
                rows['z%.2f' % z] = [round(min(ins), 1), round(max(ins), 1), len(ins)] if ins else None
            sec[nm] = rows
        st['side section y -30: x of material (min, max, count of 0.1 steps)'] = sec
        status('g2e', st)
        fb = X.body('RENDER_FABRIC_front'); fd = X.body('RENDER_FABRIC_door')
        st['cloth front'] = round(X.vol(fb), 1); st['cloth door'] = round(X.vol(fd), 1)
        up = X.wbox(-200, 200, -200, 100, 2.8, 260)
        f1 = X.cp(fb); X.sec(f1, X.cp(up)); st['cloth front z>=2.8'] = [round(X.vol(f1), 1), f1.lumps.count]
        d1 = X.cp(fd); X.sec(d1, X.cp(up)); st['cloth door z>=2.8'] = [round(X.vol(d1), 1), d1.lumps.count]
        status('g2e', st)
        for nm in ('HOUSING_F_cap', 'SLAB_frame', 'FLOOR_PLATE', 'HOUSING_F_door'):
            st['cloth front (cut) in ' + nm] = round(X.clash(f1, X.body(nm)), 2)
        st['cloth door (cut) in door'] = round(X.clash(d1, X.body('HOUSING_F_door')), 2)
        st['cloth door (cut) in plate'] = round(X.clash(d1, X.body('FLOOR_PLATE')), 2)
        status('g2e', st)
        F = X.cp(X.body('HOUSING_F_front')); X.sec(F, X.wbox(-200, 200, -200, 100, 2.0, 60))
        f2 = X.cp(f1); X.sec(f2, X.wbox(-200, 200, -200, 100, 2.0, 60))
        st['cloth front (cut, z<60) in shell (z<60)'] = round(X.clash(f2, F), 2)
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-6:]
    st['t_end'] = round(time.time() - t0, 1)
    status('g2e', st)


run(None)
