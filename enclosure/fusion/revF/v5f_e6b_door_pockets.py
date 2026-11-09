# rev F e6b (2026-11-09): V24 - the door's 10 magnet pockets 0.45 deeper for N52 D8 x 2 magnets (lip magnets become
#   N52 D8 x 1 in the unchanged lip pockets). Per pocket: the D8.3 cylinder (axis = outward wall normal) and its floor
#   (the planar face at the inner end); a D8.3 tool from 0.45 below the floor to 0.05 above it (inside the old pocket)
#   is cut from a TemporaryBRep copy of the door. Gates: each tool removes exactly pi x 4.15^2 x 0.45 of material (so it
#   breaks into no other void); one lump; probes on the axis (new pocket open 0.1 above the new floor, skin solid 0.1 below
#   it and 0.1 above the inner face, lap gap open, pad skin solid, lip pocket open). The old door hidden as
#   HOUSING_F_door_e6; the new body takes the name, visibility, material and appearance. Not saved here (e6d saves).
#   Load with a no-op run() after the exec (README lesson 86). Writes e6/e6b_status.json.
import os, traceback
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py'), encoding='utf-8').read())
OUT = os.path.expanduser('~/Documents/HA_panel_renders/e6/e6b_status.json')
GUARD = {'HOUSING_F_front': 235.9107, 'HOUSING_F_door': 47.2633, 'HOUSING_F_cap': 9.9441, 'GROMMET_usbc_F': 0.5062}
R_POCKET, DEEPER, OVER = 4.15, 0.45, 0.05
PI = math.pi


def wpt(p):
    return (p.x * 10 - XC, wy(p), wz(p))


def pocket_floors(door):
    """[(floor centre (design Point3D), outward axis (design Vector3D))] for the D8.3 cylinders, from each cylinder's
    adjacent planar face whose normal is parallel to the axis."""
    res = []
    for f in door.faces:
        if f.geometry.objectType != adsk.core.Cylinder.classType():
            continue
        g = adsk.core.Cylinder.cast(f.geometry)
        if abs(g.radius * 10 - R_POCKET) > 0.005:
            continue
        a = g.axis.copy(); a.normalize()
        if nw_of(a)[1] > 0:
            a.scaleBy(-1.0)
        o = g.origin; cands = []
        for e in f.edges:
            for af in e.faces:
                if af == f or af.geometry.objectType != adsk.core.Plane.classType():
                    continue
                pl = adsk.core.Plane.cast(af.geometry); nn = pl.normal.copy(); nn.normalize()
                if abs(abs(nn.dotProduct(a)) - 1.0) < 1e-6:
                    t = (pl.origin.x - o.x) * a.x + (pl.origin.y - o.y) * a.y + (pl.origin.z - o.z) * a.z
                    cands.append((t, af))
        if not cands:
            raise RuntimeError('no floor face for a pocket at %s' % (wpt(o),))
        t, floor = min(cands, key=lambda q: q[0])      # the innermost planar end is the floor
        c = P3(o.x + a.x * t, o.y + a.y * t, o.z + a.z * t)
        res.append((c, a, round(floor.area * 100, 3)))
    return res


def at(c, a, k):                     # c + k mm along a
    return P3(c.x + a.x * k / 10, c.y + a.y * k / 10, c.z + a.z * k / 10)


