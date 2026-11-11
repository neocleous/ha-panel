# rev F h save/export (2026-11-11): step 3 - named version and f3d archive. VERSION and TAG (g3, g4, ...) come from the loader.
#   Guards: the printed parts named in GUARD keep their volumes and are one lump, the backups named in NEED exist, no AUD_* or
#   RENDER_tmp_* body, no duplicate names. No STEP or print exports in this step.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_h_lib.py'), encoding='utf-8').read())
VERSION = globals()['VERSION']
TAG = globals()['TAG']
GUARD = globals().get('GUARD', {})
NEED = globals().get('NEED', [])
F3D = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-%s.f3d' % TAG)
F3D_NEW = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-%s new.f3d' % TAG)


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        nm = X.names()
        for n, v in GUARD.items():
            b = X.body(n)
            if b is None or abs(X.vol(b) - v) > 0.3 or b.lumps.count != 1:
                raise RuntimeError('guard %s' % n)
        for n in NEED:
            if n not in nm:
                raise RuntimeError('no backup ' + n)
        bad = [n for n in nm if n.startswith(('AUD_', 'RENDER_tmp_', 'NEW_'))] + X.dups()
        if bad:
            raise RuntimeError('leftover bodies: %s' % bad)
        st['n_bodies'] = len(nm); st['n_visible'] = sum(1 for b in X.root.bRepBodies if b.isLightBulbOn)
        st['version_before'] = X.doc.dataFile.versionNumber
        st['saved'] = bool(X.doc.save(VERSION)); st['name'] = VERSION
        status3('save_' + TAG, st)
        em = X.des.exportManager
        ok = em.execute(em.createFusionArchiveExportOptions(F3D_NEW))
        if ok and os.path.exists(F3D_NEW) and os.path.getsize(F3D_NEW) > 50e6:
            os.replace(F3D_NEW, F3D)
        st['f3d'] = bool(ok); st['f3d_bytes'] = os.path.getsize(F3D) if os.path.exists(F3D) else None
        st['f3d_new_left'] = os.path.exists(F3D_NEW)
        st['modified'] = X.doc.isModified
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-6:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('save_' + TAG, st)


run(None)
