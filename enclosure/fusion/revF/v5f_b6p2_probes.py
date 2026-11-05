# rev F block 6p2 (2026-11-05): follow-up probes after B6p (same temporary PROBE_tmp_OUT, deleted at the end).
#   1. Back band above the door: B6p's x 0 / z 165 point gave 2.32 – re-probed at x ±45 (outside the exhaust-slot field)
#      and the slot field's bbox reported.
#   2. Top-front roll: rays aimed at the inner corner (slot inner face d 14.8 meets the top inner surface z 177.5, world
#      ≈ y −22.4) in three directions per x, minimum wall reported.
#   3. Slab shadow gap: design −Y rays from 0.01 behind the slab's back face (d 12) on its perimeter ring, distance to the
#      housing's slot face; minimum distance slab–front (the slab bears on the boss).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
HB = ('HOUSING_F_front', 'HOUSING_F_door')


def dmin(X, a, b):
    r = X.app.measureManager.measureMinimumDistance(a, b)
    return round(r.value * 10, 3)


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time(); tmp = []
    try:
        fb = X.body('HOUSING_F_front'); db = X.body('HOUSING_F_door')
        o = X.wbox(-250, 250, -250, 250, -20, 260); X.diff(o, tb_copy(X, 'REF_F_outer'))
        sk = tb_copy(X, 'TOOL_outer_skin_0p7'); X.diff(sk, X.tbm.copy(fb)); X.diff(sk, X.tbm.copy(db))
        X.union(o, sk)
        ob = X.add(o, 'PROBE_tmp_OUT'); ob.isLightBulbOn = False; tmp.append(ob)
        out['exhaust_slots_bbox'] = [round(v, 1) for v in wbb(X, X.body('TOOL_exhaust_slots'))]
        wall = {}
        for nm, p, d in (('back_band_x+45_z165', (45.0, -40.0, 165.0), (0, -1, 0)), ('back_band_x-45_z165', (-45.0, -40.0, 165.0), (0, -1, 0)),
                         ('back_band_x0_z165', (0.0, -40.0, 165.0), (0, -1, 0)), ('back_band_x+45_z170', (45.0, -40.0, 170.0), (0, -1, 0))):
            hs = ray_hits(X, (XC + p[0], p[1], p[2]), d, HB)
            wall[nm] = [hs[0][1][10:], [round(hs[0][2], 1), round(hs[0][3], 1), round(hs[0][4], 1)], dmin(X, hs[0][7], ob)] if hs else None
        out['wall_[body, p_in, mm]'] = wall
        roll = {}
        for xr in (-60.0, 0.0, 60.0):
            r = []
            for d in ((0, 0.712, 0.702), (0, 0.75, 0.661), (0, 0.67, 0.742), (0, 0.80, 0.60)):
                hs = ray_hits(X, (XC + xr, -30.0, 170.0), d, HB)
                if hs:
                    r.append([round(hs[0][3], 2), round(hs[0][4], 2), dmin(X, hs[0][7], ob)])
            roll[str(xr)] = r
        out['top_front_roll_[y, z, wall]'] = roll
        sl = X.body('SLAB_frame')
        out['slab_front_min_mm'] = dmin(X, sl, fb)
        sb = sl.boundingBox; yb = sb.minPoint.y - 0.001
        ring = {}
        for nm, (x, z) in (('x+100_ZS', (10.0, -2.743)), ('x-105_ZS', (-10.5, -2.743)), ('x0_Z37', (0.0, 3.7)), ('x0_Z-92', (0.0, -9.2)),
                           ('x+70_Z37', (7.0, 3.7)), ('x-70_Z-92', (-7.0, -9.2))):
            pt = P3(x, yb, z); hp = adsk.core.ObjectCollection.create()
            fs = X.comp.findBRepUsingRay(pt, V3(0, -1, 0), adsk.fusion.BRepEntityTypes.BRepFaceEntityType, -1.0, False, hp)
            best = None; own = None
            for i in range(fs.count):
                q = hp.item(i); t = math.sqrt((q.x - pt.x) ** 2 + (q.y - pt.y) ** 2 + (q.z - pt.z) ** 2) * 10 + 0.01
                if fs.item(i).body.name == 'HOUSING_F_front':
                    best = t if best is None or t < best else best
                if fs.item(i).body.name == 'SLAB_frame':
                    own = t if own is None or t < own else own
            ring[nm] = {'to_front': round(best, 3) if best is not None else None, 'slab_face_hit': round(own, 3) if own is not None else None}
        out['slab_ring_gap_mm'] = ring
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    finally:
        for t in tmp:
            try:
                t.deleteMe()
            except Exception:
                pass
    out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('PROBE_tmp')]
    log('v5f_b6p2_probes', 'probes', out)
    print(json.dumps(out, separators=(',', ':')))
