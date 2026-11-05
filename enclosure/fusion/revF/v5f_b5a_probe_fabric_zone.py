# rev F block 5a (2026-11-05), read-only: geometry for the fabric zone (D1/D2).
#   1. REF_F_outer's 20 faces: type, area, world box (copy rotated to world), normal at pointOnFace (world).
#   2. HOUSING_F_door / HOUSING_F_front planar faces that form the front/door joint (normal ±y near y −55, normal ±z near
#      z 2.5…2.8, the door's top edge) with world boxes.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback


def run(_context):
    X = Ctx(); out = {}
    tbm = X.tbm
    M = adsk.core.Matrix3D.create()
    M.setCell(1, 1, C); M.setCell(1, 2, -S); M.setCell(2, 1, S); M.setCell(2, 2, C); M.setCell(2, 3, H / 10)

    def wb(bb):
        return [round(bb.minPoint.x * 10 - XC, 1), round(bb.maxPoint.x * 10 - XC, 1), round(bb.minPoint.y * 10, 1),
                round(bb.maxPoint.y * 10, 1), round(bb.minPoint.z * 10, 1), round(bb.maxPoint.z * 10, 1)]
    try:
        t = tbm.copy(X.body('REF_F_outer')); tbm.transform(t, M)
        fl = []
        for f in t.faces:
            p = f.pointOnFace; ok, n = f.evaluator.getNormalAtPoint(p)
            fl.append([f.geometry.objectType.split('::')[-1], round(f.area * 100, 0), wb(f.boundingBox), [round(n.x, 2), round(n.y, 2), round(n.z, 2)]])
        out['ref_faces'] = sorted(fl, key=lambda r: r[2][4])
        for bn in ('HOUSING_F_door', 'HOUSING_F_front'):
            t = tbm.copy(X.body(bn)); tbm.transform(t, M)
            jl = []
            for f in t.faces:
                if not f.geometry.objectType.endswith('Plane'):
                    continue
                p = f.pointOnFace; ok, n = f.evaluator.getNormalAtPoint(p)
                bb = f.boundingBox
                yc = (bb.minPoint.y + bb.maxPoint.y) * 5; zc = (bb.minPoint.z + bb.maxPoint.z) * 5
                if (abs(n.y) > 0.99 and -56.5 < yc < -53.0) or (abs(n.z) > 0.99 and 2.3 < zc < 3.2 and bb.minPoint.y * 10 < -50) or \
                        (bn == 'HOUSING_F_door' and bb.maxPoint.z * 10 > 150):
                    jl.append([round(f.area * 100, 1), wb(bb), [round(n.x, 2), round(n.y, 2), round(n.z, 2)]])
            out['joint_faces_' + bn] = sorted(jl, key=lambda r: -r[0])[:24]
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b5a_probe_fabric_zone', 'probe', out)
    lines = []
    for r in out.get('ref_faces', []):
        lines.append('REF %s A%s box%s n%s' % tuple(r))
    for bn in ('HOUSING_F_door', 'HOUSING_F_front'):
        for r in out.get('joint_faces_' + bn, []):
            lines.append('%s A%s box%s n%s' % (bn[-5:], r[0], r[1], r[2]))
    print('\n'.join(lines) + ('\nFAIL %s' % out['FAIL'] if 'FAIL' in out else ''))
