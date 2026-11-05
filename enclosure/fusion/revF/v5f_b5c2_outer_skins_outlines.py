# rev F block 5c-2 (2026-11-05): outer skin + floor outline tools for the fabric block (hidden, no part changed).
#   REF_F_outer copies hollowed with shellFeatures (insideThickness) -> layers inside the outer surface (lesson 26):
#   TOOL_outer_skin_0p7   the 0.7 fabric recess (D1), whole REF_F_outer
#   TOOL_outer_skin_2p7   the top groove (0.7 recess + 2.0 groove depth): REF_F_outer ∩ z ≥ 160, shelled with the z-160 cap
#                         removed (an inward offset > 3.0 of the R3 top edges would degenerate; 2.7 leaves R0.3)
#   TOOL_outer_skin_3p2   the thickened floor cove (R6 edge fillet - 3.2 = R2.8, concentric with the rev E R3.5 cove):
#                         REF_F_outer ∩ z ≤ 20, shelled with the z-20 cap removed (3.2 > R3 at the top edges)
#   Floor outlines from the rev E generator's z-0 section (outline_body, port of p18), extruded NEW:
#   TOOL_floor_off6   offset 6 (= R6 fillet tangent = cove foot), z 2.0...3.3: the flat floor the D1 layer must not cover
#   TOOL_floor_off12  offset 12 (= 6 mm strip inside the fillet tangent), z -1.0...0.75: the underside inside the strip
#   (rc = 12 - OFF; at OFF 12 the front corners are sharp, so the fillet step is skipped.)
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
SKINS = ((0.7, 'TOOL_outer_skin_0p7', None), (2.7, 'TOOL_outer_skin_2p7', (160.0, 260.0, 160.0)),
         (3.2, 'TOOL_outer_skin_3p2', (-5.0, 20.0, 20.0)))      # (t, name, (crop z0, z1, removed cap z))


def outline_body2(X, OFF, z0, z1, name):
    """outline_body() with the corner arcs / chin fillet skipped when rc = 12 - OFF < 0.3 (sharp corners)."""
    comp = X.comp; feats = X.feats
    fl = X.plane('FLOOR_plane')
    sb = X.body('SLAB_frame').boundingBox
    YBK = wy(P3(0, sb.minPoint.y, sb.minPoint.z)); YC = YBK - 0.5; YF = -sb.minPoint.z * 10 * S
    ZT = 180.0; PW = 2.2; PWW = 1.7; DTOP = 28.0; YTOP = yfront(13.0, ZT) - DTOP; HWT = 90.0
    hwE = lambda z: 100 - (100 - HWT) * (z / ZT) ** PWW
    ybE = lambda z: -85 + (YTOP + 85) * (z / ZT) ** PW
    nE = lambda z: 2.6 - 0.6 * (z / ZT)

    def sign_toward(sk, vec):
        n = sk.xDirection.crossProduct(sk.yDirection); return 1.0 if n.dotProduct(vec) > 0 else -1.0

    rc = 12.0 - OFF
    sk = comp.sketches.add(fl); sk.name = 'sk_' + name; sk.isLightBulbOn = False
    hw = hwE(0) - OFF; dep = (YF - ybE(0)) - 2 * OFF; n = nE(0); yf = YF - OFF
    rr = max(rc, 0.0)
    cu, mid = section_pts(hw, dep, n, rr)
    Q = lambda x, y: sk.modelToSketchSpace(Dw(x, y, 0.0))
    L = sk.sketchCurves.sketchLines; A = sk.sketchCurves.sketchArcs; k = math.sqrt(0.5)
    ln = L.addByTwoPoints(Q(XC - cu, yf), Q(XC + cu, yf)); ln.isFixed = True
    if rr >= 0.3:
        aR = A.addByThreePoints(ln.endSketchPoint, Q(XC + cu + rr * k, yf - rr + rr * k), Q(XC + hw, yf - rr)); aR.isFixed = True
        aL = A.addByThreePoints(Q(XC - hw, yf - rr), Q(XC - cu - rr * k, yf - rr + rr * k), ln.startSketchPoint); aL.isFixed = True
        p_start, p_end = aR.endSketchPoint, aL.startSketchPoint
    else:
        p_start, p_end = ln.endSketchPoint, ln.startSketchPoint
    cps = [p_start, Q(XC + hw, yf - rr - 2.0)] + [Q(XC + u, yf + v) for (u, v) in mid] + [Q(XC - hw, yf - rr - 2.0), p_end]
    sk.sketchCurves.sketchControlPointSplines.add(cps, adsk.fusion.SplineDegrees.SplineDegreeThree)
    pr = max((sk.profiles.item(i) for i in range(sk.profiles.count)), key=lambda p: p.areaProperties().area)
    inp = feats.extrudeFeatures.createInput(pr, NEW); s = sign_toward(sk, UP)
    inp.startExtent = adsk.fusion.OffsetStartDefinition.create(VI(s * z0 / 10)); inp.setDistanceExtent(False, VI(s * (z1 - z0) / 10))
    f = feats.extrudeFeatures.add(inp); body = f.bodies.item(0); body.name = name
    sk2 = comp.sketches.add(fl); sk2.name = 'sk_' + name + '_chin'; sk2.isLightBulbOn = False
    Q2 = lambda x, y: sk2.modelToSketchSpace(Dw(x, y, 0.0))
    sk2.sketchCurves.sketchLines.addTwoPointRectangle(Q2(-130.0, YC - OFF), Q2(130.0, 60.0))
    coll = adsk.core.ObjectCollection.create()
    for i in range(sk2.profiles.count):
        coll.add(sk2.profiles.item(i))
    ci = feats.extrudeFeatures.createInput(coll, CUT); s2 = sign_toward(sk2, UP)
    ci.startExtent = adsk.fusion.OffsetStartDefinition.create(VI(s2 * (z0 - 5.0) / 10)); ci.setDistanceExtent(False, VI(s2 * (z1 - z0 + 10.0) / 10))
    ci.participantBodies = [body]; feats.extrudeFeatures.add(ci)
    body = X.body(name)
    if rr >= 0.3:
        front = None
        for fc in body.faces:
            if fc.geometry.objectType.endswith('Plane') and abs(wy(fc.centroid) - (YC - OFF)) < 0.5:
                front = fc
        if front is None:
            raise RuntimeError('%s: chin face not found' % name)
        ec = adsk.core.ObjectCollection.create()
        for e in front.edges:
            if abs(wz(e.startVertex.geometry) - wz(e.endVertex.geometry)) > 0.5:
                ec.add(e)
        fi = feats.filletFeatures.createInput(); fi.edgeSetInputs.addConstantRadiusEdgeSet(ec, VI(rr / 10), True)
        feats.filletFeatures.add(fi)
    body = X.body(name); body.isLightBulbOn = False
    return body, YC


