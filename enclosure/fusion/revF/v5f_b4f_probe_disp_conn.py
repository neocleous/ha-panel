# rev F block 4f (2026-11-04), read-only: the Pi 5 CAM/DISP connectors in PI5_F (Raspberry Pi STEP) and their entry side.
#   1. PI5_F above the PCB top (z ≥ 9.45) in x_rel −2…22, y −59…−34: lumps with tight world boxes (copy rotated +12° about x).
#   2. For each lump ≥ 10 mm³: planar faces with their world normals and areas – an FPC slot shows as a narrow recess
#      (pairs of opposed faces 0.3–1 mm apart) opening up (+z) or sideways.
#   3. PI5_F vs PI5_F_cooler interference (the cooler envelope is from the official drawing, scaled S).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback


def run(_context):
    X = Ctx(); out = {}
    tbm = X.tbm; B = adsk.fusion.BooleanTypes
    M = adsk.core.Matrix3D.create()
    M.setCell(1, 1, C); M.setCell(1, 2, -S); M.setCell(2, 1, S); M.setCell(2, 2, C); M.setCell(2, 3, H / 10)
    try:
        t = tbm.copy(X.body('PI5_F'))
        tbm.booleanOperation(t, X.wbox(XC - 2.0, XC + 22.0, -59.0, -34.0, 9.45, 30.0), B.IntersectionBooleanType)
        tbm.transform(t, M)
        lumps = []
        for i, lp in enumerate(t.lumps):
            bb = lp.boundingBox
            box = [round(bb.minPoint.x * 10 - XC, 2), round(bb.maxPoint.x * 10 - XC, 2), round(bb.minPoint.y * 10, 2),
                   round(bb.maxPoint.y * 10, 2), round(bb.minPoint.z * 10, 2), round(bb.maxPoint.z * 10, 2)]
            vol = round(lp.volume * 1000, 2)
            ent = {'i': i, 'box': box, 'mm3': vol}
            if vol >= 10:
                fs = []
                for sh in lp.shells:
                    for f in sh.faces:
                        if f.geometry.objectType.endswith('Plane'):
                            ok, n = f.evaluator.getNormalAtPoint(f.pointOnFace)
                            p = f.pointOnFace
                            fs.append([round(n.x, 2), round(n.y, 2), round(n.z, 2), round(f.area * 100, 2),
                                       round(p.x * 10 - XC, 2), round(p.y * 10, 2), round(p.z * 10, 2)])
                fs.sort(key=lambda r: -r[3])
                ent['planar_faces_top20'] = fs[:20]
            lumps.append(ent)
        out['lumps'] = sorted(lumps, key=lambda e: e['box'])
        r = X.interference(X.body('PI5_F'), [X.body('PI5_F_cooler')])
        out['pi_vs_cooler_mm3'] = r
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b4f_probe_disp_conn', 'probe', out)
    print(json.dumps({'n_lumps': len(out.get('lumps', [])), 'pi_vs_cooler': out.get('pi_vs_cooler_mm3'), 'FAIL': out.get('FAIL')}))
