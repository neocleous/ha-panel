# rev F audit-response d4g (2026-11-06): the old Ø2.1 pin holes carried a Ø2.2 × ≈ 0.03 recess at the door's inner face (from an
#   earlier fill / re-cut; present in the d4b-1 probe already). d4c's fill follows the wall profile (REF_F_outer − 0.7 recess −
#   (INNER_E − 0.7 layer)), whose inner face lies ≈ 0.03 outside the door's, so the two recesses stayed as orphan Ø2.2 rings
#   beside the new Ø1.7 holes. Removed with Fusion's Delete (heals by extending the inner face), tried on a copy first:
#   copy -> DeleteFaceFeatures on the Ø2.2 faces (+ their recess floors if needed) -> checks -> the copy becomes
#   HOUSING_F_door, the d4e state is kept hidden as HOUSING_F_door_d4e. On any failed check the door is left as it is.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
EXPECT = {'HOUSING_F_door': 51.1616}


def dimple_faces(b):
    res = []
    for f in b.faces:
        g = f.geometry
        if g.objectType != adsk.core.Cylinder.classType() or abs(g.radius * 10 - 1.1) > 0.01:
            continue
        o = g.origin; ax = g.axis; ax.normalize()
        aw = nw_of(ax)
        if abs(abs(aw[1]) - 1.0) > 1e-3:
            continue
        p = f.pointOnFace; c = (p.x * 10 - XC, wy(p), wz(p))
        if abs(abs(c[0]) - 13.6) < 1.3 and abs(c[2] - 20.6) < 1.3 and -82.0 < c[1] < -80.5:
            res.append(f)
    return res


def small_cyls(b):
    rows = []
    for f in b.faces:
        g = f.geometry
        if g.objectType != adsk.core.Cylinder.classType() or g.radius * 10 > 1.3:
            continue
        p = f.pointOnFace; c = (p.x * 10 - XC, wy(p), wz(p))
        if abs(c[0]) < 16 and -86 < c[1] < -78 and 18 < c[2] < 23.5:
            rows.append([round(2 * g.radius * 10, 3), [round(v, 2) for v in c], round(f.area * 100, 3)])
    return rows


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        for k, v in EXPECT.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard: %s %s (expected %s)' % (k, None if b is None else round(b.volume, 4), v))
        if X.body('HOUSING_F_door_d4e') is not None:
            raise RuntimeError('HOUSING_F_door_d4e exists already')
        db = X.body('HOUSING_F_door')
        t = X.add(X.tbm.copy(db), 'D4G_door_try_tmp'); t.isLightBulbOn = False
        try:
            t.appearance = db.appearance; t.material = db.material
        except Exception:
            pass
        A = dimple_faces(t)
        out['dimple_faces'] = len(A)
        floors = []
        for f in A:
            for e in f.edges:
                for ff in e.faces:
                    if ff != f and ff.area * 100 < 6.0 and ff.geometry.objectType != adsk.core.Cylinder.classType() and ff not in floors:
                        floors.append(ff)
        out['floor_faces'] = [round(ff.area * 100, 3) for ff in floors]
        ok = False; tried = []
        for label, faces in (('cyl_only', A), ('cyl_floor', A + floors)):
            if ok or not faces:
                continue
            coll = adsk.core.ObjectCollection.create()
            for f in faces:
                coll.add(f)
            try:
                X.feats.deleteFaceFeatures.add(coll); ok = True; tried.append([label, 'ok'])
            except Exception as e:
                tried.append([label, str(e)[:120]])
                A = dimple_faces(t)                    # face objects may be stale after a failed attempt
                floors = [ff for f in A for e in f.edges for ff in e.faces if ff != f and ff.area * 100 < 6.0
                          and ff.geometry.objectType != adsk.core.Cylinder.classType()]
        out['tried'] = tried
        t = X.body('D4G_door_try_tmp')
        dv = (t.volume - db.volume) * 1000
        out['dv_mm3'] = round(dv, 4); out['try_lumps'] = t.lumps.count; out['try_small_cyls'] = small_cyls(t)
        left = dimple_faces(t)
        good = ok and t.lumps.count == 1 and not left and -0.01 < dv < 0.5 and \
            len([r for r in out['try_small_cyls'] if abs(r[0] - 1.7) < 0.01]) >= 2
        out['accepted'] = good
        if good:
            db.name = 'HOUSING_F_door_d4e'; db.isLightBulbOn = False
            t.name = 'HOUSING_F_door'; t.isLightBulbOn = True
            out['door_cm3'] = [EXPECT['HOUSING_F_door'], round(t.volume, 4)]
        else:
            t.deleteMe()
        out['names'] = [b.name for b in X.comp.bRepBodies if b.name.startswith(('HOUSING_F_door', 'D4G_'))]
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d4g_pin_dimple', 'run', out)
    print(json.dumps(out, separators=(',', ':')))
