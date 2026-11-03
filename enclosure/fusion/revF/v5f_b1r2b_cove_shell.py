# rev F block 1r-2b (2026-11-03), FALLBACK - run only if the R3.5 fillet in v5f_b1r2 failed (ring already joined).
# Inside radius from a shelled base slice: BASE = REF_E_outer ∩ world slab z -1..6.0 (z 0..6 with the R6 floor fillet),
# shelled 2.5 inward with its z 6.0 top face removed -> a tray whose inner surface is the 2.5 offset of the outer surface
# (R3.5 round the bend, floor top z 2.5); minus TOOL_ring_opening_6p5 -> COVE_tmp -> combine JOIN into HOUSING_E.
# The tray (TOOL_cove_tray) is kept hidden. Same probes as v5f_b1r2 plus the wall step at z 5.9 / 6.1.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
SITES = {'side_y-30': (XC + 95.713, -30.0, 0.9584, -0.2855), 'chin_XC': (XC, 7.5, 0.0, 1.0), 'back_XC': (XC, -85.0, 0.0, -1.0)}


def run(_context):
    X = Ctx()
    out = {}
    try:
        hb = X.body('HOUSING_E'); ref = X.body('REF_E_outer'); opening = X.body('TOOL_ring_opening_6p5')
        out['housing_start_cm3'] = round(hb.volume, 3)
        tb = X.tbm.copy(ref)
        X.tbm.booleanOperation(tb, X.wbox(-140, 140, -130, 60, -1.0, 6.0), adsk.fusion.BooleanTypes.IntersectionBooleanType)
        base = X.add(tb, 'BASE_tmp')
        coll = adsk.core.ObjectCollection.create()
        for f in base.faces:
            if f.geometry.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType:
                if abs(adsk.core.Plane.cast(f.geometry).normal.dotProduct(UP)) > 0.9999 and abs(wz(f.centroid) - 6.0) < 0.02:
                    coll.add(f)
        out['base_top_faces'] = coll.count
        t0 = time.time()
        si = X.feats.shellFeatures.createInput(coll, False); si.insideThickness = VI(0.25)
        X.feats.shellFeatures.add(si)
        out['shell'] = 'ok %.1f s' % (time.time() - t0)
        base = X.body('BASE_tmp')
        tb2 = X.tbm.copy(base); X.diff(tb2, X.tbm.copy(opening))
        base.name = 'TOOL_cove_tray'; base.isLightBulbOn = False
        cove = X.add(tb2, 'COVE_tmp')
        out['cove_cm3'] = round(cove.volume, 3)
        X.combine(hb, [cove])
        hb = X.body('HOUSING_E')
        out['housing_end_cm3'] = round(hb.volume, 3)
        out['housing_faces'] = hb.faces.count
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name == 'COVE_tmp']

        def along(b, x, y, z, nx, ny, a, c, it=30):          # a: inside, c: outside (distance along (nx, ny))
            for _ in range(it):
                m = (a + c) / 2
                if X.inside(b, x + nx * m, y + ny * m, z): a = m
                else: c = m
            return a

        sites = {}
        for k, (gx, gy, nx, ny) in SITES.items():
            t = along(ref, gx, gy, 8.0, nx, ny, -10.0, 10.0)
            px, py = gx + nx * t, gy + ny * t
            P = lambda u, z: (px - nx * u, py - ny * u, z)
            ins = lambda u, z: X.inside(hb, *P(u, z))
            r = {'P0': (round(px - XC, 3), round(py, 3))}
            r['wall_z8'] = round(along(hb, px, py, 8.0, -nx, -ny, 1.25, 4.0), 3)
            r['wall_z5.9_z6.1'] = (round(along(hb, px, py, 5.9, -nx, -ny, 1.25, 4.0), 3), round(along(hb, px, py, 6.1, -nx, -ny, 1.25, 4.0), 3))
            h = math.sqrt(0.5)
            def bis(a, c):
                for _ in range(30):
                    m = (a + c) / 2
                    if ins(6.0 - m * h, 6.0 - m * h) == ins(6.0 - a * h, 6.0 - a * h): a = m
                    else: c = m
                return (a + c) / 2
            ri = bis(2.5, 4.75); ro = bis(4.75, 7.0)
            r['bend_r_in_out_t'] = (round(ri, 3), round(ro, 3), round(ro - ri, 3))
            r['solid'] = {'ring_u6.3_z1.25': ins(6.3, 1.25), 'top_u6.25_z2.4': ins(6.25, 2.4), 'under_u6.2_z0.1': ins(6.2, 0.1),
                          'cove_u3.0_z4.0': ins(3.0, 4.0), 'cove_u4.0_z3.0': ins(4.0, 3.0), 'old_knife_u5_z0.5': ins(5.0, 0.5)}
            r['open'] = {'gap_u6.65_z1.25': not ins(6.65, 1.25), 'top_u6.25_z2.6': not ins(6.25, 2.6),
                         'cove_u3.3_z4.0': not ins(3.3, 4.0), 'cove_u4.4_z3.0': not ins(4.4, 3.0), 'outside_u3.4_z0.5': not ins(3.4, 0.5),
                         'bisector_r3.3': not ins(6.0 - 3.3 * h, 6.0 - 3.3 * h)}
            r['opening_edge_u'] = round(along(hb, px - nx * 6.0, py - ny * 6.0, 1.25, -nx, -ny, 0.0, 1.0) + 6.0, 3)
            sites[k] = r
        out['sites'] = sites
        out['all_ok'] = all(all(s['solid'].values()) and all(s['open'].values()) for s in sites.values())
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b1r2b_cove_shell', 'cove from shelled slice', out)
    print(json.dumps(out))
