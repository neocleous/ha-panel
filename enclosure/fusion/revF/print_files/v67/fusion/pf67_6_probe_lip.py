# pf67_6_probe_lip (block 2 follow-up). READ-ONLY on the design (connector readOnly: true). Writes only under print_files_v67/_work/.
#   Names the face of the shell that the PLA slice flags (the strip 0.4 above the bed at world x -90..90, y 6.4, z 50.7..53, which
#   starts in mid-air in the chin-down print): the shell's faces whose centroid lies near world (x, 6.0..6.8, 50.5..53.5), with
#   their normal (world), area and world bounds, and the least distance from each to the screen plate (HOUSING_F_plate) and to the
#   slab (SLAB_frame). No geometry is created.


def run(_context):
    t0 = time.time(); X = R2Ctx(); r2_guard(X, strict=True)
    sh = X.body('HOUSING_F_front'); plate = X.body('HOUSING_F_plate'); slab = X.body('SLAB_frame')
    out = []
    for f in sh.faces:
        bb = f.boundingBox
        c = [(bb.minPoint.x + bb.maxPoint.x) / 2, (bb.minPoint.y + bb.maxPoint.y) / 2, (bb.minPoint.z + bb.maxPoint.z) / 2]
        a, b = bb.minPoint, bb.maxPoint
        cs = [r2_wpt(adsk.core.Point3D.create(x, y, z)) for x in (a.x, b.x) for y in (a.y, b.y) for z in (a.z, b.z)]
        wlo = [min(q[k] for q in cs) for k in range(3)]; whi = [max(q[k] for q in cs) for k in range(3)]
        if not (whi[0] - wlo[0] > 60 and whi[1] >= 5.5 and wlo[1] <= 7.0 and whi[2] >= 50.0 and wlo[2] <= 54.0 and whi[2] - wlo[2] < 12):
            continue
        ok, nrm = f.evaluator.getNormalAtPoint(f.pointOnFace)
        n = r2_wvec(nrm) if ok else None
        d_plate = X.mm.measureMinimumDistance(f, plate).value * 10.0
        d_slab = X.mm.measureMinimumDistance(f, slab).value * 10.0
        p = r2_wpt(f.pointOnFace)
        out.append({'area_mm2': round(f.area * 100, 2), 'normal_world': [round(v, 3) for v in n] if n else None,
                    'point_world': [round(v, 2) for v in p], 'world_lo': [round(v, 2) for v in wlo], 'world_hi': [round(v, 2) for v in whi],
                    'to_plate_mm': round(d_plate, 3), 'to_slab_mm': round(d_slab, 3), 'type': f.geometry.objectType.split('::')[-1]})
        if time.time() - t0 > 40:
            break
    out.sort(key=lambda r: -r['area_mm2'])
    r2_out(os.path.join(R2_DIR, 'data', 'pf67_6_probe_lip.json'), out)
    print(json.dumps({'n': len(out), 'faces': out[:12], 's': round(time.time() - t0, 1)}, separators=(',', ':')))


def r2_wvec(v):
    w = (v.x, v.y * R2_C - v.z * R2_S, v.y * R2_S + v.z * R2_C); L = math.sqrt(sum(c * c for c in w)) or 1.0
    return tuple(c / L for c in w)
