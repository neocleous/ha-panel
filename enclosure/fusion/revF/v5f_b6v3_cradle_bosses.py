# rev F block 6 / V11-3 (2026-11-05): B6V-2 found front ∩ door 3.36 mm³ – the cradle floor bosses at (x_rel ±3.8, y −76.0)
#   reach y −80.0, into the door's thickened floor cove (inner cove surface ≈ y −79 at the back centre, z 3–6). The plug box
#   of the V11 route only occupies x_rel −25.7…−5.7, so:
#   1. Front shell: bosses (±3.8, −76.0) removed; new floor bosses Ø8 z 2.0–8.0 at (+6.5, −72.5) and (−1.5, −72.5)
#      (back edge y −76.5 as before B6V-1; the −x one 0.2 clear of the plug box in x), Ruthex M3 Ø4.0 z 2.3–8.0.
#   2. CRADLE_5807: plate front restored for x_rel > −5.2 (from CRADLE_5807_b5 + 6.5: plate to y −60.5 and the +x front pad
#      under the board's corner come back; the cable and the plug's relief pass under it, plate bottom z 14.5 vs relief top
#      14.0); legs (±3.8, −76.0) removed and their plate holes filled; old fixing hole (+5.5, −72.5) filled; legs Ø8
#      z 8.0–14.6 at the new boss positions, Ø3.4 through, c-bore Ø6.5 × 1.5 (M3 × 12 DIN912).
#   3. Checks: front ∩ door, the cradle and front against every current part, door sweep, probes.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
DZ = 6.5
EXPECT = {'HOUSING_F_front': 237.926, 'HOUSING_F_door': 53.536, 'CRADLE_5807': 1.598, 'GROMMET_usbc_F': 0.489}
FB_V1 = ((3.8, -76.0), (-3.8, -76.0))
FB2 = ((6.5, -72.5), (-1.5, -72.5))
PLATE = (-10.5, 10.5, -82.1, -60.5, 8.0 + DZ, 11.0 + DZ)          # x_rel0, x_rel1, y0, y1, z0, z1
SKIP_PREFIX = ('HOUSING_F', 'HOUSING_E', 'REF_', 'INNER_', 'TOOL_', 'V11', 'RENDER_', 'sk_')
SKIP_SUFFIX = ('_b4n', '_b4d', '_b1', '_b2', '_b5', '_revE', '_revD', '_tmp', '_wip', '_r2')
STALE = ('HOUSING_shell', 'DOOR_tray', 'REF_outer_hidden', 'DOOR_plate', 'DOOR_F', 'GROMMET_usbc', 'TOUCH_pcb', 'LD2410C_env',
         'SENSOR_strip_L', 'SENSOR_strip_R', 'SPK_driver_D40', 'PD_trigger_env_20V')


def current_parts(X):
    parts = []
    for b in X.comp.bRepBodies:
        n = b.name
        if n.startswith(SKIP_PREFIX) or n.endswith(SKIP_SUFFIX) or n in STALE or n.startswith(('VOICEPE_', 'BUCK_', 'AMP_', 'SPK_driver', 'SENSOR_strip')) \
                or (n.startswith('PI5_') and n not in ('PI5_F', 'PI5_F_cooler')) or (n.startswith('TOUCH_') and n != 'TOUCH_PCB'):
            continue
        parts.append(b)
    return parts + [X.body(n) for n in ('HOUSING_F_front', 'HOUSING_F_door')]


