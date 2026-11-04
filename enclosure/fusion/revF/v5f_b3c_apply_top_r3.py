# rev F block 3c (2026-11-04): apply D2 to the front shell.
#   1. INNER_F = copy of INNER_E with its top-face edges (z 177.5: front line + side/back curve) filleted R1.0, hidden.
#      INNER_E's top edge is sharp; against the outer R3 a sharp inner corner leaves ≈ 2.3 on the bisector, the R1.0 inner
#      round keeps ≥ 2.5 (concentric would be R0.5).
#   2. Tool = (REF_F_outer − REF_E_outer) [the R3 top-edge sliver, B3b: 1355.67 mm³, z > 165] ∪ (INNER_E − INNER_F)
#      [the inner-edge sliver] ∪ (HOUSING_F_front ∩ top band x_rel ±110, y −58…−14, z 160…190) [existing material, so the
#      join overlaps instead of only touching]; combine JOIN into HOUSING_F_front (B3b found nothing to remove: E − F = 0).
#   3. Minimum distance from INNER_F's top faces (top + R1 rounds, z > 150) to REF_F_outer's faces above z 160; interference
#      with slab, LCD, door, lanes, boxes.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
EXPECT = {'HOUSING_F_front': 238.880, 'REF_F_outer': 1974.145, 'INNER_E': 1787.7, 'HOUSING_F_door': 55.484}
RIN = 1.0


def run(_context):
    X = Ctx(); out = {}
    B = adsk.fusion.BooleanTypes; tbm = X.tbm; feats = X.feats; mm = X.app.measureManager

    def bbw(bb):
        mn, mx = bb.minPoint, bb.maxPoint
        cs = [P3(x, y, z) for x in (mn.x, mx.x) for y in (mn.y, mx.y) for z in (mn.z, mx.z)]
        return [round(min(c.x * 10 - XC for c in cs), 1), round(max(c.x * 10 - XC for c in cs), 1), round(min(wy(c) for c in cs), 1),
                round(max(wy(c) for c in cs), 1), round(min(wz(c) for c in cs), 1), round(max(wz(c) for c in cs), 1)]
    try:
        for n, v in EXPECT.items():
            b = X.body(n)
            if b is None or abs(b.volume - v) > (0.06 if n == 'INNER_E' else 0.002):
                raise RuntimeError('guard: %s volume %s, expected %s' % (n, None if b is None else round(b.volume, 3), v))
        if X.body('INNER_F') is not None:
            raise RuntimeError('INNER_F exists already')
        ie = X.body('INNER_E')
        bi = X.add(tbm.copy(ie), 'INNER_F')
        top = None
        for f in bi.faces:
            if f.geometry.objectType.endswith('Plane') and abs(wz(f.pointOnFace) - 177.5) < 0.6:
                top = f
        coll = adsk.core.ObjectCollection.create()
        for e in top.edges:
            coll.add(e)
        fi = feats.filletFeatures.createInput(); fi.edgeSetInputs.addConstantRadiusEdgeSet(coll, VI(RIN / 10), True); feats.filletFeatures.add(fi)
        bi = X.body('INNER_F'); bi.isLightBulbOn = False
        out['INNER_F_cm3'] = round(bi.volume, 3); out['inner_sliver_mm3'] = round((ie.volume - bi.volume) * 1000, 2)
        add = tbm.copy(X.body('REF_F_outer')); tbm.booleanOperation(add, tbm.copy(X.body('REF_E_outer')), B.DifferenceBooleanType)
        sl = tbm.copy(ie); tbm.booleanOperation(sl, tbm.copy(bi), B.DifferenceBooleanType)
        fb = X.body('HOUSING_F_front'); v0 = fb.volume
        band = tbm.copy(fb); tbm.booleanOperation(band, X.wbox(XC - 110, XC + 110, -58, -14, 160, 190), B.IntersectionBooleanType)
        tool = X.union(X.union(add, sl), band)
        out['tool_cm3'] = round(tool.volume, 3); out['tool_lumps'] = tool.lumps.count
        X.combine(fb, [X.add(tool, 'B3C_top_tmp')])
        fb = X.body('HOUSING_F_front')
        out['front_cm3'] = [round(v0, 3), round(fb.volume, 3)]; out['front_added_mm3'] = round((fb.volume - v0) * 1000, 2)
        out['front_lumps'] = fb.lumps.count
        out['names'] = [b.name for b in X.comp.bRepBodies if b.name.startswith(('HOUSING_F', 'B3C_'))]
        log('v5f_b3c_apply_top_r3', 'applied', out)
        ro = X.body('REF_F_outer')

        def zmax(f):
            return bbw(f.boundingBox)[5]
        ofs = [f for f in ro.faces if zmax(f) > 160]
        ifs = [f for f in bi.faces if bbw(f.boundingBox)[4] > 150]          # INNER_F top face + the new R1 faces only
        out['n_faces'] = [len(ifs), len(ofs)]
        best = None
        for fi_ in ifs:
            for fo in ofs:
                r = mm.measureMinimumDistance(fi_, fo)
                if best is None or r.value < best[0]:
                    p1, p2 = r.positionOne, r.positionTwo
                    best = (r.value, [round(p1.x * 10 - XC, 1), round(wy(p1), 1), round(wz(p1), 1)], [round(p2.x * 10 - XC, 1), round(wy(p2), 1), round(wz(p2), 1)],
                            fi_.geometry.objectType.split('::')[-1], fo.geometry.objectType.split('::')[-1])
        out['min_wall_above_160'] = {'mm': round(best[0] * 10, 2), 'inner_pt': best[1], 'outer_pt': best[2], 'faces': best[3:]}
        names = [b.name for b in X.comp.bRepBodies]
        others = [X.body(n) for n in ['SLAB_frame', 'LCD_glass', 'HOUSING_F_door', 'SPKBOX_L', 'SPKBOX_R', 'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR']
                  + [n for n in names if n.startswith('LCD_') and n != 'LCD_glass']]
        r = X.interference(fb, others)
        out['interference_nonzero'] = {k: v for k, v in r.items() if v > 0} or 'all 0 (%d bodies)' % len(r)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b3c_apply_top_r3', 'checks', out)
    print(json.dumps(out))
