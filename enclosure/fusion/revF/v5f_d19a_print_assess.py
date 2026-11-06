# rev F d19a (2026-11-06), read-only: printability of the 14 prints (Daniel 21:49). B6o's method (mesh, triangles facing down more
#   than 45° from the build direction need support, the bed's own triangles excluded) for 8 build directions, plus: flat ceilings
#   (facing down within 11° of vertical: bridges), and for the best direction and the as-installed one the overhang triangles
#   joined into connected regions (shared mesh nodes) with area, world bbox and mean angle – to name the features that need
#   support. The two bracket halves are split by x. Writes ~/Documents/HA_panel_renders/d_data/data/d19a_print.json.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py'), encoding='utf-8').read())
import traceback
OUTF = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d19a_print.json')
PRINTS = [('Front shell', 'HOUSING_F_front', None), ('Top cap', 'HOUSING_F_cap', None), ('Slab frame', 'SLAB_frame', None),
          ('ReSpeaker carrier', 'RESP_CARRIER', None), ('Rear door', 'HOUSING_F_door', None), ('USB-C grommet', 'GROMMET_usbc_F', None),
          ('5807 cradle', 'CRADLE_5807', None), ('Bracket L', 'MAIN_BRACKET', 1), ('Bracket R', 'MAIN_BRACKET', -1),
          ('BME680 hood', 'BME_HOOD', None), ('Speaker box L', 'SPKBOX_L', None), ('Speaker box R', 'SPKBOX_R', None),
          ('Touch clip L', 'TOUCH_CLIP_L', None), ('Touch clip R', 'TOUCH_CLIP_R', None)]
DIRS = {'+z': (0.0, 0.0, 1.0), '-z': (0.0, 0.0, -1.0), '+y': (0.0, 1.0, 0.0), '-y': (0.0, -1.0, 0.0), '+x': (1.0, 0.0, 0.0),
        '-x': (-1.0, 0.0, 0.0), 'slab_back_down': (0.0, C, S), 'slab_front_down': (0.0, -C, -S)}
QUAL = adsk.fusion.TriangleMeshQualityOptions.NormalQualityTriangleMesh


def mesh(b):
    mc = b.meshManager.createMeshCalculator(); mc.setQuality(QUAL); m = mc.calculate()
    c = m.nodeCoordinatesAsDouble; ix = m.nodeIndices; nv = m.normalVectorsAsDouble
    P = [(c[i] * 10 - XC, c[i + 1] * 10 * C - c[i + 2] * 10 * S, H + c[i + 1] * 10 * S + c[i + 2] * 10 * C) for i in range(0, len(c), 3)]
    N = [(nv[i], nv[i + 1] * C - nv[i + 2] * S, nv[i + 1] * S + nv[i + 2] * C) for i in range(0, len(nv), 3)]
    T = []
    for t in range(0, len(ix), 3):
        a, b_, c_ = ix[t], ix[t + 1], ix[t + 2]
        pa, pb, pc = P[a], P[b_], P[c_]
        u = (pb[0] - pa[0], pb[1] - pa[1], pb[2] - pa[2]); v = (pc[0] - pa[0], pc[1] - pa[1], pc[2] - pa[2])
        cr = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
        ar = math.sqrt(cr[0] ** 2 + cr[1] ** 2 + cr[2] ** 2) / 2
        if ar <= 0:
            continue
        n = (cr[0] / (2 * ar), cr[1] / (2 * ar), cr[2] / (2 * ar))
        na = (N[a][0] + N[b_][0] + N[c_][0], N[a][1] + N[b_][1] + N[c_][1], N[a][2] + N[b_][2] + N[c_][2])
        if n[0] * na[0] + n[1] * na[1] + n[2] * na[2] < 0:
            n = (-n[0], -n[1], -n[2])
        cx = ((pa[0] + pb[0] + pc[0]) / 3, (pa[1] + pb[1] + pc[1]) / 3, (pa[2] + pb[2] + pc[2]) / 3)
        T.append((a, b_, c_, n, ar, cx))
    return P, T


def stats(P, T, U, regions=False):
    h = {}
    hp = lambda i: P[i][0] * U[0] + P[i][1] * U[1] + P[i][2] * U[2]
    nodes = set(i for t in T for i in t[:3])
    hv = {i: hp(i) for i in nodes}; h0 = min(hv.values()); H_ = max(hv.values()) - h0
    ov = []; bed = 0.0; flat = 0.0
    for t in T:
        d = t[3][0] * U[0] + t[3][1] * U[1] + t[3][2] * U[2]
        if d < -0.7071:
            if hv[t[0]] - h0 < 0.3 and hv[t[1]] - h0 < 0.3 and hv[t[2]] - h0 < 0.3:
                bed += t[4]
            else:
                ov.append((t, d))
                if d < -0.98:
                    flat += t[4]
    r = {'overhang_mm2': round(sum(t[4] for t, d in ov)), 'flat_ceiling_mm2': round(flat), 'bed_mm2': round(bed), 'height': round(H_, 1)}
    if regions:
        par = {}

        def f(x):
            while par.setdefault(x, x) != x:
                par[x] = par[par[x]]; x = par[x]
            return x
        for t, d in ov:
            a, b_, c_ = t[0], t[1], t[2]
            ra, rb, rc = f(a), f(b_), f(c_)
            par[rb] = ra; par[f(c_)] = ra
        reg = {}
        for t, d in ov:
            k = f(t[0]); e = reg.setdefault(k, [0.0, [1e9, -1e9, 1e9, -1e9, 1e9, -1e9], 0.0, 1e9])
            e[0] += t[4]; e[2] += -d * t[4]
            for p in (P[t[0]], P[t[1]], P[t[2]]):
                for j in range(3):
                    e[1][2 * j] = min(e[1][2 * j], p[j]); e[1][2 * j + 1] = max(e[1][2 * j + 1], p[j])
            e[3] = min(e[3], min(hv[t[0]], hv[t[1]], hv[t[2]]) - h0)
        lst = sorted(reg.values(), key=lambda e: -e[0])
        r['n_regions'] = len(lst)
        r['regions'] = [[round(e[0], 1), [round(v, 1) for v in e[1]], round(math.degrees(math.acos(min(1.0, e[2] / e[0]))), 0),
                         round(e[3], 1)] for e in lst[:10]]
    return r


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        cache = {}
        for (lab, n, side) in PRINTS:
            if n not in cache:
                cache[n] = mesh(X.body(n))
            P, T = cache[n]
            if side is not None:
                T = [t for t in T if t[5][0] * side > 0]
            res = {'tris': len(T)}
            best = None
            for dn, U in DIRS.items():
                s = stats(P, T, U)
                res[dn] = s
                if best is None or s['overhang_mm2'] < res[best]['overhang_mm2']:
                    best = dn
            res['best'] = best
            res['regions_best'] = stats(P, T, DIRS[best], True)
            if best != '+z':
                res['regions_+z'] = stats(P, T, DIRS['+z'], True)
            out[lab] = res
        out['t_s'] = round(time.time() - t0, 1)
        os.makedirs(os.path.dirname(OUTF), exist_ok=True)
        json.dump(out, open(OUTF, 'w'))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
        try:
            json.dump(out, open(OUTF, 'w'))
        except Exception:
            pass
    log('v5f_d19a_print_assess', 'run', {'t_s': out.get('t_s'), 'FAIL': out.get('FAIL')})
    print(json.dumps({'t_s': out.get('t_s'), 'FAIL': out.get('FAIL')}, separators=(',', ':')))
