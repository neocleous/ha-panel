# rev F f2b1 (2026-11-10): read-only probe - why the cove cut of f2b fails (ASM_INCONS_FACE) and which tool variant works.
# All on TemporaryBRep copies; nothing in the model changes. Result: fp/f2b1_status.json
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
PIP = [(18.35, -5.5), (-39.65, -5.5), (18.35, -54.5), (-39.65, -54.5)]
CRA = [(6.5, -72.5), (-1.5, -72.5)]
LIPX = [(23.5, 36.5), (-36.5, -23.5)]


def run(_context):
    st = {'t0': time.strftime('%Y-%m-%d %H:%M:%S')}
    t0 = time.time()

    def mark(k, v=None):
        st[k] = v if v is not None else round(time.time() - t0, 1)
        status('f2b1', st)
    try:
        X = K()
        front = X.body('HOUSING_F_front')
        s = X.cp(front); v0 = X.vol(s); mark('t_copy')
        X.dif(s, X.wbox(-130, 130, -110, 40, -2.0, 2.8)); v1 = X.vol(s); mark('t_floor')
        st['lumps_after_floor'] = X.lumps(s)[:14]; mark('t_lumps')
        for (x, y) in PIP:
            X.dif(s, X.cylz(x, y, 5.0, 2.0, 8.6))
        for (x, y) in CRA:
            X.dif(s, X.cylz(x, y, 5.4, 2.0, 8.6))
        v2 = X.vol(s); mark('t_posts')
        st['lumps_after_posts'] = X.lumps(s)[:14]
        st['vol'] = {'v42': round(v0, 1), 'floor': round(v1 - v0, 1), 'posts': round(v2 - v1, 1)}
        inner = X.body('INNER_E'); skin = X.body('TOOL_inner_skin_0p7')
        full = X.cp(inner); mark('t_cp_inner')
        X.sec(full, X.wbox(46.2, 110.0, -75.0, 0.5, 2.3, 9.0)); mark('t_sec_inner')
        X.dif(full, X.cp(skin)); mark('t_dif_skin')
        st['full_mm3'] = round(X.vol(full), 1); st['full_lumps'] = X.lumps(full)[:4]
        # what the shell has inside that region, by height band
        bands = {}
        for (a, b) in ((2.3, 4.0), (4.0, 5.0), (5.0, 5.6), (5.6, 5.95), (5.95, 6.2), (6.2, 7.0), (7.0, 9.0)):
            t = X.cp(full); X.sec(t, X.wbox(40, 115, -80, 5, a, b))
            u = X.cp(s)
            try:
                X.sec(u, t); bands['%.2f-%.2f' % (a, b)] = [round(X.vol(u), 3), X.lumps(u)[:5]]
            except Exception as e:
                bands['%.2f-%.2f' % (a, b)] = 'FAIL ' + str(e)[:60]
        st['shell_in_core_bands'] = bands; mark('t_bands')
        # variants of the cut on copies of the shell
        var = {}

        def attempt(name, tool):
            ta = time.time()
            c = X.cp(s)
            try:
                X.dif(c, tool)
                var[name] = ['ok', round(X.vol(c) - v2, 2), len(X.lumps(c)), round(time.time() - ta, 1)]
            except Exception as e:
                var[name] = ['FAIL', str(e)[:50], round(time.time() - ta, 1)]
            st['variants'] = var; status('f2b1', st)
        for top in (5.95, 5.6, 5.2, 7.0, 8.5):
            t = X.cp(full); X.sec(t, X.wbox(40, 115, -80, 5, 2.0, top)); attempt('top%.2f' % top, t)
        for (dx, top) in ((0.05, 6.5), (0.1, 6.5), (-0.1, 5.95), (-0.2, 5.95)):
            t = X.cp(full); X.sec(t, X.wbox(40, 115, -80, 5, 2.0, top)); X.move(t, dx=dx); attempt('dx%+.2f_top%.2f' % (dx, top), t)
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status('f2b1', st)


run(None)
