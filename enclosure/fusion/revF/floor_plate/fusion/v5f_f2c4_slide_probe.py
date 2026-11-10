# rev F f2c4 (2026-11-10): read-only - what a speaker box meets when it sits 1.0 / 2.2 mm behind its place at full height
# (the plate and everything on it slide forward 2.0 as one unit). Shell piece only (rear outboard corner region and the sides).
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        F = X.body('HOUSING_F_front')
        sh = X.cp(F)
        X.sec(sh, X.uni(X.wbox(40, 110, -75, -30, 2, 95), X.wbox(-110, -40, -75, -30, 2, 95)))
        st['t_piece'] = round(time.time() - t0, 1)
        for side in 'LR':
            b = X.body('SPKBOX_' + side)
            for dy in (0.0, -0.5, -1.0, -2.2):
                t = X.cp(b); X.move(t, dy=dy)
                X.sec(t, X.cp(sh))
                st['%s dy%g' % (side, dy)] = [round(X.vol(t), 2)] + X.lumps(t)[:4]
            # how far back before first contact, by height band, at dy -2.2
            t = X.cp(b); X.move(t, dy=-2.2); X.sec(t, X.cp(sh))
            bands = {}
            for (a, c) in ((3, 10), (10, 20), (20, 40), (40, 60), (60, 77)):
                u = X.cp(t)
                try:
                    X.sec(u, X.wbox(-120, 120, -90, 0, a, c)); bands['%d-%d' % (a, c)] = [round(X.vol(u), 2)] + [l[1] for l in X.lumps(u)[:2]]
                except Exception:
                    bands['%d-%d' % (a, c)] = 0
            st[side + ' bands dy-2.2'] = bands
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status('f2c4', st)


run(None)
