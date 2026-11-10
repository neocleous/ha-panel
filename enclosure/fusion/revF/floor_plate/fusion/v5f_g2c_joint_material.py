# rev F g2c (2026-11-10): step 1, block 2 - read-only: material round the holes that would take a Ruthex M3 insert (dia 4.0) for the standard
# screw: touch-clip blocks and driver pilots on the speaker boxes. Per hole: solid fraction of the core (r 2.0), of a 1.6 and a 2.0 wall
# round it, and of 1.0 behind its end. Also: the clip blocks' and the cradle legs' extents, the feet's lowest point, cap head room.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()

        def cyl(p, u, s0, s1, r):
            a = Wp(p[0] + u[0] * s0, p[1] + u[1] * s0, p[2] + u[2] * s0); b = Wp(p[0] + u[0] * s1, p[1] + u[1] * s1, p[2] + u[2] * s1)
            return X.tbm.createCylinderOrCone(a, r / 10.0, b, r / 10.0)

        def frac(body, tool):
            full = X.vol(tool)
            t = X.cp(tool)
            try:
                X.tbm.booleanOperation(t, body, BT.IntersectionBooleanType)
                return round(X.vol(t) / full, 3)
            except Exception:
                return -1.0

        def tube(p, u, s0, s1, ri, ro):
            t = cyl(p, u, s0, s1, ro); X.dif(t, cyl(p, u, s0 - 0.1, s1 + 0.1, ri)); return t

        def hole(body, p, u, D):
            return {'core': frac(body, cyl(p, u, 0, D, 2.0)), 'w1.6': frac(body, tube(p, u, 0, D, 2.0, 3.6)), 'w2.0': frac(body, tube(p, u, 0, D, 2.0, 4.0)),
                    'behind0.5': frac(body, cyl(p, u, D, D + 0.5, 2.0)), 'behind1': frac(body, cyl(p, u, D, D + 1.0, 2.0)),
                    'behind2': frac(body, cyl(p, u, D, D + 2.0, 2.0)), 'front0.5': frac(body, cyl(p, u, -0.5, 0, 3.6))}

        L = X.cp(X.body('SPKBOX_L')); R = X.cp(X.body('SPKBOX_R'))
        res = {}
        for D in (6.2, 6.7):
            res['clip L D%.1f' % D] = hole(L, (43.5, -6.1, 38.0), (1, 0, 0), D)
            res['clip R D%.1f' % D] = hole(R, (-43.5, -6.1, 38.0), (-1, 0, 0), D)
        for sx, B, nm in ((1, L, 'L'), (-1, R, 'R')):
            for x in (52.75, 88.25):
                for z in (10.25, 45.75):
                    for y0 in (-3.0, -3.35):
                        res['drv %s x%.2f z%.2f from y%.2f D6.7' % (nm, sx * x, z, y0)] = hole(B, (sx * x, y0, z), (0, -1, 0), 6.7)
        st['holes'] = res; status('g2c', st)
        # the clip blocks and the clips
        ext = {}
        for nm, B, sx in (('L', L, 1), ('R', R, -1)):
            t = X.cp(B); X.sec(t, X.wbox(sx * 38.0, sx * 52.0, -14.0, 1.0, 28.0, 48.0))
            ext['box %s near the clip screw (x 38..52, y -14..1, z 28..48)' % nm] = X.lumps(t, 3000)
            c = X.body('TOUCH_CLIP_' + nm)
            ext['clip ' + nm] = X.lumps(X.cp(c), 3000)
        cr = X.body('CRADLE_5807')
        ext['cradle'] = X.lumps(X.cp(cr), 5000)
        t = X.cp(cr); X.sec(t, X.wbox(-7.0, 12.0, -78.0, -67.0, 7.0, 19.0)); ext['cradle legs zone'] = X.lumps(t, 3000)
        for z0, z1 in ((8.0, 10.0), (10.0, 12.0), (12.0, 14.0), (14.0, 16.0), (16.0, 17.5)):
            for x in (6.5, -1.5):
                ext['cradle ring r4..6 x%.1f z%.0f-%.1f' % (x, z0, z1)] = frac(cr, tube((x, -72.5, 0), (0, 0, 1), z0, z1, 4.0, 6.0))
                ext['cradle ring r1.7..4 x%.1f z%.0f-%.1f' % (x, z0, z1)] = frac(cr, tube((x, -72.5, 0), (0, 0, 1), z0, z1, 1.7, 4.0))
        pd = X.body('PD_5807_env')
        ext['inlet board env'] = X.lumps(X.cp(pd), 3000)
        st['ext'] = ext; status('g2c', st)
        # feet: lowest point
        feet = {}
        for fn in ('FOOT_FL', 'FOOT_RL'):
            f = X.body(fn)
            if f is None:
                continue
            low = None
            for i in range(0, 61):
                h = 6.0 - 0.1 * i
                t = X.cp(f); X.sec(t, X.wbox(-150, 150, -150, 60, -20.0, -h))
                if X.vol(t) > 1e-4:
                    low = round(-h - 0.1, 1) if i else -6.0
                    low = round(-h, 1)
                    break
            feet[fn] = low
        st['feet lowest z (0.1 steps)'] = feet
        # cap: button head room under the pads (r 2.95, z 167.85..169.5) and DIN912 head (r 2.85, z 166.5..169.5) against the front shell
        F = X.cp(X.body('HOUSING_F_front')); X.sec(F, X.wbox(-60, 60, -50, -20, 160, 176))
        cap = {}
        for nm, x, y in (('BL', 25.91, -37.80), ('BR', -25.91, -37.80), ('SL', 43.36, -32.85), ('SR', -43.36, -32.85)):
            cap[nm] = {'button r2.95': round(X.clash(X.cylz(x, y, 2.95, 167.85, 169.45), F), 3), 'button r3.35': round(X.clash(X.cylz(x, y, 3.35, 167.85, 169.45), F), 3),
                       'pad Ø3.4 hole core': frac(F, X.cylz(x, y, 1.6, 169.6, 172.5)), 'pad ring r1.8..2.85': frac(F, tube((x, y, 0), (0, 0, 1), 169.55, 170.5, 1.8, 2.85))}
        st['cap heads'] = cap
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-6:]
    st['t_end'] = round(time.time() - t0, 1)
    status('g2c', st)


run(None)
