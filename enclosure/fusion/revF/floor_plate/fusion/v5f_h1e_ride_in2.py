# rev F h1e (2026-11-11): step 3, block 1 - read-only: the ride-in of h1d with the board's real height classes instead of one prism.
#   h1d: the full-outline prism 28.5 tall meets only the shell, and only above v 16 at w 21.6..28.5 (the rim above the door opening);
#   every other fixed body 0. Here, against the shell cropped to the site (cached):
#   A  outline u +/-43.5, v +/-28.95, everything except the supply module: 16.0 tall (C5, C6) - and taller, to find the limit
#   B  the supply module's box u -37.11..13.79, v -4.35..7.75 at 28.5 tall - and grown in u and v, to find its margin
#   C  the real bodies (pcb, PS1 + its top tolerance, conn, tall, low) moved out 0.5 .. 60 mm in STEPS
#   each swept from its place to 60 mm out along the slab normal.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_h_lib.py'), encoding='utf-8').read())
MODE = globals().get('MODE', 'AB')
STEPS = (0.5, 1, 2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 35, 40, 50, 60)


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        c = cache()
        if 'crop_front_site' not in c:
            t = X.cp(tcopy(X, 'HOUSING_F_front')); X.sec(t, X.dbox(U0 - 62, U0 + 62, -30, 75, V0 - 47, V0 + 47))
            c['crop_front_site'] = t
        sh = c['crop_front_site']
        st['crop'] = [round(X.vol(sh), 1), round(time.time() - t0, 1)]

        def hit(pr):
            t = X.cp(pr)
            X.tbm.booleanOperation(t, sh, BT.IntersectionBooleanType)
            v = X.vol(t)
            return [round(v, 2)] + (bbb(t, 1) if v > 0.001 else [])
        if 'A' in MODE:
            st['A'] = {'w %.1f' % w: hit(X.dbox(U0 - 43.5, U0 + 43.5, -28.9, D0 + w, V0 - 28.95, V0 + 28.95)) for w in (16.0, 18.0, 20.0, 21.0, 22.0)}
            status3('h1e', st)
        if 'B' in MODE:
            st['B'] = {'g %.1f' % g: hit(X.dbox(U0 - 37.11 - g, U0 + 13.79 + g, -28.9, D0 + 28.5, V0 - 4.35 - g, V0 + 7.75 + g)) for g in (0.0, 1.0, 2.0, 3.0, 5.0, 8.0)}
            status3('h1e', st)
        if 'C' in MODE:
            res = c.setdefault('h1e_C', {})
            for n in ('MAIN_pcb', 'MAIN_PS1', 'MAIN_PS1_tol', 'MAIN_conn', 'MAIN_tall', 'MAIN_low'):
                src = tcopy(X, n)
                for s in STEPS:
                    k = '%s %g' % (n[5:], s)
                    if k in res:
                        continue
                    if time.time() - t0 > 35.0:
                        st['partial'] = True; break
                    t = move_n(X, X.cp(src), s)
                    X.tbm.booleanOperation(t, sh, BT.IntersectionBooleanType)
                    res[k] = round(X.vol(t), 3)
            st['C_done'] = len(res)
            st['C_hits'] = {k: v for k, v in res.items() if v > 0.0005}
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('h1e', st)


run(None)
