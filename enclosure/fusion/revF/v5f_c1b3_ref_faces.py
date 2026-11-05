# rev F cap block c1b3 (2026-11-05): REF_F_outer ∩ z 160…177.2 face list (why c1b2's shell with the front plane removed failed),
#   plus the leftover un-shelled TOOL_cap_off0p72 from c1b2 renamed TOOL_cap_off0p72_fail (hidden).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        b = X.body('TOOL_cap_off0p72')
        if b is not None and b.faces.count < 40 and abs(b.volume - X.body('TOOL_cap_off0p72_v1').volume) > 1.0:
            b.name = 'TOOL_cap_off0p72_fail'; b.isLightBulbOn = False; out['renamed'] = [b.name, round(b.volume, 3)]
        tb = tb_copy(X, 'REF_F_outer')
        inter(X, tb, X.wbox(-250, 250, -250, 250, 160.0, 177.2))
        rows = []
        for f in tb.faces:
            g = f.geometry; bb = f.boundingBox
            pts = [bb.minPoint, bb.maxPoint]
            p = f.pointOnFace; ok, n = f.evaluator.getNormalAtPoint(p)
            r = [g.objectType.split('::')[-1], round(f.area * 100, 1), round(p.x * 10 - XC, 1), round(wy(p), 2), round(wz(p), 2),
                 [round(n.x, 3), round(n.y, 3), round(n.z, 3)], f.edges.count]
            if hasattr(g, 'radius'):
                r.append(('R', round(g.radius * 10, 2)))
            if hasattr(g, 'majorRadius'):
                r.append(('Rmaj/min', round(g.majorRadius * 10, 2), round(g.minorRadius * 10, 2)))
            rows.append(r)
        out['faces_[type, mm2, xr, y, z, n_design, edges]'] = rows
        # front-plane face corner points
        fr = []
        for f in tb.faces:
            if f.geometry.objectType.endswith('Plane'):
                ok, n = f.evaluator.getNormalAtPoint(f.pointOnFace)
                if abs(n.y) > 0.99:
                    for v in f.vertices:
                        fr.append([round(v.geometry.x * 10 - XC, 2), round(wy(v.geometry), 2), round(wz(v.geometry), 2)])
        out['front_plane_vertices'] = fr
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_c1b3_ref_faces', 'faces', out)
    print(json.dumps(out, separators=(',', ':'))[:8000])
