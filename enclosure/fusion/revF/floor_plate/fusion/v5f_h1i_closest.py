# rev F h1i (2026-11-11): step 3, block 1 - read-only: where the tightest pairs of h1c are closest (both points in the board frame
#   u, v, w and in the world x_rel, y, z), and the document's version after the g3 save.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_h_lib.py'), encoding='utf-8').read())
PAIRS = globals().get('PAIRS', [('MAIN_plug_env', 'SPKBOX_L'), ('MAIN_plug_env', 'SPKBOX_R'), ('MAIN_plug_env', 'KO_K5_LR'), ('MAIN_plug_env', 'KO_K5_LL'),
                                 ('MAIN_conn', 'KO_K5_LR'), ('MAIN_PS1_tol', 'KO_capkey_SR'), ('MAIN_PS1', 'KO_capkey_SR'), ('MAIN_PS1_tol', 'HOUSING_F_front'),
                                 ('MAIN_PS1_tol', 'HOUSING_F_door'), ('MAIN_pcb', 'RESP_top_env'), ('MAIN_PS1', 'RESP_top_env'), ('MAIN_pcb', 'SPKBOX_L'),
                                 ('MAIN_J2_plug_env', 'PI5_F_cooler'), ('MAIN_J2_plug_env', 'PIPWR_a_env'), ('MAIN_J2_plug_env', 'SPKBOX_L'),
                                 ('MAIN_pcb', 'HOUSING_F_front'), ('MAIN_plug_env', 'HOUSING_F_front'), ('MAIN_plug_env', 'HOUSING_F_door'),
                                 ('MAIN_tall', 'HOUSING_F_front'), ('MAIN_tall', 'HOUSING_F_door'), ('MAIN_pcb', 'HOUSING_F_cap')])


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        df = X.doc.dataFile
        st['version'] = [df.versionNumber, df.latestVersionNumber, X.doc.isModified, X.root.bRepBodies.count]
        rows = {}
        for a, b in PAIRS:
            if time.time() - t0 > 35.0:
                st['partial'] = True; break
            r = X.app.measureManager.measureMinimumDistance(X.body(a), X.body(b))
            p, q = r.positionOne, r.positionTwo
            rows[a[5:] + '~' + b] = [round(r.value * 10, 2), [round(v, 1) for v in Bf(p)], [round(v, 1) for v in Bf(q)], [round(v, 1) for v in W(q)]]
        st['rows'] = rows
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('h1i', st)


run(None)