def run(_context):
    st = {'t0': time.strftime('%H:%M:%S')}
    t0 = time.time()
    try:
        X = Ctx(); tbm = X.tbm
        st['version'] = [X.doc.dataFile.versionNumber, X.doc.isModified]
        bad = [[k, None if X.body(k) is None else round(X.body(k).volume, 4)] for k, v in GUARD.items()
               if X.body(k) is None or abs(X.body(k).volume - v) > 0.0005]
        if X.body('HOUSING_F_door_e6') is not None:
            bad.append('HOUSING_F_door_e6 exists')
        st['guard_bad'] = bad
        if bad:
            raise RuntimeError('GUARD %s' % bad)
        door = X.body('HOUSING_F_door'); front = X.body('HOUSING_F_front')
        floors = pocket_floors(door)
        if len(floors) != 10:
            raise RuntimeError('%d pockets' % len(floors))
        tb = tbm.copy(door); v0 = tb.volume * 1000
        expect = PI * R_POCKET ** 2 * DEEPER
        rows = []
        for (c, a, farea) in sorted(floors, key=lambda r: (wpt(r[0])[0] > 0, wpt(r[0])[2])):
            tool = tbm.createCylinderOrCone(at(c, a, -DEEPER), R_POCKET / 10, at(c, a, OVER), R_POCKET / 10)
            got = vol_x(X, tool, tb)
            r = {'floor_w': [round(x, 3) for x in wpt(c)], 'n_w': [round(x, 4) for x in nw_of(a)], 'floor_area_mm2': farea,
                 'in_material_mm3': [got, round(expect, 3)]}
            if abs(got - expect) > 0.02:
                raise RuntimeError('tool gate %s' % r)
            vb = tb.volume * 1000
            tbm.booleanOperation(tb, tool, adsk.fusion.BooleanTypes.DifferenceBooleanType)
            r['removed_mm3'] = round(vb - tb.volume * 1000, 3)
            ins_d = lambda k: tb.pointContainment(at(c, a, k)) in INS
            ins_f = lambda k: front.pointContainment(at(c, a, k)) in INS
            # inner face of the door on the axis (the old skin was 0.9..0.93: search 0.3..0.6 below the new floor)
            k = -DEEPER; step = 0.01
            while ins_d(k - step) and k > -DEEPER - 1.5:
                k -= step
            r['skin_axis'] = round(-DEEPER - k, 3)
            pr = {'open_new+0.1': not ins_d(-DEEPER + 0.1), 'open_old_floor': not ins_d(0.0), 'skin-0.1': ins_d(-DEEPER - 0.1),
                  'skin_inner+0.05': ins_d(k + 0.05), 'gap_open': not ins_d(k - 0.1) and not ins_f(k - 0.1),
                  'pad_skin': ins_f(k - 0.2 - 0.25), 'lip_pocket_open': not ins_f(k - 0.2 - 0.47 - 0.5)}
            r['probes'] = pr
            if not all(pr.values()):
                raise RuntimeError('probes %s' % r)
            rows.append(r)
        st['pockets'] = rows
        if tb.lumps.count != 1:
            raise RuntimeError('lumps %d' % tb.lumps.count)
        st['removed_total_mm3'] = [round(v0 - tb.volume * 1000, 3), round(10 * expect, 3)]
        vis = door.isLightBulbOn; mat, app_ = door.material, door.appearance
        door.name = 'HOUSING_F_door_e6'; door.isLightBulbOn = False
        nb = X.add(tb, 'HOUSING_F_door'); nb.isLightBulbOn = vis
        try:
            if mat:
                nb.material = mat
            if app_:
                nb.appearance = app_
        except Exception:
            pass
        st['door'] = {'old_cm3': round(v0 / 1000, 4), 'new_cm3': round(nb.volume, 4), 'lumps': nb.lumps.count,
                      'faces_old_new': [X.body('HOUSING_F_door_e6').faces.count, nb.faces.count], 'visible': vis}
        st['modified'] = X.doc.isModified
        st['done'] = True
        log('v5f_e6b_door_pockets', 'done', {'door': st['door'], 'removed': st['removed_total_mm3']})
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    st['t_s'] = round(time.time() - t0, 1)
    json.dump(st, open(OUT, 'w'), indent=1)
    print(json.dumps({k: st.get(k) for k in ('t_s', 'done', 'guard_bad', 'door', 'removed_total_mm3', 'FAIL')}))


run(None)
