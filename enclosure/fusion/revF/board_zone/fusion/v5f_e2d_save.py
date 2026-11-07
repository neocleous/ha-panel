# rev F e2d (2026-11-08): save the main board rev 2 bodies (e2b) as a new version, export the f3d, re-activate the document
#   that was active before e2a. Guard: the three new bodies' volumes and the hidden *_e2 copies.
import os, traceback
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
OUT = os.path.expanduser('~/Documents/HA_panel_renders/board_zone/e2d_status.json')
EXPECT = {'MAIN_pcb': 7.9192, 'MAIN_front_env': 146.9829, 'MAIN_back_env': 14.2437, 'MAIN_pcb_e2': 7.2,
          'MAIN_front_env_e2': 130.14, 'MAIN_back_env_e2': 15.75, 'HOUSING_F_front': 235.9107, 'HOUSING_F_door': 47.2633,
          'MAIN_BRACKET': 6.5563}
VERSION = ('rev F WIP 2026-11-08 e2: main board rev 2 (MAIN_env rev 2, docs 733cb5a) - MAIN_pcb 90 x 55, z 34-89, -x top '
           'corner cut; MAIN_front_env 30 (24.2 below z 35.8) without the K5 corner; MAIN_back_env 2.9 + J2 3.5 without the '
           'bare top corners; previous bodies hidden as *_e2 (Claude)')
F3D = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-e2.f3d')


def run(_context):
    st = {'t0': time.strftime('%H:%M:%S')}
    t0 = time.time()
    try:
        X = Ctx()
        bad = [k for k, v in EXPECT.items() if X.body(k) is None or abs(X.body(k).volume - v) > 0.0005]
        st['guard_bad'] = bad
        if bad:
            raise RuntimeError('GUARD %s' % bad)
        st['visible_main'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('MAIN_') and b.isLightBulbOn]
        ok = X.doc.save(VERSION)
        st['saved'] = ok
        st['version'] = [X.doc.dataFile.versionNumber, X.doc.dataFile.latestVersionNumber]
        st['t_save'] = round(time.time() - t0, 1)
        em = X.des.exportManager
        em.execute(em.createFusionArchiveExportOptions(F3D))
        st['f3d_mb'] = round(os.path.getsize(F3D) / 1e6, 1)
        st['t_export'] = round(time.time() - t0, 1)
        log('v5f_e2d_save', 'done', st)
        prev = [d for d in X.app.documents if d.name == 'HA Panel v5 - exploded prints (d19)']
        if prev:
            prev[0].activate()
        st['active_after'] = X.app.activeDocument.name
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    json.dump(st, open(OUT, 'w'), indent=1)
    print(json.dumps(st))


run(None)
