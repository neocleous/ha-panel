# rev F audit-response round d (2026-11-06), read-only: section loops round the parts the audit fixes touch, plotted
#   off-line. Writes ~/Documents/HA_panel_renders/d0_sections.json. Planes: ('x', x_rel, (y0, y1, z0, z1)),
#   ('z', z_w, (x_rel0, x_rel1, y0, y1)), ('y', y_w, (x_rel0, x_rel1, z0, z1)); loops per body in plane coordinates.
#   Set PLANES / OUT below (the same script serves every d-step's pictures).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
OUT = os.path.expanduser('~/Documents/HA_panel_renders/d4_inlet_sections.json')
B = ['HOUSING_F_door', 'GROMMET_usbc_F', 'CRADLE_5807', 'PD_5807_env', 'HOUSING_F_front', 'PIPWR_a_env', 'LEAD_PI_POWER']
PLANES = {
    'I_x0': ('x', 0.0, (-90.0, -64.0, 0.0, 34.0), B),
    'I_x13.6': ('x', 13.6, (-90.0, -64.0, 0.0, 34.0), B),
    'I_z20.6': ('z', 20.6, (-20.0, 20.0, -90.0, -64.0), B),
    'I_z16': ('z', 16.0, (-14.0, 14.0, -82.0, -62.0), B),
    'I_z11': ('z', 11.0, (-14.0, 14.0, -82.0, -62.0), B),
    'I_y-84.9': ('y', -84.9, (-20.0, 20.0, 8.0, 34.0), B),
    'I_y-83': ('y', -83.0, (-20.0, 20.0, 8.0, 34.0), B),
    'D_y-77': ('y', -77.0, (-26.0, -12.0, 0.0, 12.0), ['HOUSING_F_door', 'HOUSING_F_front']),
    'D_x-19': ('x', -19.0, (-86.0, -68.0, 0.0, 12.0), ['HOUSING_F_door', 'HOUSING_F_front']),
}


def clip(P, W):
    S0, S1, Z0, Z1 = W

    def cut(P, inside, inter_):
        o = []
        for i in range(len(P)):
            a = P[i - 1]; b = P[i]; ia, ib = inside(a), inside(b)
            if ib:
                if not ia: o.append(inter_(a, b))
                o.append(b)
            elif ia:
                o.append(inter_(a, b))
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


def sections(X, planes):
    out = {}
    for pk, (kind, val, W, bodies) in planes.items():
        if kind == 'x':
            pl = adsk.core.Plane.create(P3((XC + val) / 10, 0, 0), V3(1, 0, 0)); uv = lambda p: (wy(p), wz(p))
        elif kind == 'z':
            pl = adsk.core.Plane.create(Dw(0.0, 0.0, val), UP); uv = lambda p: (p.x * 10 - XC, wy(p))
        else:
            pl = adsk.core.Plane.create(Dw(0.0, val, H), WY); uv = lambda p: (p.x * 10 - XC, wz(p))
        res = {}
        for n in bodies:
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
            if keep:
                res[n] = keep
        out[pk] = {'kind': kind, 'val': val, 'win': W, 'loops': res}
    return out


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        out = sections(X, PLANES)
        out['t_s'] = round(time.time() - t0, 1)
        json.dump(out, open(OUT, 'w'))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d4a_inlet_sections', 'sections', {'t_s': out.get('t_s'), 'FAIL': out.get('FAIL'), 'planes': list(PLANES)})
    print(json.dumps({'t_s': out.get('t_s'), 'FAIL': out.get('FAIL')}))
