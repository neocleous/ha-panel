# HA panel model audit (2026-11-05) block 1a: B-rep validity per printed part (G.1) and sharp concave edges (G.4 data).
#   Read-only. Per part: lumps, shells (closed / void, volume), faces < 0.01 mm², edges < 0.05 mm (world points), and every
#   sharp concave edge: face normals at the edge midpoint more than 20° apart, concave when the point
#   p + 0.02 mm · (n1 − n2)/|n1 − n2| lies inside the body (valid for any dihedral and either normal sense). World mm.
#   SEL (set by the loader) picks the parts; default all ten. Time-boxed: stops before a part when 45 s have passed.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
exec(open(os.path.expanduser('~/Documents/audit/scripts/v5f_audit_common.py')).read())
COS20 = math.cos(math.radians(20.0))


def edge_mid(e):
    ev = e.evaluator; ok, t0, t1 = ev.getParameterExtents(); ok, p = ev.getPointAtParameter((t0 + t1) / 2); return p


def run(_context):
    X = Ctx(); guard(X); out = {}; t0 = time.time()
    parts = globals().get('SEL') or PRINTED
    try:
        for name in parts:
            if time.time() - t0 > 45:
                out['stopped_before'] = name; break
            b = X.body(name); r = {'faces': b.faces.count, 'edges': b.edges.count, 'lumps': b.lumps.count}
            sh = []
            for li in range(b.lumps.count):
                L = b.lumps.item(li)
                for si in range(L.shells.count):
                    s = L.shells.item(si)
                    sh.append([li, si, s.isClosed, s.isVoid, round(s.volume * 1000, 3), round(s.area * 100, 2),
                               [round(v, 1) for v in wpt(s.boundingBox.minPoint)], [round(v, 1) for v in wpt(s.boundingBox.maxPoint)]])
            r['shells'] = sh
            r['small_faces'] = [[round(f.area * 100, 5), [round(v, 2) for v in wpt(f.pointOnFace)]] for f in b.faces if f.area < 1e-4]
            r['small_edges'] = [[round(e.length * 10, 4), [round(v, 2) for v in wpt(edge_mid(e))]] for e in b.edges if e.length < 5e-3]
            conc = []; on = 0; sharp = 0
            for e in b.edges:
                if e.faces.count != 2:
                    continue
                p = edge_mid(e)
                ok1, n1 = e.faces.item(0).evaluator.getNormalAtPoint(p); ok2, n2 = e.faces.item(1).evaluator.getNormalAtPoint(p)
                if not (ok1 and ok2):
                    continue
                c = n1.dotProduct(n2)
                if c > COS20:
                    continue
                sharp += 1
                d = V3(n1.x - n2.x, n1.y - n2.y, n1.z - n2.z); L_ = d.length
                if L_ < 1e-9:
                    continue
                q = P3(p.x + 0.002 * d.x / L_, p.y + 0.002 * d.y / L_, p.z + 0.002 * d.z / L_)
                pc = b.pointContainment(q)
                if pc == adsk.fusion.PointContainment.PointOnPointContainment:
                    on += 1
                elif pc == adsk.fusion.PointContainment.PointInsidePointContainment:
                    conc.append([round(e.length * 10, 2), round(math.degrees(math.acos(max(-1.0, min(1.0, c)))), 1),
                                 [round(v, 2) for v in wpt(p)]])
            r['sharp'] = sharp; r['concave'] = len(conc); r['concave_on'] = on; r['concave_edges'] = conc
            r['t'] = round(time.time() - t0, 1)
            out[name] = r
            log('v5f_a1a_validity', name, r)
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
        log('v5f_a1a_validity', 'FAIL', out['FAIL'])
    print(json.dumps({k: ({kk: (vv if kk not in ('concave_edges',) else len(vv)) for kk, vv in v.items()} if isinstance(v, dict) else v)
                      for k, v in out.items()}))