def hits_vs(X, m, parts):
    mb = m.boundingBox; hits = {}
    for o in parts:
        if o.name == m.name:
            continue
        ob = o.boundingBox
        lo = [max(mb.minPoint.x, ob.minPoint.x), max(mb.minPoint.y, ob.minPoint.y), max(mb.minPoint.z, ob.minPoint.z)]
        hi = [min(mb.maxPoint.x, ob.maxPoint.x), min(mb.maxPoint.y, ob.maxPoint.y), min(mb.maxPoint.z, ob.maxPoint.z)]
        if any(hi[k] < lo[k] for k in range(3)):
            continue
        box = X.tbm.createBox(adsk.core.OrientedBoundingBox3D.create(P3((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2),
                              V3(1, 0, 0), V3(0, 1, 0), hi[0] - lo[0] + 0.02, hi[1] - lo[1] + 0.02, hi[2] - lo[2] + 0.02))
        qa = X.tbm.copy(m); inter(X, qa, box)
        if qa.volume <= 0:
            continue
        qb = X.tbm.copy(o); inter(X, qb, X.tbm.copy(box)); inter(X, qa, qb)
        if qa.volume * 1000 > 0.005:
            hits[o.name] = [round(qa.volume * 1000, 2), [round(c, 1) for c in wbb(X, qa)]]
    return hits or 'all 0'


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        for k, v in EXPECT.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.002:
                raise RuntimeError('guard: %s volume %s, expected %s' % (k, None if b is None else round(b.volume, 3), v))
        fb = X.body('HOUSING_F_front'); cb = X.body('CRADLE_5807')
        v0 = {'front': round(fb.volume, 3), 'cradle': round(cb.volume, 3)}
        out['front_x_door_before'] = vol_x(X, fb, X.body('HOUSING_F_door'))
        # 1. front shell bosses
        rem = None
        for (xr, y) in FB_V1:
            t = X.wcyl_z(XC + xr, y, 4.1, 2.5, 8.1); rem = t if rem is None else X.union(rem, t)
        X.combine(fb, [X.add(rem, 'B6V3_rem_tmp')], op=CUT); fb = X.body('HOUSING_F_front')
        add = None
        for (xr, y) in FB_V1:
            t = X.wcyl_z(XC + xr, y, 2.05, 2.2, 2.5); add = t if add is None else X.union(add, t)
        for (xr, y) in FB2:
            X.union(add, X.wcyl_z(XC + xr, y, 4.0, 2.0, 8.0))
        X.combine(fb, [X.add(add, 'B6V3_add_tmp')]); fb = X.body('HOUSING_F_front')
        cut = None
        for (xr, y) in FB2:
            t = X.wcyl_z(XC + xr, y, 2.0, 2.3, 8.1); cut = t if cut is None else X.union(cut, t)
        X.combine(fb, [X.add(cut, 'B6V3_cut_tmp')], op=CUT); fb = X.body('HOUSING_F_front')
        out['front_cm3'] = [v0['front'], round(fb.volume, 3)]; out['front_lumps'] = fb.lumps.count
        # 2. cradle (new body replaces B6V-1's; B6V-1's kept hidden as CRADLE_5807_b6v1)
        cb.name = 'CRADLE_5807_b6v1'; cb.isLightBulbOn = False
        cr = X.tbm.copy(cb)
        old = X.tbm.copy(X.body('CRADLE_5807_b5')); mvw(X, old, 0.0, 0.0, DZ)
        inter(X, old, X.wbox(XC - 5.2, XC + 12.0, -72.05, -50.0, 0.0, 40.0))
        X.union(cr, old)
        for (xr, y) in FB_V1:
            X.diff(cr, X.wcyl_z(XC + xr, y, 4.1, 7.9, PLATE[4]))
        pl = X.wbox(XC + PLATE[0], XC + PLATE[1], PLATE[2], PLATE[3], PLATE[4], PLATE[5])
        fill = None
        for (xr, y) in FB_V1 + ((5.5, -72.5),):
            t = X.wcyl_z(XC + xr, y, 3.3, PLATE[4], PLATE[5]); inter(X, t, X.tbm.copy(pl))
            fill = t if fill is None else X.union(fill, t)
        X.union(cr, fill)
        for (xr, y) in FB2:
            X.union(cr, X.wcyl_z(XC + xr, y, 4.0, 8.0, PLATE[4] + 0.1))
        for (xr, y) in FB2:
            X.diff(cr, X.wcyl_z(XC + xr, y, 1.7, 7.9, PLATE[5] + 0.1))
            X.diff(cr, X.wcyl_z(XC + xr, y, 3.25, PLATE[5] - 1.5, PLATE[5] + 0.1))
        nb = X.add(cr, 'CRADLE_5807')
        out['cradle_cm3'] = [v0['cradle'], round(nb.volume, 3)]; out['cradle_lumps'] = nb.lumps.count
        # 3. checks
        db = X.body('HOUSING_F_door')
        out['front_x_door_after'] = vol_x(X, fb, db)
        parts = current_parts(X)
        out['interference_mm3'] = {'CRADLE_5807': hits_vs(X, nb, parts), 'HOUSING_F_front': hits_vs(X, fb, parts)}
        g = X.body('GROMMET_usbc_F'); sweep = {}
        for dy in (1.0, 3.0, 10.0, 30.0, 80.0):
            q = X.tbm.copy(db); X.union(q, X.tbm.copy(g)); mvw(X, q, 0.0, -dy, 0.0)
            sweep[str(dy)] = {n: vol_x(X, q, X.body(n)) for n in ('HOUSING_F_front', 'CRADLE_5807', 'PD_5807_env')}
        out['door_sweep_mm3'] = sweep
        P = lambda b, x, y, z: X.inside(b, XC + x, y, z)
        out['probes'] = {
            'v1_bosses_gone': not P(fb, 3.8 + 3.0, -77.5, 5.0) and not P(fb, -3.8 - 3.0, -77.5, 5.0),
            'floor_solid_at_v1_holes': P(fb, 3.8, -76.0, 2.4) and P(fb, -3.8, -76.0, 2.4),
            'new_bosses_solid': P(fb, 6.5 + 3.0, -72.5, 5.0) and P(fb, -1.5 - 3.0, -72.5, 5.0),
            'new_boss_holes_open': not P(fb, 6.5, -72.5, 5.0) and not P(fb, -1.5, -72.5, 5.0),
            'plate_front_+x_back': P(nb, 5.0, -65.0, 16.0), 'plate_front_-x_open': not P(nb, -8.0, -65.0, 16.0),
            'legs_solid': P(nb, 6.5 + 3.0, -72.5, 11.0) and P(nb, -1.5 - 3.0, -72.5, 11.0),
            'leg_holes_open': not P(nb, 6.5, -72.5, 11.0) and not P(nb, -1.5, -72.5, 16.5),
            'old_legs_gone': not P(nb, -3.8 - 3.0, -77.5, 11.0),
            'v1_plate_holes_filled': P(nb, 3.8, -76.0, 16.5) and P(nb, -3.8, -76.0, 16.5),
            'b5_cbore_filled': P(nb, 3.0, -72.5, 17.0),        # in B5's c-bore at (5.5, −72.5), outside the new one at (6.5, −72.5)
        }
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b6v3_cradle_bosses', 'build', out)
    print(json.dumps(out))