def run(_context):
    X = Ctx(); out = {}
    try:
        ref = X.body('REF_F_outer')
        out['REF_F_outer_cm3'] = round(ref.volume, 3)
        for t, nm, crop in SKINS:
            if X.body(nm) is not None:
                out[nm] = 'exists'; continue
            t0 = time.time()
            tb = X.tbm.copy(ref)
            if crop is not None:
                X.tbm.booleanOperation(tb, X.wbox(-250, 250, -250, 250, crop[0], crop[1]), adsk.fusion.BooleanTypes.IntersectionBooleanType)
            b = X.add(tb, nm)
            coll = adsk.core.ObjectCollection.create()
            if crop is None:
                coll.add(b)
            else:
                cap = None
                for f in b.faces:
                    if f.geometry.objectType.endswith('Plane') and abs(wz(f.pointOnFace) - crop[2]) < 0.05:
                        ok, n = f.evaluator.getNormalAtPoint(f.pointOnFace)
                        if abs(n.y * S + n.z * C) > 0.99:
                            cap = f
                if cap is None:
                    raise RuntimeError('%s: crop cap at z %s not found' % (nm, crop[2]))
                coll.add(cap)
            si = X.feats.shellFeatures.createInput(coll, False)
            si.insideThickness = VI(t / 10)
            X.feats.shellFeatures.add(si)
            b = X.body(nm); b.isLightBulbOn = False
            out[nm] = {'cm3': round(b.volume, 3), 'lumps': b.lumps.count, 's': round(time.time() - t0, 1)}
            log('v5f_b5c2_outer_skins_outlines', nm, out[nm])
        for OFF, z0, z1, nm in ((6.0, 2.0, 3.3, 'TOOL_floor_off6'), (12.0, -1.0, 0.75, 'TOOL_floor_off12')):
            if X.body(nm) is not None:
                out[nm] = 'exists'; continue
            b, yc = outline_body2(X, OFF, z0, z1, nm)
            bb = b.boundingBox
            out[nm] = {'cm3': round(b.volume, 3), 'chin_y': round(yc - OFF, 2), 'x_rel': [round(bb.minPoint.x * 10 - XC, 2), round(bb.maxPoint.x * 10 - XC, 2)]}
        # probes: 0.7 skin at the chin face (y 7.5 -> 6.8) and the side (+x, z 100); off12 at the front strip and inside
        sk = X.body('TOOL_outer_skin_0p7'); o12 = X.body('TOOL_floor_off12')
        out['probe'] = {'skin_chin_y7.15': X.inside(sk, XC, 7.15, 25.0), 'skin_chin_y6.6_out': not X.inside(sk, XC, 6.6, 25.0),
                        'off12_y-5.0_in': X.inside(o12, XC, -5.0, 0.3), 'off12_y-4.0_out': not X.inside(o12, XC, -4.0, 0.3),
                        'off12_side_x86.0_in_y-10': X.inside(o12, XC + 86.0, -10.0, 0.3), 'off12_side_x88.5_out_y-10': not X.inside(o12, XC + 88.5, -10.0, 0.3)}
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b5c2_outer_skins_outlines', 'done', out)
    print(json.dumps(out))
