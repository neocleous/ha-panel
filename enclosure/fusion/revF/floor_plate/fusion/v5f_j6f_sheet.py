# rev F j6f (2026-11-12): close, finding 1 (Daniel 11:01: remove it) - the leftover sheet under the right speaker box's raised roof.
#   The roof step of 2026-11-10 (g6a) opened the old ceiling from z 74.4 up; where the ceiling was 2.0 thick (z 74.0..76.0, as in
#   version 46) a sheet 0.4 thick stayed (top face at z 74.4, 273.9 mm2, x -90.9..-66.0, y -23.2..-10.1).
#   The sheet is taken out by cutting its own top face 0.4 down into a copy of the box (an extrude cut of the face: a straight prism,
#   no steps at the leaning wall). Checks on the copy: what went (volume, where), nothing added, one lump, no flat face left at z 74.4
#   larger than 10 mm2, needles through the place. DRY (default): the copy is deleted again. APPLY=True: the old box -> SPKBOX_R_v54
#   (hidden), the copy becomes SPKBOX_R; the cache's copies and tables of the box are purged.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_j_lib.py'), encoding='utf-8').read())
APPLY = globals().get('APPLY', False)
ZT = 74.4; DEPTH = 0.4
PLANE = adsk.core.SurfaceTypes.PlaneSurfaceType


def top_faces(X, b):                             # flat faces looking up at z ZT: [area mm2, face]
    out = []
    for f in b.faces:
        if f.geometry.surfaceType != PLANE:
            continue
        ok, n = f.evaluator.getNormalAtPoint(f.pointOnFace)
        if n.y * S + n.z * C < 0.99:
            continue
        if abs(W(f.pointOnFace)[2] - ZT) > 0.01:
            continue
        out.append([round(f.area * 100.0, 1), f])
    return sorted(out, key=lambda r: -r[0])


def run(_context):
    st = {'apply': APPLY}
    t0 = time.time()
    nb = None
    try:
        X = K()
        if X.body('SPKBOX_R_v54') is not None or X.body('NEW_SPKBOX_R') is not None:
            raise RuntimeError('already applied or a NEW_ body exists')
        old = X.body('SPKBOX_R')
        v0 = X.vol(old)
        st['old'] = {'mm3': round(v0, 1), 'lumps': old.lumps.count, 'faces': old.faces.count, 'visible': old.isLightBulbOn,
                     'flat faces up at z 74.4 (mm2)': [r[0] for r in top_faces(X, old)]}
        nb = X.add(X.cp(old), 'NEW_SPKBOX_R', like=old, show=True)
        tf = top_faces(X, nb)
        if not tf or abs(tf[0][0] - 273.9) > 1.0:
            raise RuntimeError('sheet face not found: %s' % [r[0] for r in tf])
        ext = X.root.features.extrudeFeatures
        inp = ext.createInput(tf[0][1], adsk.fusion.FeatureOperations.CutFeatureOperation)
        inp.setDistanceExtent(False, adsk.core.ValueInput.createByReal(-DEPTH / 10.0))
        inp.participantBodies = [nb]
        ext.add(inp)
        nb = X.body('NEW_SPKBOX_R')
        v1 = X.vol(nb)
        gone = X.cp(old); X.dif(gone, X.cp(nb))
        added = X.cp(nb); X.dif(added, X.cp(old))
        st['new'] = {'mm3': round(v1, 1), 'lumps': nb.lumps.count, 'faces': nb.faces.count, 'taken out mm3': round(v0 - v1, 2),
                     'old minus new: mm3, lumps, world box': [round(X.vol(gone), 2), gone.lumps.count, wext(gone) if X.vol(gone) > 0.001 else None],
                     'new minus old mm3': round(X.vol(added), 3),
                     'flat faces up at z 74.4 (mm2)': [r[0] for r in top_faces(X, nb)]}
        nd = {}
        tn = X.cp(nb)
        for (x, y) in ((-78.5, -16.7), (-85.0, -20.0), (-70.0, -12.0), (-68.0, -22.0), (-64.0, -16.0), (-57.0, -20.0), (-70.0, -40.0)):
            nd['up at x%g y%g' % (x, y)] = ivals(X, X.wbox(x - 0.02, x + 0.02, y - 0.02, y + 0.02, 60.0, 86.0), tn, 2)
        st['needles through the new box (z of material)'] = nd
        ok = (nb.lumps.count == 1 and abs((v0 - v1) - 273.9 * DEPTH) < 2.0 and X.vol(added) < 0.01
              and not any(r[0] > 10.0 for r in top_faces(X, nb)))
        st['checks pass'] = ok
        if APPLY and ok:
            vis = old.isLightBulbOn
            X.retire(old, '_v54')
            nb.name = 'SPKBOX_R'; nb.isLightBulbOn = vis
            c = cache()
            st['purged'] = purge(prefixes=('SPKBOX_R',), tables=())
            n = 0
            for tname in ('j6a', 'j6a_d', 'j6a_t'):
                t = c.get(tname, {})
                for k in [k for k in t if 'SPKBOX_R' in k.split('|')]:
                    del t[k]; n += 1
            c.get('j6b_walls', {}).pop('SPKBOX_R', None)
            for k in [k for k in c if isinstance(k, tuple) and len(k) > 1 and k[0] == 'crop' and 'SPKBOX_R' in str(k)]:
                del c[k]
            st['matrix pairs to redo'] = n
            st['added'] = {'dups': X.dups(), 'bodies': X.root.bRepBodies.count, 'backup': X.body('SPKBOX_R_v54') is not None,
                           'backup visible': X.body('SPKBOX_R_v54').isLightBulbOn, 'visible bodies': sum(1 for q in X.root.bRepBodies if q.isLightBulbOn)}
            nb = None
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-6:]
    try:
        if nb is not None:
            q = X.body('NEW_SPKBOX_R')
            if q is not None:
                q.deleteMe()
        st['NEW_ left'] = [n for n in X.names() if n.startswith('NEW_')]
        st['bodies after'] = X.root.bRepBodies.count
    except Exception:
        st['CLEANUP_FAIL'] = traceback.format_exc().splitlines()[-4:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('j6f_apply' if APPLY else 'j6f', st)


run(None)
