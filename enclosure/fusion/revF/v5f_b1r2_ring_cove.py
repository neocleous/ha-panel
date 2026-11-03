# rev F block 1r-2 (2026-11-03): floor ring + inside radius (Daniel 21:01: "Option 1 but add a radius on the inside to
# maintain the thickness and strength of the shell").
# u = inward distance from the outer generator surface. Outer floor fillet R6 (centre u 6, z 6).
# 1. TOOL_ring_opening_6p5 = outline_body(OFF 6.5, z -1..3.5): chin line y 1.0, front corners R5.5 (kept, hidden).
# 2. RING = REF_E_outer ∩ world slab z -1..2.5, minus the opening -> z 0..2.5 from the R6 surface to u 6.5;
#    interference vs the Pi / slab / glass bodies, then combine JOIN into HOUSING_E.
# 3. Fillet R3.5 on the concave edges between the ring top (z 2.5) and the shell's inner face: concentric with the outer R6,
#    so the wall is 2.5 thick round the bend; tangent to the inner face at z 6.0 and to the ring top at u 6.0, leaving
#    0.5 of flat ring top to the opening edge at u 6.5.
# 4. Probes at three sites (side y -30 on +x, chin at XC, back at XC): wall at z 8, bend thickness along the 45 deg
#    bisector from the fillet centre, ring / ring top / underside / cove points, opening edge.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
SITES = {'side_y-30': (XC + 95.713, -30.0, 0.9584, -0.2855), 'chin_XC': (XC, 7.5, 0.0, 1.0), 'back_XC': (XC, -85.0, 0.0, -1.0)}


def run(_context):
    X = Ctx()
    out = {}
    try:
        hb = X.body('HOUSING_E'); ref = X.body('REF_E_outer')
        out['housing_start_cm3'] = round(hb.volume, 3)
        opening, YC, rc = outline_body(X, 6.5, -1.0, 3.5, 'TOOL_ring_opening_6p5')
        opening.isLightBulbOn = False
        out['opening'] = {'cm3': round(opening.volume, 3), 'YC': round(YC, 3), 'rc': rc}
        tb = X.tbm.copy(ref)
        X.tbm.booleanOperation(tb, X.wbox(-140, 140, -130, 60, -1.0, 2.5), adsk.fusion.BooleanTypes.IntersectionBooleanType)
        X.diff(tb, X.tbm.copy(opening))
        ring = X.add(tb, 'RING_tmp')
        out['ring_cm3'] = round(ring.volume, 3)
        others = [X.body(n) for n in ('SLAB_frame', 'LCD_glass', 'PI5_F', 'PI5_F_cooler', 'GPIO_plugA_env', 'GPIO_plugB_env', 'KO_K7_fan')]
        out['ring_interf'] = X.interference(ring, others)
        if any(v > 0 for v in out['ring_interf'].values()):
            ring.isLightBulbOn = False
            raise RuntimeError('ring interference %s' % out['ring_interf'])
        v0 = hb.volume
        X.combine(hb, [ring])
        hb = X.body('HOUSING_E')
        out['housing_after_ring_cm3'] = round(hb.volume, 3)
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name == 'RING_tmp']
        # concave edges ring top / inner face
        tops = []
        for f in hb.faces:
            if f.geometry.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType:
                nrm = adsk.core.Plane.cast(f.geometry).normal
                if abs(nrm.dotProduct(UP)) > 0.9999 and abs(wz(f.centroid) - 2.5) < 0.02:
                    tops.append(f)
        ec = adsk.core.ObjectCollection.create(); kinds = {}
        for f in tops:
            for e in f.edges:
                oth = [g for g in e.faces if g.tempId != f.tempId]
                if oth and wz(oth[0].pointOnFace) > 2.51:
                    ec.add(e)
                    kn = str(oth[0].geometry.surfaceType); kinds[kn] = kinds.get(kn, 0) + 1
        out['ring_top_faces'] = len(tops); out['cove_edges'] = ec.count; out['cove_edge_neighbours'] = kinds
        t0 = time.time()
        try:
            fi = X.feats.filletFeatures.createInput()
            fi.edgeSetInputs.addConstantRadiusEdgeSet(ec, VI(0.35), True)
            X.feats.filletFeatures.add(fi)
            out['fillet'] = 'ok %.1f s' % (time.time() - t0)
        except Exception:
            out['fillet'] = 'FAILED: ' + traceback.format_exc().splitlines()[-1]
        hb = X.body('HOUSING_E')
        out['housing_end_cm3'] = round(hb.volume, 3)
        out['housing_faces'] = hb.faces.count

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
    log('v5f_b1r2_ring_cove', 'ring + cove', out)
    print(json.dumps(out))
