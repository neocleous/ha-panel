# rev F block 3b (2026-11-04): D2 – the outer reference with the top edge at R3 (was rear R10 + front R3), built as a NEW
# hidden body REF_F_outer with the rev E p17 generator (same sections, slab cut, chin cut, R12 chin corners, floor R6),
# rev E scripts untouched. Differences from p17: the slab is NOT moved (it is at its final pose; the generator inputs come
# from its current bounding box), nothing is deleted (p17's build() deletes BODY_E/INNER_E/HOUSING_E – not used here),
# sketches are named skF_*, the body is BODY_F -> REF_F_outer, top rear R3 instead of R10 (front line R3 as before).
# Then compares with REF_E_outer: added = F - E, removed = E - F (volumes, lumps, world boxes). Nothing else is changed.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
RTOP, RFRONT, RFLOOR, RCORNER = 3.0, 3.0, 6.0, 12.0
EXPECT = {'HOUSING_F_front': 238.880, 'INNER_E': 1787.7, 'REF_E_outer': 1972.9}


def run(_context):
    X = Ctx(); out = {}
    B = adsk.fusion.BooleanTypes; tbm = X.tbm; comp = X.comp; feats = X.feats
    try:
        for n, v in EXPECT.items():
            b = X.body(n)
            if b is None or abs(b.volume - v) > (0.002 if n == 'HOUSING_F_front' else 0.06):
                raise RuntimeError('guard: %s volume %s, expected %s' % (n, None if b is None else round(b.volume, 3), v))
        for n in ('BODY_F', 'REF_F_outer'):
            if X.body(n) is not None:
                raise RuntimeError('%s exists already' % n)
        fl = X.plane('FLOOR_plane')
        sb = X.body('SLAB_frame').boundingBox
        YBK = wy(P3(0, sb.minPoint.y, sb.minPoint.z)); YC = YBK - 0.5; ZBK = wz(P3(0, sb.minPoint.y, sb.minPoint.z))
        ZT = 180.0; PW = 2.2; PWW = 1.7; DTOP = 28.0; YTOP = yfront(13.0, ZT) - DTOP; HWT = 90.0
        YF = -sb.minPoint.z * 10 * S
        hwE = lambda z: 100 - (100 - HWT) * (z / ZT) ** PWW
        ybE = lambda z: -85 + (YTOP + 85) * (z / ZT) ** PW
        depE = lambda z: YF - ybE(z)
        nE = lambda z: 2.6 - 0.6 * (z / ZT)
        rcE = lambda z: min(12.0, 0.5 * depE(z) - 2.0)
        out['inputs'] = {'YBK': round(YBK, 3), 'YC': round(YC, 3), 'ZBK': round(ZBK, 3), 'YF': round(YF, 3), 'YTOP': round(YTOP, 3)}

        def level_plane(z, name):
            ex = X.plane(name)
            if ex:
                return ex
            for off in (z / 10, -z / 10):
                cpi = comp.constructionPlanes.createInput(); cpi.setByOffset(fl, VI(off)); p = comp.constructionPlanes.add(cpi)
                if abs(wz(p.geometry.origin) - z) < 0.05:
                    p.name = name; p.isLightBulbOn = False; return p
                p.deleteMe()

        def sk_on(pl, name):
            sk = comp.sketches.add(pl); sk.isLightBulbOn = False; sk.name = name; return sk
        t0 = time.time()
        li = feats.loftFeatures.createInput(NEW)
        for z in [0, 20, 40, 60, 80, 100, 120, 140, 155, 165, 172, ZT]:
            pl = fl if z == 0 else level_plane(z, 'level_%d' % int(z))
            sk = sk_on(pl, 'skF_%d' % int(z))
            yf = YF; hw = hwE(z); dep = depE(z); n = nE(z); rc = rcE(z)
            cu, mid = section_pts(hw, dep, n, rc)
            Q = lambda x, y: sk.modelToSketchSpace(Dw(x, y, z))
            L = sk.sketchCurves.sketchLines; A = sk.sketchCurves.sketchArcs; k = math.sqrt(0.5)
            ln = L.addByTwoPoints(Q(XC - cu, yf), Q(XC + cu, yf)); ln.isFixed = True
            aR = A.addByThreePoints(ln.endSketchPoint, Q(XC + cu + rc * k, yf - rc + rc * k), Q(XC + hw, yf - rc)); aR.isFixed = True
            aL = A.addByThreePoints(Q(XC - hw, yf - rc), Q(XC - cu - rc * k, yf - rc + rc * k), ln.startSketchPoint); aL.isFixed = True
            cps = [aR.endSketchPoint, Q(XC + hw, yf - rc - 2.0)] + [Q(XC + u, yf + v) for (u, v) in mid] + [Q(XC - hw, yf - rc - 2.0), aL.startSketchPoint]
            sk.sketchCurves.sketchControlPointSplines.add(cps, adsk.fusion.SplineDegrees.SplineDegreeThree)
            if sk.profiles.count < 1:
                raise RuntimeError('no profile at z %s' % z)
            pr = max((sk.profiles.item(i) for i in range(sk.profiles.count)), key=lambda p: p.areaProperties().area)
            li.loftSections.add(pr)
        li.isSolid = True
        bf = feats.loftFeatures.add(li).bodies.item(0); bf.name = 'BODY_F'
        out['loft_s'] = round(time.time() - t0, 1)
        # slab cut (p17 slabcut): rectangle around the slab's x/Z extent ± 0.3, from 60 in front of the glass to 0.3 behind the slab
        sk = sk_on(comp.xZConstructionPlane, 'skF_slot'); Q = lambda x, z: sk.modelToSketchSpace(P3(x / 10, 0, z / 10))
        sk.sketchCurves.sketchLines.addTwoPointRectangle(Q(sb.minPoint.x * 10 - 0.3, sb.minPoint.z * 10 - 0.3), Q(sb.maxPoint.x * 10 + 0.3, sb.maxPoint.z * 10 + 0.3))
        nrm = sk.xDirection.crossProduct(sk.yDirection); s = 1.0 if nrm.dotProduct(V3(0, -1, 0)) > 0 else -1.0
        coll = adsk.core.ObjectCollection.create()
        for i in range(sk.profiles.count):
            coll.add(sk.profiles.item(i))
        inp = feats.extrudeFeatures.createInput(coll, CUT)
        d0 = -60.0; d1 = -sb.minPoint.y * 10 + 0.3
        inp.startExtent = adsk.fusion.OffsetStartDefinition.create(VI(s * d0 / 10)); inp.setDistanceExtent(False, VI(s * (d1 - d0) / 10))
        inp.participantBodies = [X.body('BODY_F')]; feats.extrudeFeatures.add(inp)
        # chin cut (p17 chincut)
        sk = sk_on(fl, 'skF_chin'); Q = lambda x, y: sk.modelToSketchSpace(Dw(x, y, 0.0))
        sk.sketchCurves.sketchLines.addTwoPointRectangle(Q(-130.0, YC), Q(130.0, 60.0))
        nrm = sk.xDirection.crossProduct(sk.yDirection); s = 1.0 if nrm.dotProduct(UP) > 0 else -1.0
        coll = adsk.core.ObjectCollection.create()
        for i in range(sk.profiles.count):
            coll.add(sk.profiles.item(i))
        inp = feats.extrudeFeatures.createInput(coll, CUT)
        z0 = -5.0; z1 = ZBK + 6.0
        inp.startExtent = adsk.fusion.OffsetStartDefinition.create(VI(s * z0 / 10)); inp.setDistanceExtent(False, VI(s * (z1 - z0) / 10))
        inp.participantBodies = [X.body('BODY_F')]; feats.extrudeFeatures.add(inp)
        b = X.body('BODY_F')
        # chin vertical corners R12 (p17 corners)
        front = None
        for f in b.faces:
            if f.geometry.objectType.endswith('Plane') and abs(wy(f.centroid) - YC) < 0.5:
                front = f
        coll = adsk.core.ObjectCollection.create()
        for e in front.edges:
            if abs(wz(e.startVertex.geometry) - wz(e.endVertex.geometry)) > 30:
                coll.add(e)
        fi = feats.filletFeatures.createInput(); fi.edgeSetInputs.addConstantRadiusEdgeSet(coll, VI(RCORNER / 10), True); feats.filletFeatures.add(fi)
        out['corners'] = coll.count
        b = X.body('BODY_F')

        def planar_face_at(z):
            best = None
            for f in X.body('BODY_F').faces:
                if f.geometry.objectType.endswith('Plane') and abs(wz(f.centroid) - z) < 1.0:
                    best = f
            return best
        f = planar_face_at(0)
        coll = adsk.core.ObjectCollection.create()
        for e in f.edges:
            coll.add(e)
        fi = feats.filletFeatures.createInput(); fi.edgeSetInputs.addConstantRadiusEdgeSet(coll, VI(RFLOOR / 10), True); feats.filletFeatures.add(fi)
        out['floor_edges'] = coll.count
        f = planar_face_at(ZT)
        rest = adsk.core.ObjectCollection.create()
        for e in f.edges:
            if not e.geometry.objectType.endswith('Line3D'):
                rest.add(e)
        fi = feats.filletFeatures.createInput(); fi.edgeSetInputs.addConstantRadiusEdgeSet(rest, VI(RTOP / 10), True); feats.filletFeatures.add(fi)
        out['top_rear_edges'] = rest.count
        f = planar_face_at(ZT); fr = adsk.core.ObjectCollection.create()
        for e in f.edges:
            if e.geometry.objectType.endswith('Line3D'):
                fr.add(e)
        fi = feats.filletFeatures.createInput(); fi.edgeSetInputs.addConstantRadiusEdgeSet(fr, VI(RFRONT / 10), True); feats.filletFeatures.add(fi)
        out['top_front_edges'] = fr.count
        b = X.body('BODY_F'); b.name = 'REF_F_outer'; b.isLightBulbOn = False
        out['REF_F_outer_cm3'] = round(b.volume, 3); out['faces'] = b.faces.count; out['build_s'] = round(time.time() - t0, 1)
        log('v5f_b3b_ref_outer_r3', 'built', out)

        def bbw(bb):
            mn, mx = bb.minPoint, bb.maxPoint
            cs = [P3(x, y, z) for x in (mn.x, mx.x) for y in (mn.y, mx.y) for z in (mn.z, mx.z)]
            return [round(min(c.x * 10 - XC for c in cs), 1), round(max(c.x * 10 - XC for c in cs), 1), round(min(wy(c) for c in cs), 1),
                    round(max(wy(c) for c in cs), 1), round(min(wz(c) for c in cs), 1), round(max(wz(c) for c in cs), 1)]
        ro = X.body('REF_E_outer')
        for k, (a, c) in (('added_F_minus_E', (b, ro)), ('removed_E_minus_F', (ro, b))):
            t = tbm.copy(a); tbm.booleanOperation(t, tbm.copy(c), B.DifferenceBooleanType)
            ls = sorted([[round(t.lumps.item(i).volume * 1000, 3)] + bbw(t.lumps.item(i).boundingBox) for i in range(t.lumps.count)], key=lambda r: -r[0])
            out[k] = {'mm3': round(t.volume * 1000, 2), 'n_lumps': len(ls), 'lumps': ls[:10]}
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b3b_ref_outer_r3', 'compare', out)
    print(json.dumps(out))
