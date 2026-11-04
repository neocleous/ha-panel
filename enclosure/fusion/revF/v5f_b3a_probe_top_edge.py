# rev F block 3a (2026-11-04), read-only: the top-rear edge before D2 (R10 -> R3/R4).
#   rev E p17 fillets the OUTER loft's top edge (rear R10, front line R3) but INNER_E is a separate loft whose top section at
#   z 177.5 has no fillet, so the inner top edge is sharp. Measures:
#   1. INNER_E - REF_E_outer (cavity outside the outer skin = holes in the shell): volume + lumps.
#   2. Minimum distance from each INNER_E top-face edge to the outer faces with any point above z 160 (REF_E_outer).
#   3. Top-face z of REF_E_outer / HOUSING_F_front and the planar top face's extent (where the fillets start).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback


def run(_context):
    X = Ctx(); out = {}
    B = adsk.fusion.BooleanTypes; tbm = X.tbm; mm = X.app.measureManager

    def bbw(bb):
        mn, mx = bb.minPoint, bb.maxPoint
        cs = [P3(x, y, z) for x in (mn.x, mx.x) for y in (mn.y, mx.y) for z in (mn.z, mx.z)]
        xs = [c.x * 10 - XC for c in cs]; ys = [wy(c) for c in cs]; zs = [wz(c) for c in cs]
        return [round(min(xs), 1), round(max(xs), 1), round(min(ys), 1), round(max(ys), 1), round(min(zs), 1), round(max(zs), 1)]
    try:
        ie = X.body('INNER_E'); ro = X.body('REF_E_outer'); fb = X.body('HOUSING_F_front')
        t = tbm.copy(ie); tbm.booleanOperation(t, tbm.copy(ro), B.DifferenceBooleanType)
        out['inner_outside_outer_mm3'] = round(t.volume * 1000, 2)
        out['lumps'] = sorted([[round(t.lumps.item(i).volume * 1000, 2)] + bbw(t.lumps.item(i).boundingBox) for i in range(t.lumps.count)], key=lambda r: -r[0])[:8]
        log('v5f_b3a_probe_top_edge', 'perforation', out)
        top_in = None
        for f in ie.faces:
            if f.geometry.objectType.endswith('Plane') and abs(wz(f.pointOnFace) - 177.5) < 0.6:
                top_in = f
        out['inner_top_face'] = None if top_in is None else {'z': round(wz(top_in.pointOnFace), 2), 'edges': top_in.edges.count, 'bbox': bbw(top_in.boundingBox)}
        ofs = []
        for f in ro.faces:
            bb = f.boundingBox
            zmax = max(wz(P3(x, y, z)) for x in (bb.minPoint.x, bb.maxPoint.x) for y in (bb.minPoint.y, bb.maxPoint.y) for z in (bb.minPoint.z, bb.maxPoint.z))
            if zmax > 160:
                ofs.append(f)
        out['outer_faces_above_160'] = [[f.geometry.objectType.split('::')[-1], bbw(f.boundingBox)] for f in ofs]
        res = []
        if top_in is not None:
            for e in top_in.edges:
                best = None
                for f in ofs:
                    r = mm.measureMinimumDistance(e, f)
                    if best is None or r.value < best[0]:
                        p1, p2 = r.positionOne, r.positionTwo
                        best = (r.value, [round(p1.x * 10 - XC, 1), round(wy(p1), 1), round(wz(p1), 1)], [round(p2.x * 10 - XC, 1), round(wy(p2), 1), round(wz(p2), 1)], f.geometry.objectType.split('::')[-1])
                res.append({'edge': e.geometry.objectType.split('::')[-1], 'edge_bbox': bbw(e.boundingBox), 'min_wall': round(best[0] * 10, 2), 'at_inner': best[1], 'at_outer': best[2], 'outer_face': best[3]})
        out['min_wall_top_edge'] = res
        tops = []
        for b in (ro, fb):
            for f in b.faces:
                if f.geometry.objectType.endswith('Plane') and wz(f.pointOnFace) > 175:
                    tops.append([b.name, round(wz(f.pointOnFace), 2), bbw(f.boundingBox)])
        out['top_planes'] = tops
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b3a_probe_top_edge', 'probe', out)
    print(json.dumps(out))
