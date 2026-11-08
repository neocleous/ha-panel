# rev F e3c (2026-11-08): save the main board rev 2.1 C7 bodies (e3a) as a new version, export the f3d, re-activate the
#   exploded-prints copy. Guard: the new and the existing main-board bodies' volumes.
import os, traceback
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
OUT = os.path.expanduser('~/Documents/HA_panel_renders/board_zone/e3c_status.json')
EXPECT = {'MAIN_C7_env': 0.29698, 'KO_C7_vent': 0.07127, 'MAIN_pcb': 7.9192, 'MAIN_front_env': 146.9829,
          'MAIN_back_env': 14.2437, 'HOUSING_F_front': 235.9107, 'HOUSING_F_door': 47.2633, 'MAIN_BRACKET': 6.5563}
VERSION = ('rev F WIP 2026-11-08 e3: main board rev 2.1 (MAIN_env rev 2.1, docs 236be84) - MAIN_C7_env (C7 D5.5 x 12.5 at '
           'x_rel -5.67, z 86.05, top strip above the NID) and KO_C7_vent (3 mm above its vent), both hidden (Claude)')
F3D = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-e3.f3d')


def run(_context):
    st = {'t0': time.strftime('%H:%M:%S')}
    t0 = time.time()
    try:
        X = Ctx()
        bad = [k for k, v in EXPECT.items() if X.body(k) is None or abs(X.body(k).volume - v) > 0.0005]
        st['guard_bad'] = bad
        if bad:
            raise RuntimeError('GUARD %s' % bad)
        st['saved'] = X.doc.save(VERSION)
        st['t_save'] = round(time.time() - t0, 1)
        em = X.des.exportManager
        em.execute(em.createFusionArchiveExportOptions(F3D))
        st['f3d_mb'] = round(os.path.getsize(F3D) / 1e6, 1)
        st['t_export'] = round(time.time() - t0, 1)
        log('v5f_e3c_save', 'done', st)
        prev = [d for d in X.app.documents if d.name == 'HA Panel v5 - exploded prints (d19)']
        if prev:
            prev[0].activate()
        st['active_after'] = X.app.activeDocument.name
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    json.dump(st, open(OUT, 'w'), indent=1)
    print(json.dumps(st))


run(None)
