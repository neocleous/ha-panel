# rev F g4d (2026-11-10): step 1, block 4 - named version and f3d archive after g4a. Guards: the five changed bodies' volumes, no AUD_*,
# no RENDER_tmp_*, no duplicate names. No STEP exports in this step (print exports follow the new board).
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
VERSION = ('rev F WIP 2026-11-10 g1: one standard screw (M3 x 8 button head, Ruthex M3 x 5.7) - cradle posts on the plate 5 taller, '
           'cradle legs 5 shorter, driver holes dia 4.0 x 6.7 for inserts, old box-screw pilots in the shell filled (Claude)')
F3D = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-g1.f3d')
F3D_NEW = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-g1 new.f3d')
GUARD = {'FLOOR_PLATE': 33466.2, 'CRADLE_5807': 1771.0, 'SPKBOX_L': 26017.3, 'SPKBOX_R': 25622.0, 'HOUSING_F_front': 201762.1}


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
            if n + '_v45' not in nm:
                raise RuntimeError('no backup %s_v45' % n)
        bad = [n for n in nm if n.startswith(('AUD_', 'RENDER_tmp_'))] + X.dups()
        if bad:
            raise RuntimeError('leftover bodies: %s' % bad)
        st['n_bodies'] = len(nm); st['n_visible'] = sum(1 for b in X.root.bRepBodies if b.isLightBulbOn)
        try:
            st['version_before'] = X.doc.dataFile.versionNumber
        except Exception:
            st['version_before'] = None
        st['saved'] = bool(X.doc.save(VERSION)); st['name'] = VERSION
        status('g4d', st)
        em = X.des.exportManager
        ok = em.execute(em.createFusionArchiveExportOptions(F3D_NEW))
        if ok and os.path.exists(F3D_NEW) and os.path.getsize(F3D_NEW) > 50e6:
            os.replace(F3D_NEW, F3D)
        st['f3d'] = bool(ok); st['f3d_bytes'] = os.path.getsize(F3D) if os.path.exists(F3D) else None
        st['f3d_new_left'] = os.path.exists(F3D_NEW)
        try:
            st['version_after_call'] = X.doc.dataFile.versionNumber
        except Exception:
            st['version_after_call'] = None
        st['modified'] = X.doc.isModified
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-6:]
    st['t_end'] = round(time.time() - t0, 1)
    status('g4d', st)


run(None)
