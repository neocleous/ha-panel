# rev F block 6o (2026-11-05), read-only: print-orientation numbers per printed part (brief block 6.3).
#   Each part is meshed (normal quality); for each candidate build direction U (world axes and the slab normal) the script
#   sums the area of the triangles that face down more than 45° from vertical (n·U < −0.707, i.e. need support) – the
#   triangles lying on the bed (all three nodes within 0.3 of the lowest point) excluded – and reports the bed contact
#   area, the build height and whether the part fits a 256 × 256 × 256 bed (axis-aligned bbox in that orientation).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
PARTS = ['HOUSING_F_front', 'HOUSING_F_door', 'SLAB_frame', 'SPKBOX_L', 'SPKBOX_R', 'MAIN_BRACKET', 'RESP_CARRIER', 'CRADLE_5807',
         'GROMMET_usbc_F']
DIRS = {'+z': (0.0, 0.0, 1.0), '-z': (0.0, 0.0, -1.0), '+y': (0.0, 1.0, 0.0), '-y': (0.0, -1.0, 0.0), '+x': (1.0, 0.0, 0.0),
        '-x': (-1.0, 0.0, 0.0), 'slab_back_down': (0.0, C, S), 'slab_front_down': (0.0, -C, -S)}


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        res = {}
        for name in PARTS:
            b = X.body(name)
            if b is None:
                res[name] = 'missing'; continue
            mc = b.meshManager.createMeshCalculator()
            mc.setQuality(adsk.fusion.TriangleMeshQualityOptions.NormalQualityTriangleMesh)
            m = mc.calculate()
            c = m.nodeCoordinatesAsDouble; ix = m.nodeIndices; nv = m.normalVectorsAsDouble
            P = []
            for i in range(0, len(c), 3):
                x, yd, zd = c[i] * 10, c[i + 1] * 10, c[i + 2] * 10
                P.append((x - XC, yd * C - zd * S, H + yd * S + zd * C))
            N = []
            for i in range(0, len(nv), 3):
                N.append((nv[i], nv[i + 1] * C - nv[i + 2] * S, nv[i + 1] * S + nv[i + 2] * C))
            tris = []
            for t in range(0, len(ix), 3):
                a, bb, cc = ix[t], ix[t + 1], ix[t + 2]
                pa, pb, pc = P[a], P[bb], P[cc]
                u = (pb[0] - pa[0], pb[1] - pa[1], pb[2] - pa[2]); v = (pc[0] - pa[0], pc[1] - pa[1], pc[2] - pa[2])
                cr = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
                ar = math.sqrt(cr[0] ** 2 + cr[1] ** 2 + cr[2] ** 2) / 2
                if ar <= 0:
                    continue
                n = (cr[0] / (2 * ar), cr[1] / (2 * ar), cr[2] / (2 * ar))
                na = (N[a][0] + N[bb][0] + N[cc][0], N[a][1] + N[bb][1] + N[cc][1], N[a][2] + N[bb][2] + N[cc][2])
                if n[0] * na[0] + n[1] * na[1] + n[2] * na[2] < 0:
                    n = (-n[0], -n[1], -n[2])
                tris.append((a, bb, cc, n, ar))
            r = {'tris': len(tris)}
            for dn, U in DIRS.items():
                h = [p[0] * U[0] + p[1] * U[1] + p[2] * U[2] for p in P]
                h0 = min(h); H_ = max(h) - h0
                ov = 0.0; bed = 0.0
                for (a, bb, cc, n, ar) in tris:
                    d = n[0] * U[0] + n[1] * U[1] + n[2] * U[2]
                    if d < -0.7071:
                        if h[a] - h0 < 0.3 and h[bb] - h0 < 0.3 and h[cc] - h0 < 0.3:
                            bed += ar
                        else:
                            ov += ar
                # bbox size in the plane ⟂ U: two orthonormal axes
                e1 = (1.0, 0.0, 0.0) if abs(U[0]) < 0.9 else (0.0, 1.0, 0.0)
                k = e1[0] * U[0] + e1[1] * U[1] + e1[2] * U[2]
                e1 = (e1[0] - k * U[0], e1[1] - k * U[1], e1[2] - k * U[2]); l = math.sqrt(sum(q * q for q in e1)); e1 = tuple(q / l for q in e1)
                e2 = (U[1] * e1[2] - U[2] * e1[1], U[2] * e1[0] - U[0] * e1[2], U[0] * e1[1] - U[1] * e1[0])
                s1 = [p[0] * e1[0] + p[1] * e1[1] + p[2] * e1[2] for p in P]; s2 = [p[0] * e2[0] + p[1] * e2[1] + p[2] * e2[2] for p in P]
                w1, w2 = max(s1) - min(s1), max(s2) - min(s2)
                r[dn] = {'overhang_mm2': round(ov), 'bed_mm2': round(bed), 'height': round(H_, 1), 'footprint': [round(w1, 1), round(w2, 1)],
                         'fits_256': H_ <= 256 and max(w1, w2) <= 256}
            res[name] = r
        out['parts'] = res
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b6o_print_orient', 'overhangs', out)
    print(json.dumps({'t_s': out.get('t_s'), 'FAIL': out.get('FAIL')}))
