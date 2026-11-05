# rev F cap block c1f (2026-11-05), read-only: section outlines for the step-1 checkpoint pictures (plotted off-line).
#   Planes: S1 x_rel 0 (back, through the groove and both exhaust rows), S2 x_rel 28 (BL post: cone, rib, web, insert,
#   countersink), S3 x_rel 58.4 (FL post after c1d2, rib to the front bar; x 60 before), S4 y −30 (side wall, +x half).
#   Bodies: HOUSING_F_front, HOUSING_F_cap, HOUSING_F_door, SLAB_frame, REF_F_outer, TOOL_outer_skin_0p7 (cloth layer).
#   Output per plane and body: closed loops in plane coordinates (S1–S3: (y, z), S4: (x_rel, z)), clipped to the window,
#   simplified (RDP 0.01 mm), to the log only.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
ONLY = None                     # run 1 stopped at S4 (planeIntersection InternalValidationError: the door / slab miss the
#   plane – now caught per body); run 2 ONLY = ('S4_y-30',); run 3 (after c1e3's groove re-cut) all planes;
#   run 4 after the rebuild c1d2 + c1e4 (S3 moved to the new FL axis)
BODIES = ['HOUSING_F_front', 'HOUSING_F_cap', 'HOUSING_F_door', 'SLAB_frame', 'REF_F_outer', 'TOOL_outer_skin_0p7']
PLANES = {'S1_x0': ('x', 0.0, (-60.0, -14.0, 152.0, 183.0)), 'S2_x28': ('x', 28.0, (-58.0, -18.0, 152.0, 183.0)),
          'S3_x58.4': ('x', 58.4, (-40.0, -10.0, 156.0, 183.0)), 'S4_y-30': ('y', -30.05, (40.0, 80.0, 160.0, 183.0))}


def clip(P, W):
    S0, S1, Z0, Z1 = W

    def cut(P, inside, inter):
        o = []
        for i in range(len(P)):
            a = P[i - 1]; b = P[i]; ia, ib = inside(a), inside(b)
            if ib:
                if not ia: o.append(inter(a, b))
                o.append(b)
            elif ia:
                o.append(inter(a, b))
        return o
    ix = lambda v: (lambda a, b: (v, a[1] + (b[1] - a[1]) * (v - a[0]) / ((b[0] - a[0]) or 1e-12)))
    iz = lambda v: (lambda a, b: (a[0] + (b[0] - a[0]) * (v - a[1]) / ((b[1] - a[1]) or 1e-12), v))
    for f in [(lambda p: p[0] >= S0, ix(S0)), (lambda p: p[0] <= S1, ix(S1)), (lambda p: p[1] >= Z0, iz(Z0)), (lambda p: p[1] <= Z1, iz(Z1))]:
        if not P: break
        P = cut(P, f[0], f[1])
    return P


def rdp(P, eps):
    if len(P) < 3: return P
    a, b = P[0], P[-1]; dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1e-12
    dmax, idx = 0, 0
    for i in range(1, len(P) - 1):
        d = abs(dy * (P[i][0] - a[0]) - dx * (P[i][1] - a[1])) / L
        if d > dmax: dmax, idx = d, i
    if dmax > eps:
        return rdp(P[:idx + 1], eps)[:-1] + rdp(P[idx:], eps)
    return [a, b]


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        for pk, (kind, val, W) in PLANES.items():
            if ONLY and pk not in ONLY:
                continue
            if kind == 'x':
                pl = adsk.core.Plane.create(P3((XC + val) / 10, 0, 0), V3(1, 0, 0))
                uv = lambda p: (wy(p), wz(p))
            else:
                pl = adsk.core.Plane.create(Dw(0.0, val, H), WY)
                uv = lambda p: (p.x * 10 - XC, wz(p))
            res = {}
            for n in BODIES:
                b = X.body(n)
                if b is None:
                    continue
                try:
                    wb = X.tbm.planeIntersection(b, pl)
                except Exception as e:
                    res[n + '_FAIL'] = str(e)[:60]; continue
                if wb is None:
                    continue
                segs = []
                for e in wb.edges:
                    ev = e.evaluator; ok, t0e, t1e = ev.getParameterExtents(); ok, pts = ev.getStrokes(t0e, t1e, 0.0005)
                    segs.append([uv(p) for p in pts])
                loops = []
                while segs:
                    cur = segs.pop(0); grown = True
                    while grown:
                        grown = False
                        for i, s in enumerate(segs):
                            if math.dist(s[0], cur[-1]) < 0.005: cur += s[1:]; segs.pop(i); grown = True; break
                            if math.dist(s[-1], cur[-1]) < 0.005: cur += s[::-1][1:]; segs.pop(i); grown = True; break
                    loops.append(cur)
                keep = []
                for L in loops:
                    Cc = clip(L, W)
                    if len(Cc) < 3: continue
                    k = max(range(len(Cc)), key=lambda i: math.dist(Cc[0], Cc[i]))
                    Cc = rdp(Cc[:k + 1], 0.01)[:-1] + rdp(Cc[k:] + [Cc[0]], 0.01)
                    keep.append([[round(a, 3), round(c, 3)] for (a, c) in Cc])
                res[n] = keep
            out[pk] = {'kind': kind, 'val': val, 'win': W, 'loops': res}
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_c1f_sections', 'sections' if not ONLY else 'sections_' + '_'.join(ONLY), out)
    print(json.dumps({'t_s': out.get('t_s'), 'FAIL': out.get('FAIL'),
                      'n': {k: {n: (len(v) if isinstance(v, list) else v) for n, v in out[k]['loops'].items()} for k in PLANES if k in out}}))
